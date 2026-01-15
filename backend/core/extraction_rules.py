from __future__ import annotations
import re
import logging
from typing import List,Tuple
import json
from pathlib import Path
from backend.core.regex_patterns import VERB_SUFFIX_PATTERN
from backend.models.schemas import StepProof
from backend.core.action_enrichment import enrich_action
from backend.core.step_canonicalizer import canonicalize_step
from backend.models.flow import NodeType

log = logging.getLogger("flowai.extract")

DEFAULT_CORE_VERBS =[
r"giriş yap",r"çıkış yap",r"kaydol",r"kayıt ol",r"doğrula", r"onayla",
    r"temizle", r"analiz et", r"raporla", r"indir", r"yükle", r"oluştur",
    r"sil", r"güncelle", r"ara", r"paylaş", r"gönder", r"al", r"yapılandır",
    # en kısa kök varyantları (tek kelime komutlar için)
    r"temizle", r"analiz", r"raporla", r"indir", r"yükle", r"aç", r"kapat",r"bas",
    r"tıkla",r"tikla",r"seç",r"sec",r"doldur",r"giriş",r"gir"
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
    r"\.",r"\?",r"\!",
    r"\bsonra\b", r"\bardından\b", r"\btakiben\b", r"\bve\b"
]

SEP_REGEX = re.compile(rf"(?:{'|'.join(STEP_SEPARATORS)})", flags=re.IGNORECASE)

def _split_with_spans(text:str)-> List[tuple[int,int,str]]:
    spans:List[tuple[int,int,str]]=[]
    last=0
    for m in SEP_REGEX.finditer(text):
        start=last
        end=m.start()
        piece=text[start:end]
        if piece.strip():
            spans.append((start,end,piece))
        last = m.end()
    
    if last < len(text):
        piece=text[last:]
        if piece.strip():
            spans.append((last,len(text),piece))
    return spans


NOISE =[
    r"lütfen", r"önce", r"en son", r"ilk olarak", r"ikinci olarak", r"adım",
    r"step", r"aşam(a|aları)?", r"süreç", r"işlem", r"vb\.", r"vs\."
]

NOISE_REGEX = re.compile(rf"\b({'|'.join(NOISE)})\b",flags=re.IGNORECASE)

MULTISPACE = re.compile(r"\s+")

_ESCAPED = sorted((re.escape(v)for v in CORE_VERBS),key=len,reverse=True)
VERB_REGEX=re.compile(rf"\b((?:{'|'.join(_ESCAPED)}))(?:{VERB_SUFFIX_PATTERN})\b",flags=re.IGNORECASE | re.UNICODE)

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

def _extract_commands_from_piece(piece:str) -> list[str]:
    """
    Parça içinde öncelikle tanımlı fiilleri ara.
    Bulunamazsa. ilk kelime + varsa ikinci kelime ile bir 'komut' tahmini yap.
    """

    matches=[m.group(1).strip() for m in VERB_REGEX.finditer(piece)]
    if matches:
        return matches

    tokens = piece.split()
    if not tokens:
        return []
    
    if len(tokens) == 1 :
        return [tokens[0]]
    return [" ".join(tokens[:2])]

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
        cmds = _extract_commands_from_piece(cleaned)
        for cmd in cmds:
            if not cmd:
                continue
            if len(cmd) < 2:
                continue
            cmd =cmd.strip(" .,:;")
            if cmd and cmd not in seen:
                seen.add(cmd)
                steps.append(cmd)

    log.info("regex matched %d step(s)",len(steps))
    return steps

def extract_steps_with_proof(text:str) -> List[StepProof]:
    steps:List[StepProof]=[]

    def classify_step(action: str) -> str:
        a=action.lower()
        if any (k in a for k in ["onay","kontrol","eğer","ise"]):
            return NodeType.decision
        if any(k in a for k in["kapan","iptal","son"]):
            return NodeType.terminal
        ACTION_KEYS = [
            "oluştur","aç","başlat","doldur","seç","bas","tıkla","tikla"
            ,"gir","yaz","ekle","çıkar","sil","güncelle","yükle","indir","gönder","kaydol"
        ]
        if any (k in a for k in ACTION_KEYS):
            return NodeType.action
        return NodeType.trigger
    spans=_split_with_spans(text)

    for start_idx,end_idx,snippet in spans:
        snippet=snippet.strip()
        cleaned = _denoise(snippet.lower())
        if not cleaned:
            continue

        cmds = _extract_commands_from_piece(cleaned)
        for cmd in cmds:
            action=enrich_action(sentence=snippet,verb=cmd).enriched_action

            raw_snippet = text[start_idx:end_idx]
            steps.append(
                StepProof(
                    action=action,
                    start_idx=start_idx,
                    end_idx=end_idx,
                    snippet=raw_snippet,
                    type=classify_step(action),
                )
            )
    
    filtered: List[StepProof]=[]

    for s in steps:
        a=(s.action or "").strip()

        if ":" not in a:
            filtered.append(s)
            continue

        verb,obj= [x.strip() for x in a.split(":",1)]

        if not verb or not obj:
            filtered.append(s)
            continue
        
        if verb.casefold() == obj.casefold():
            continue

        filtered.append(s)

    filtered = [canonicalize_step(s) for s in filtered]

    return filtered
