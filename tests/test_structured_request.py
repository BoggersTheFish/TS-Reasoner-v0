import unittest

from ts_reasoner.structured_request import (
    Ambiguity, ReasoningRequest, StructuredClaim, StructuredConstraint,
    StructuredRelation, verify_reasoning_request,
)


class StructuredRequestTests(unittest.TestCase):
    def request(self, *, intent, relations=(), claims=(), constraints=(), ambiguities=(), repairs=()):
        return ReasoningRequest("r", "input", intent, relations=relations, claims=claims, constraints=constraints, ambiguities=ambiguities, repair_actions=repairs)

    def test_ordering_accept(self):
        relations=(StructuredRelation("r1","alice","older_than","bob",source_ids=("n1",)), StructuredRelation("r2","bob","older_than","carol",source_ids=("n2",)), StructuredRelation("q","","oldest","",kind="query"))
        result=verify_reasoning_request(self.request(intent="ordering_query",relations=relations))
        self.assertEqual(result.decision,"ACCEPT"); self.assertEqual(result.answer.subject,"alice")

    def test_boolean_accept(self):
        claims=(StructuredClaim("c1","door","door_open"),StructuredClaim("c2","system","system_armed"),StructuredClaim("q","alarm","alarm_active",modality="query"))
        constraints=(StructuredConstraint("k","boolean_rule",("door_open","system_armed"),"alarm_active"),)
        self.assertEqual(verify_reasoning_request(self.request(intent="boolean_query",claims=claims,constraints=constraints)).decision,"ACCEPT")

    def test_unsupported_reject(self):
        relations=(StructuredRelation("q","alice","wealthy","",kind="query"),)
        result=verify_reasoning_request(self.request(intent="relational_query",relations=relations))
        self.assertEqual(result.decision,"REJECT"); self.assertTrue(result.unsupported_claims)

    def test_ambiguity_repairs(self):
        ambiguity=Ambiguity("pronoun","Her has multiple antecedents",("alice","sarah"),True,"Did Alice or Sarah own the key?")
        result=verify_reasoning_request(self.request(intent="relational_query",ambiguities=(ambiguity,)))
        self.assertEqual(result.decision,"REPAIR"); self.assertEqual(result.repair_result,"REPAIR_NEEDS_USER")

    def test_plan_accept(self):
        constraints=(StructuredConstraint("k","before",("verify_backup","delete_repository")),)
        result=verify_reasoning_request(self.request(intent="planning_query",constraints=constraints))
        self.assertEqual(result.answer.subject,"verify_backup")

    def test_repair_accepted(self):
        relations=(StructuredRelation("r","red_key","opens","north_door",source_ids=("n",)),StructuredRelation("q","red_key","opens","",kind="query"))
        result=verify_reasoning_request(self.request(intent="relational_query",relations=relations,repairs=("normalise_alias:key",)))
        self.assertEqual(result.decision,"REPAIR"); self.assertEqual(result.repair_result,"REPAIR_ACCEPTED")

    def test_contradiction_reject(self):
        relations=(StructuredRelation("r1","alice","older_than","bob"),StructuredRelation("r2","bob","older_than","alice"),StructuredRelation("q","","oldest","",kind="query"))
        self.assertEqual(verify_reasoning_request(self.request(intent="ordering_query",relations=relations)).reason,"contradiction")

    def test_deterministic_request_hash(self):
        request=self.request(intent="assert",relations=(StructuredRelation("r","a","p","b",source_ids=("n",)),))
        self.assertEqual(request.canonical_hash,request.canonical_hash)


if __name__ == "__main__": unittest.main()
