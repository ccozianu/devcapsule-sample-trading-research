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

    def test_browse_setting_is_recorded_in_the_result(self) -> None:
        result = run_debate("q?", make_engines(), DebateSettings(browse=True))
        self.assertTrue(result.settings.browse)

    def test_progress_is_reported_before_each_engine_call(self) -> None:
        lines: list[str] = []
        run_debate(
            "q?", make_engines(), DebateSettings(rotations=3), on_progress=lines.append
        )
        # 3 memoized answers + per rotation: 1 critique + 1 rebuttal + 1 synthesis.
        self.assertEqual(len(lines), 3 + 3 * 3)
        self.assertEqual(lines[0], "alpha answering")
        self.assertIn("rotation 1/3 round 1/1: beta critiquing alpha", lines)
        self.assertIn("rotation 3/3: beta synthesizing", lines)

    def test_progress_is_optional(self) -> None:
        run_debate("q?", make_engines(), DebateSettings(rotations=3))

    def test_last_synthesizer_judges_only_the_syntheses(self) -> None:
        seen: list[list[tuple[str, str]]] = []

        def judge(messages: list[tuple[str, str]]) -> str:
            seen.append(messages)
            return (
                'verdict text\n```json\n{"verdict": "diverged",'
                ' "factual_agreements": ["price"], "factual_disputes": [],'
                ' "reasoning_agreements": [], "reasoning_disputes": ["odds"]}\n```'
            )

        result = run_debate(
            "q?",
            make_engines(),
            DebateSettings(rotations=3),
            last_synthesizer=("flash", judge),
        )
        assert result.last_synthesis is not None
        self.assertEqual(result.last_synthesis.engine, "flash")
        self.assertEqual(result.last_synthesis.verdict, "diverged")
        self.assertEqual(result.last_synthesis.factual_agreements, ("price",))
        self.assertEqual(result.last_synthesis.reasoning_disputes, ("odds",))
        # The judge's verdict never changes the provisional state (OQ-1 open).
        self.assertEqual(result.provisional_state, "converged")
        # The judge sees the syntheses and nothing of the raw exchange.
        (messages,) = seen
        user_content = messages[-1][1]
        self.assertIn("SYNTHESIS by", user_content)
        self.assertNotIn("criticizes", user_content)

    def test_unparseable_last_synthesis_is_recorded_not_raised(self) -> None:
        result = run_debate(
            "q?",
            make_engines(),
            DebateSettings(rotations=3),
            last_synthesizer=("flash", lambda messages: "prose only"),
        )
        assert result.last_synthesis is not None
        self.assertIsNone(result.last_synthesis.verdict)
        self.assertIsNotNone(result.last_synthesis.parse_error)


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
