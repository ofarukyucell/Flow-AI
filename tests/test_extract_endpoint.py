from fastapi.testclient import TestClient

from backend.main import app

client=TestClient(app)

def test_extract_endpoint_success():
    payload ={
        "source":"text",
        "payload":"giriş yaptım ve analiz ettim; sonra raporladım",
        "options":None,
    } 

    response = client.post("/api/extract",json=payload)

    assert response.status_code==200

    data=response.json()

    assert data["ok"] is True
    assert isinstance(data["flow_id"],str)

    assert isinstance(data["steps"],list)
    assert len(data["steps"]) >=1

    first = data["steps"][0]

    for field in ("action","start_idx","end_idx","snippet"):
        assert field in first

    assert 0<= first["start_idx"] <= first["end_idx"] <= len(payload["payload"])

    snippet = payload ["payload"][first["start_idx"]:first["end_idx"]]
    assert first["snippet"] == snippet



def test_extract_endpoint_empty_payload():
    payload = {
        "source":"text",
        "payload":"   ",
        "options": None,
    }

    response=client.post("/api/extract",json=payload)

    assert response.status_code !=200

    data= response.json()

    assert data.get("ok")is False

    error = data.get("error",{})
    assert error.get("code") == "empty_payload"
    

def test_extract_endpoint_invalid_source():
    payload={
        "source":"tweet",
        "payload":"giriş yaptım",
        "options":None,
    }
    
    response = client.post("/api/extract",json=payload)

    assert response.status_code ==422

    data=response.json()

    assert data.get("ok") is False

    error = data.get("error",{})
    code =  error.get("code", "") 
    message = error.get("message", "") 

    assert "validation" in code.lower()
    assert "validation" in message.lower()

    details=data.get("details")
    if details is not None:
        assert isinstance(details,list)
        assert len(details) >=1

        first = details[0]

        assert first.get("loc",[])[-1]=="source"
        assert first.get("input") =="tweet"    
    