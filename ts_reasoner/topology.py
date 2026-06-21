"""Deterministic signed spatial topology for Habitat v3."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from collections import deque
from typing import Any, Iterable

from .typed_support import canonical_hash


class ConnectionStatus(str, Enum):
    OPEN = "OPEN"
    BLOCKED = "BLOCKED"
    LOCKED = "LOCKED"
    UNKNOWN = "UNKNOWN"
    CONFLICTED = "CONFLICTED"


@dataclass(frozen=True)
class ConnectionEvidence:
    evidence_id: str
    status: ConnectionStatus
    source_ids: tuple[str, ...] = ()
    provenance_ids: tuple[str, ...] = ()
    active: bool = True


@dataclass(frozen=True)
class Connection:
    connection_id: str
    source_location_id: str
    destination_location_id: str
    direction: str = "bidirectional"
    status: ConnectionStatus = ConnectionStatus.OPEN
    required_conditions: tuple[str, ...] = ()
    blocked_by: tuple[str, ...] = ()
    cost: int = 1
    source_ids: tuple[str, ...] = ()
    provenance_ids: tuple[str, ...] = ()
    evidence: tuple[ConnectionEvidence, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["status"] = self.status.value
        value["evidence"] = [
            {**asdict(item), "status": item.status.value} for item in self.evidence
        ]
        return value


def connection_id(source: str, destination: str, direction: str = "bidirectional", name: str = "") -> str:
    if direction == "bidirectional":
        source, destination = sorted((source, destination))
    suffix = f":{name}" if name else ""
    return f"connection:{source}:{destination}{suffix}"


def _resolved_status(evidence: Iterable[ConnectionEvidence]) -> ConnectionStatus:
    statuses = {item.status for item in evidence if item.active}
    if not statuses:
        return ConnectionStatus.UNKNOWN
    if len(statuses) > 1:
        return ConnectionStatus.CONFLICTED
    return next(iter(statuses))


class SpatialTopology:
    """Stable merge and cycle-safe routing over explicitly declared edges only."""

    def __init__(self, *, max_connections: int = 1024) -> None:
        self.max_connections = max_connections
        self.connections: dict[str, Connection] = {}

    def clone(self) -> "SpatialTopology":
        other = SpatialTopology(max_connections=self.max_connections)
        other.connections = dict(self.connections)
        return other

    @property
    def hash(self) -> str:
        return canonical_hash(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {key: value.to_dict() for key, value in sorted(self.connections.items())}

    def merge(self, incoming: Connection) -> Connection:
        if incoming.cost < 1:
            raise ValueError("connection cost must be positive")
        if incoming.direction not in {"bidirectional", "directed"}:
            raise ValueError("unsupported connection direction")
        if incoming.connection_id not in self.connections and len(self.connections) >= self.max_connections:
            raise OverflowError("MAX_TOPOLOGY_SIZE")
        previous = self.connections.get(incoming.connection_id)
        evidence = list(previous.evidence if previous else ())
        candidates = incoming.evidence or (
            ConnectionEvidence(
                "connection_evidence:" + canonical_hash(incoming.to_dict())[:16],
                incoming.status,
                incoming.source_ids,
                incoming.provenance_ids,
            ),
        )
        by_id = {item.evidence_id: item for item in evidence}
        by_id.update({item.evidence_id: item for item in candidates})
        merged_evidence = tuple(by_id[key] for key in sorted(by_id))
        merged = Connection(
            incoming.connection_id,
            incoming.source_location_id,
            incoming.destination_location_id,
            incoming.direction,
            _resolved_status(merged_evidence),
            tuple(sorted(set((previous.required_conditions if previous else ()) + incoming.required_conditions))),
            tuple(sorted(set((previous.blocked_by if previous else ()) + incoming.blocked_by))),
            min(previous.cost if previous else incoming.cost, incoming.cost),
            tuple(sorted(set((previous.source_ids if previous else ()) + incoming.source_ids))),
            tuple(sorted(set((previous.provenance_ids if previous else ()) + incoming.provenance_ids))),
            merged_evidence,
        )
        self.connections[merged.connection_id] = merged
        return merged

    def set_status(
        self,
        connection_id_value: str,
        status: ConnectionStatus,
        *,
        evidence_id: str,
        source_ids: tuple[str, ...] = (),
        provenance_ids: tuple[str, ...] = (),
    ) -> Connection:
        current = self.connections[connection_id_value]
        return self.merge(Connection(
            current.connection_id,
            current.source_location_id,
            current.destination_location_id,
            current.direction,
            status,
            current.required_conditions,
            current.blocked_by,
            current.cost,
            source_ids,
            provenance_ids,
            (ConnectionEvidence(evidence_id, status, source_ids, provenance_ids),),
        ))

    def locations(self) -> tuple[str, ...]:
        return tuple(sorted({x for item in self.connections.values() for x in (item.source_location_id, item.destination_location_id)}))

    def traversable(
        self,
        source: str,
        destination: str,
        *,
        supported_conditions: Iterable[str] = (),
    ) -> tuple[bool, Connection | None, str]:
        conditions = set(supported_conditions)
        for item in sorted(self.connections.values(), key=lambda value: value.connection_id):
            forward = item.source_location_id == source and item.destination_location_id == destination
            reverse = item.direction == "bidirectional" and item.destination_location_id == source and item.source_location_id == destination
            if not (forward or reverse):
                continue
            if item.status != ConnectionStatus.OPEN:
                return False, item, item.status.value
            if not set(item.required_conditions) <= conditions:
                return False, item, "MISSING_REQUIRED_CONDITION"
            if set(item.blocked_by) & conditions:
                return False, item, "BLOCKING_CONDITION"
            return True, item, "OPEN"
        return False, None, "NO_CONNECTION"

    def route(
        self,
        source: str,
        destination: str,
        *,
        supported_conditions: Iterable[str] = (),
        max_depth: int = 12,
        max_states: int = 2048,
    ) -> tuple[tuple[str, ...], tuple[str, ...], int]:
        if source == destination:
            return (source,), (), 1
        queue = deque([(source, (source,), tuple())])
        seen = {source}
        explored = 0
        while queue and explored < max_states:
            current, path, supports = queue.popleft()
            explored += 1
            if len(path) - 1 >= max_depth:
                continue
            candidates: list[tuple[str, Connection]] = []
            for edge in self.connections.values():
                if edge.source_location_id == current:
                    candidates.append((edge.destination_location_id, edge))
                if edge.direction == "bidirectional" and edge.destination_location_id == current:
                    candidates.append((edge.source_location_id, edge))
            for next_location, edge in sorted(candidates, key=lambda row: (row[0], row[1].connection_id)):
                allowed, _, _ = self.traversable(current, next_location, supported_conditions=supported_conditions)
                if not allowed or next_location in seen:
                    continue
                next_path = (*path, next_location)
                next_support = (*supports, edge.connection_id, *edge.source_ids)
                if next_location == destination:
                    return next_path, tuple(sorted(set(next_support))), explored
                seen.add(next_location)
                queue.append((next_location, next_path, next_support))
        return (), (), explored
