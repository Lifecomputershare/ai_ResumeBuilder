import json

from resume_engine import ResumeIntelligenceEngine


def test_safety_gate_blocks_fabrication_requests():
    engine = ResumeIntelligenceEngine()
    result = engine.safety_gate("Please fabricate experience for a senior role")
    assert result is not None


def test_score_resume_returns_structured_json():
    engine = ResumeIntelligenceEngine()
    output = engine.score_resume(
        "- Built APIs\n- Optimized SQL queries\n- Implemented CI/CD pipelines",
        ["APIs", "SQL", "CI/CD", "Docker"],
    )
    data = json.loads(output)
    assert set(data.keys()) == {
        "ats_compatibility",
        "role_relevance",
        "clarity_and_impact",
        "overall_score",
    }


def test_rewrite_content_removes_pronouns():
    engine = ResumeIntelligenceEngine()
    rewritten = engine.rewrite_content("I improved our release process and my team velocity")
    assert " I " not in f" {rewritten} "
    assert " my " not in f" {rewritten.lower()} "
