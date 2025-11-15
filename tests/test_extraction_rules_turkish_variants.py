from backend.core.extraction_rules import extract_steps_from_text

def test_past_tense():
    text="giriş yaptım, analiz ettim,raporladım"
    assert extract_steps_from_text(text) == ["giriş yap","analiz et","raporla"]

def test_suffix_sonra():
    text= "analiz ettikten sonra raporla"
    assert extract_steps_from_text(text) == ["analiz et","raporla"]

def test_connected_verbs():
    text="dosyayı indirip yükle"
    assert extract_steps_from_text(text) == ["indir","yükle"]
    