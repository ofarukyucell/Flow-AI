from backend.core.extraction_rules import extract_steps_from_text

def test_arrows():
    text= "giriş yap -> analiz et -> raporla"
    assert extract_steps_from_text(text) == ["giriş yap","analiz et","raporla"]

def test_mixed_separators():
    text="temizle, ardından indir ; ve yükle "
    assert extract_steps_from_text(text) == ["temizle","indir","yükle"]

def test_noise():
    text = "lütfen önce giriş yap, sonra analiz et, ve en son raporla"
    assert extract_steps_from_text(text)==["giriş yap","analiz et", "raporla"]

def test_no_steps():
    assert extract_steps_from_text(".........") == []

def test_json_based_new_verb():
    text = "giriş yap -> faturala -> filtrele"
    assert extract_steps_from_text(text) == ["giriş yap","faturala","filtrele"]