from __future__ import annotations
import re
import logging
from typing import List
import json
from pathlib import Path

log = logging.getLogger("flowai.extract")

DEFAULT_CORE_VERBS =[
r"giriş yap",r"çıkış yap",r"kaydol",r"kayıt ol",r"doğrula", r"onayla",
    r"temizle", r"analiz et", r"raporla", r"indir", r"yükle", r"oluştur",
    r"sil", r"güncelle", r"ara", r"paylaş", r"gönder", r"al", r"yapılandır",
    # en kısa kök varyantları (tek kelime komutlar için)
    r"temizle", r"analiz", r"raporla", r"indir", r"yükle", r"aç", r"kapat",
]

def _load_core_verbs() ->list[str]:
    """
    backend/core/verbs_tr.jsondan filleri yükler eğer 
    dosya yolu bulunamazsa default_core_verbsden fiilleri çeker.
    """
    try:
        verbs_path = Path(__file__).parent / "verbs_tr.json"
        if verbs_path.exists():
            data = json.loads(verbs_path.read_text(encoding="utf-8"))
            cleaned = []
            seen = set()
            for v in data:
                if not isinstance(v,str):
                    continue
                vv = v.strip().lower()
                if len (vv)<2 or vv in seen:
                    continue
                seen.add(vv)
                cleaned.append(vv)
            if cleaned:
                return cleaned
    except Exception as e:
        log.warning("verbs json load failed: %s",e)
    return[v.lower() for v in DEFAULT_CORE_VERBS ]

CORE_VERBS=_load_core_verbs()

STEP_SEPARATORS = [
    r"→", r"->", r"⇒", r">", r"•", r"‣", r"›",
    r"\|", r";", r",",
    r"\bsonra\b", r"\bardından\b", r"\btakiben\b", r"\bve\b"
]

SEP_REGEX = re.compile(rf"(?:{'|'.join(STEP_SEPARATORS)})", flags=re.IGNORECASE)

NOISE =[
    r"lütfen", r"önce", r"en son", r"ilk olarak", r"ikinci olarak", r"adım",
    r"step", r"aşam(a|aları)?", r"süreç", r"işlem", r"vb\.", r"vs\."
]

NOISE_REGEX = re.compile(rf"\b({'|'.join(NOISE)})\b",flags=re.IGNORECASE)

MULTISPACE = re.compile(r"\s+")

_ESCAPED = sorted((re.escape(v)for v in CORE_VERBS),key=len,reverse=True)
VERB_REGEX=re.compile(rf"\b({'|'.join(_ESCAPED)})\b",flags=re.IGNORECASE |re.UNICODE)

def _normalize(text: str) ->str:
    t= text.strip().lower()
    return t

def _split_into_candidates(text:str) -> List[str]:
    parts = [p.strip() for p in SEP_REGEX.split(text) if p and p.strip()]
    return parts

def _denoise(piece: str) ->str:
    p=NOISE_REGEX.sub(" ",piece)
    p=MULTISPACE.sub(" ",p).strip(" .:---")
    return p

def _extract_command_from_piece(piece:str) -> str | None:
    """
    Parça içinde öncelikle tanımlı fiilleri ara.
    Bulunamazsa. ilk kelime + varsa ikinci kelime ile bir 'komut' tahmini yap.
    """

    m=VERB_REGEX.search(piece)
    if m:
        return m.group(1).strip()

    
    tokens = piece.split()
    if not tokens:
        return None
    
    if len(tokens) == 1 :
        return tokens[0]
    return " ".join(tokens[:2])

def extract_steps_from_text(text:str)->List[str]:
    """
    doğal dilden adım listesi üretir.
    -Normalizasyon
    -Ayırıcılara göre parçalama
    -Gürültü temizliği
    -Fiil eşleşmesi (regex) + heuristik yedek
    -yinelenenleri sırayı bozmadan kaldırma
    """
    norm=_normalize(text)
    candidates= _split_into_candidates(norm)

    steps:List[str]=[]
    seen=set()

    for raw in candidates:
        cleaned = _denoise(raw)
        if not cleaned:
            continue
        cmd = _extract_command_from_piece(cleaned)
        if not cmd:
            continue
        if len(cmd)<2:
            continue
        cmd = cmd.strip(" .,:;")
        if cmd and cmd not in seen:
            seen.add(cmd)
            steps.append(cmd)
    log.info("regex matched %d step(s)",len(steps))
    return steps