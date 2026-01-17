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

def test_mermaid_txt_linear_flow_has_no_true_false_edges():
    payload = {
        "source":"text",
        "payload":"Kaydol. Email gönder. Sonlandır.",
        "options":{}
    }
    r = client.post("/api/flow/mermaid.txt",json=payload)
    assert r.status_code==200

    txt=r.text.lower()

    assert "flowchart td" in txt

    assert "--|true|-->" not in txt
    assert "--|false|-->" not in txt

    assert "-->"in txt

def test_mermaid_txt_single_action_has_no_edges_and_no_terminal():
    payload = {
        "source":"text",
        "payload":"Kaydol",
        "options":{}
    }
    r= client.post("/api/flow/mermaid.txt",json=payload)
    assert r.status_code==200

    txt = r.text.lower()

    assert "flowchart td" in txt

    assert '["kaydol"]' in txt

    assert "-->" not in txt

    assert "((" not in txt

def test_mermaid_txt_if_clause_does_not_create_decision_when_only_action_is_extracted():
    payload = {
        "source": "text",
        "payload": "Eğer email varsa kaydol.",
        "options": {}
    }

    r = client.post("/api/flow/mermaid.txt", json=payload)
    assert r.status_code == 200

    txt = r.text.lower()

    
    assert "flowchart td" in txt

    
    assert "--|true|-->" not in txt
    assert "--|false|-->" not in txt
    assert "-->" not in txt

    assert '["kaydol"]' in txt

def test_mermaid_txt_single_decision_node_has_no_edges():
    payload={
        "source":"text",
        "payload":"Eğer email boşsa uyar.",
        "options":{}
    }
    r = client.post("/api/flow/mermaid.txt",json=payload)
    assert r.status_code==200

    txt =r.text.lower()

    assert "flowchart td" in txt

    assert'{"eğer email"}' in txt

    assert "--|true|-->" not in txt
    assert "--|false|-->" not in txt
    assert "-->" not in txt

def test_mermaid_txt_output_is_deterministic_for_same_input():
    payload = {
        "source":"text",
        "payload":"Eğer email boşsa uyar.kaydol. Sonlandır.",
        "options":{}
    }

    r1 = client.post("/api/flow/mermaid.txt",json=payload)
    r2 = client.post("/api/flow/mermaid.txt",json=payload)

    assert r1.status_code==200
    assert r2.status_code==200

    assert r1.text==r2.text

def test_mermaid_txt_escapes_quotes_in_decisio_label():
    payload = {
        "source":"text",
        "payload":'Eğer "email" boşsa uyar (acil)!',
        "options":{}
    }
    r = client.post("/api/flow/mermaid.txt",json=payload)
    assert r.status_code ==200

    txt = r.text

    assert 'n1{"eğer \\"email\\""}' in txt

def test_mermaid_txt_has_no_extra_whitespace_or_blank_lines():
    payload = {
        "source": "text",
        "payload": "Kaydol.\n\nSonlandır.",
        "options": {}
    }

    r = client.post("/api/flow/mermaid.txt", json=payload)
    assert r.status_code == 200

    txt = r.text

    # başta veya sonda boşluk / newline olmamalı
    assert txt == txt.strip()

    # çift boş satır olmamalı
    assert "\n\n" not in txt
