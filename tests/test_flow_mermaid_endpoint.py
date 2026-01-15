from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_mermaid_txt_contains_true_false_for_decision():
    payload={
        "source":"text",
        "payload":"Eğer email boşsa uyar. kaydol. Sonlandır.",
        "options":{}
    }

    r = client.post("/api/flow/mermaid.txt", json=payload)
    assert r.status_code == 200

    txt = r.text
    assert "flowchart TD" in txt
    assert "--|true|-->" in txt.lower() or "--|True|-->" in txt
    assert "--|false|-->" in txt.lower() or "--|False|-->" in txt