"""Unit tests for the rotated-debate protocol using scripted fake engines."""

import unittest

from rotated_debate.model import DebateSettings
from rotated_debate.parsing import extract_json_block
from rotated_debate.protocol import build_rotations, run_debate


class FakeEngine:
    """Replies by role, inferred from the system prompt; counts answer calls."""

    def __init__(self, alias: str, rebuttal_json: str | None = None) -> None:
        self.alias = alias
        self.answer_calls = 0
        self.rebuttal_json = rebuttal_json or '{"concessions": [], "maintained": ["all"]}'

    def __call__(self, messages: list[tuple[str, str]]) -> str:
        system = messages[0][1]
        if "the ANSWERER in" in system:
            self.answer_calls += 1
            return f"{self.alias} answers."
        if "the CRITIC" in system:
            return (
                f"{self.alias} criticizes.\n```json\n"
                '{"stance": "partial", "objections": ["weak evidence"]}\n```'
            )
        if "responding to a critique" in system:
            return f"{self.alias} rebuts.\n```json\n{self.rebuttal_json}\n```"
        if "the SYNTHESIZER" in system:
            return (
                f"{self.alias} synthesizes.\n```json\n"
                '{"verdict": "converged", "contested_points": []}\n```'
            )
        raise AssertionError(f"unknown role prompt: {system[:60]}")


def make_engines(**rebuttal_json: str) -> dict[str, FakeEngine]:
    return {
        alias: FakeEngine(alias, rebuttal_json.get(alias))
        for alias in ("alpha", "beta", "gamma")
    }


class RotationTests(unittest.TestCase):
    def test_cyclic_rotations_are_balanced(self) -> None:
        triples = build_rotations(["a", "b", "c"], 3)
        for role in range(3):
            self.assertEqual({t[role] for t in triples}, {"a", "b", "c"})

    def test_six_rotations_cover_all_permutations(self) -> None:
        triples = build_rotations(["a", "b", "c"], 6)
        self.assertEqual(len(set(triples)), 6)

    def test_rotation_count_bounds_are_enforced(self) -> None:
        with self.assertRaises(ValueError):
            build_rotations(["a", "b", "c"], 7)
        with self.assertRaises(ValueError):
            build_rotations(["a", "b"], 2)


class DebateTests(unittest.TestCase):
    def test_answers_are_memoized_per_engine(self) -> None:
        engines = make_engines()
        run_debate("q?", engines, DebateSettings(rotations=6))
        for engine in engines.values():
            self.assertEqual(engine.answer_calls, 1)

    def test_capitulation_is_distinguished_from_reasoned_concession(self) -> None:
        engines = make_engines(
            alpha='{"concessions": [{"point": "p1", "reason": null},'
            ' {"point": "p2", "reason": "new evidence"}], "maintained": []}'
        )
        result = run_debate("q?", engines, DebateSettings(rotations=3))
        alpha_concessions = [
            c
            for r in result.rotations
            if r.answerer == "alpha"
            for e in r.rounds
            for c in e.rebuttal.concessions
        ]
        self.assertEqual([c.capitulation for c in alpha_concessions], [True, False])

    def test_unanimous_synthesizer_verdicts_report_converged(self) -> None:
        result = run_debate("q?", make_engines(), DebateSettings(rotations=3))
        self.assertEqual(result.provisional_state, "converged")
        self.assertEqual(len(result.rotations), 3)

    def test_unparseable_synthesis_downgrades_state_without_raising(self) -> None:
        engines = make_engines()

        class MuteSynthesizer(FakeEngine):
            def __call__(self, messages: list[tuple[str, str]]) -> str:
                if "the SYNTHESIZER" in messages[0][1]:
                    return "prose only, no json"
                return super().__call__(messages)

        engines["gamma"] = MuteSynthesizer("gamma")
        result = run_debate("q?", engines, DebateSettings(rotations=3))
        self.assertNotEqual(result.provisional_state, "converged")

    def test_browse_is_rejected_in_v0(self) -> None:
        with self.assertRaises(NotImplementedError):
            run_debate("q?", make_engines(), DebateSettings(browse=True))


class ParsingTests(unittest.TestCase):
    def test_fenced_block_is_preferred(self) -> None:
        data, error = extract_json_block('junk {"a": 1} junk\n```json\n{"b": 2}\n```')
        self.assertIsNone(error)
        self.assertEqual(data, {"b": 2})

    def test_bare_trailing_object_is_recovered(self) -> None:
        data, _ = extract_json_block('no fences here {"verdict": "diverged"}')
        self.assertEqual(data, {"verdict": "diverged"})

    def test_garbage_yields_error_not_exception(self) -> None:
        data, error = extract_json_block("nothing structured at all")
        self.assertIsNone(data)
        self.assertIsNotNone(error)


if __name__ == "__main__":
    unittest.main()
