import pytest

from backend.core.extraction_rules import extract_steps_with_proof
from backend.models.schemas import StepProof

def test_step_proof_basif_indices():
    text= "giriş uyaptım ve analiz ettim; sonra raporladım."
    steps= extract_steps_with_proof(text)

    assert len(steps)>= 3

    for s in steps:
        assert isinstance(s,StepProof)

        assert 0 <= s.start_idx <=s.end_idx<=len(text)

        assert s.snippet == text[s.start_idx:s.end_idx]

    actions=[s.action for s in steps]
    assert any("giriş" in a for a in actions)
    assert any("analiz" in a for a in actions)
    assert any("raporla" in a for a in actions)

def test_step_proof_empty_text():
    text=""
    steps = extract_steps_with_proof(text)

    assert steps ==[]
