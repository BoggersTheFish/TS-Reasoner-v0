import unittest

from ts_reasoner.habitat import (
    CONFLICTED, SUPPORTED_FALSE, SUPPORTED_TRUE, UNKNOWN,
    HABITAT_ACTION_SCHEMAS, CausalRule, WorldFact, causal_closure, evaluate_habitat, project_signed_state,
)
from ts_reasoner.structured_request import ReasoningRequest, verify_reasoning_request


def fact(identity, subject, predicate, object_id="", polarity="positive"):
    return {"semantic_id":identity,"subject_id":subject,"predicate":predicate,"object_id":object_id,"polarity":polarity,"source_ids":[identity]}


class HabitatV2ReasonerTests(unittest.TestCase):
    def test_required_action_schema_contract_is_explicit(self):
        self.assertEqual([item.action_type for item in HABITAT_ACTION_SCHEMAS],["move","take","unlock","open","give"])
        self.assertTrue(all(item.preconditions and item.effects and item.cost==1 for item in HABITAT_ACTION_SCHEMAS))
    def test_four_valued_projection(self):
        true=project_signed_state([WorldFact.from_dict(fact("p","door","open"))])
        false=project_signed_state([WorldFact.from_dict(fact("n","door","locked",polarity="negative"))])
        conflict=project_signed_state([WorldFact.from_dict(fact("p","door","open")),WorldFact.from_dict(fact("n","door","open",polarity="negative"))])
        self.assertEqual(true["door|open|"].status,SUPPORTED_TRUE)
        self.assertEqual(false["door|locked|"].status,SUPPORTED_FALSE)
        self.assertEqual(conflict["door|open|"].status,CONFLICTED)
        self.assertNotIn("missing|state|",true)

    def test_bounded_causal_chain(self):
        facts=[WorldFact.from_dict(fact("door","door","open")),WorldFact.from_dict(fact("armed","system","armed"))]
        rules=[CausalRule("r1",("door|open|",),"sensor|active|",("r1",)),CausalRule("r2",("sensor|active|","system|armed|"),"alarm|active|",("r2",))]
        state,derivations=causal_closure(facts,rules)
        self.assertEqual(state["alarm|active|"].status,SUPPORTED_TRUE)
        self.assertEqual([x.depth for x in derivations],[1,2])

    def test_conflict_cannot_accept(self):
        payload={"facts":[fact("p","door","open"),fact("n","door","open",polarity="negative")],"query":{"kind":"state","subject_id":"door","predicate":"open"}}
        result=evaluate_habitat(payload)
        self.assertEqual((result.decision,result.subtype,result.signed_status),("REJECT","REJECT_CONFLICTED",CONFLICTED))

    def test_unknown_cannot_accept(self):
        result=evaluate_habitat({"facts":[],"query":{"kind":"state","subject_id":"door","predicate":"open"}})
        self.assertEqual((result.decision,result.signed_status),("REJECT",UNKNOWN))

    def test_structured_request_routes_through_habitat_authority(self):
        request=ReasoningRequest("r","Is the door open?","habitat_query",habitat={"facts":[fact("p","door","open")],"query":{"kind":"state","subject_id":"door","predicate":"open"}})
        decision=verify_reasoning_request(request)
        self.assertEqual((decision.decision,decision.decision_subtype),("ACCEPT","CONCLUSION_VERIFIED"))
        self.assertEqual(decision.answer.support_ids,("p",))

    def test_planner_verifies_example(self):
        facts=[
            fact("alice_hall","alice","at","hall"),fact("box_kitchen","box","at","kitchen"),
            fact("key_box","red_key","inside","box"),fact("door_locked","north_door","locked"),
            fact("key_unlocks","red_key","unlocks","north_door"),
        ]
        outcome=evaluate_habitat({"facts":facts,"query":{"kind":"plan","subject_id":"alice","predicate":"open","object_id":"north_door"}})
        self.assertEqual((outcome.decision,outcome.subtype),("ACCEPT","PLAN_VERIFIED"))
        self.assertEqual(len(outcome.planning.chosen_plan),5)
        self.assertTrue(all(all(c.passed for c in step.precondition_checks) for step in outcome.planning.chosen_plan))

    def test_impossible_plan_rejects(self):
        facts=[fact("alice_hall","alice","at","hall"),fact("door_locked","north_door","locked")]
        outcome=evaluate_habitat({"facts":facts,"query":{"kind":"plan","subject_id":"alice","predicate":"open","object_id":"north_door"}})
        self.assertEqual((outcome.decision,outcome.subtype),("REJECT","REJECT_UNREACHABLE"))


if __name__=="__main__": unittest.main()
