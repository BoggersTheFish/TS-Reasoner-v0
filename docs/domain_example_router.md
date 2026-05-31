# TS-AGL Domain Example Router

v7.3 makes domain-pack language examples active.

Before v7.3, domain manifests described operations and examples, but routing was still mostly hardcoded. v7.3 adds a transparent teaching-example router:

```text
domain pack examples
  -> ranked operation candidates
  -> LanguageMove
  -> TSCall
Boundary

The example router is not a broad language model. It is a dependency-free, inspectable bridge from domain teaching packs into operation routing.

It uses:

token overlap
simple sequence similarity
a confidence threshold
safe abstention to route_unknown
Evaluation

Run:

python3 scripts/evaluate_ts_agl_example_router.py

The report is written to:

artifacts/ts_agl_example_router_report.json
Core claim

Domain packs now teach routing behavior directly.

Build the substrate once. Teach it domains through examples.

