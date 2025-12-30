from dataclasses import dataclass
from typing import Optional
import re

BUTTON_ACTION_RE = re.compile(
    r"(?P<obj>.+?)\s+(butonuna|butona)\s+(bas|tıkla)",
    re.IGNORECASE
)

FIELD_ACTION_RE= re.compile(
    r"(?P<obj>.+?)\s+(alanını|alanı|formu|formunu)\s+(doldur)",
    re.IGNORECASE

)

SELECT_ACTION_RE= re.compile(
    r"(?P<obj>.+?)\s+(seç)",
    re.IGNORECASE
)

@dataclass
class EnrichmentResult:
    verb: str
    obj: Optional[str]
    enriched_action: str

def enrich_action(sentence: str, verb: str) -> EnrichmentResult:
    sentence = sentence.strip()
    verb = verb.strip()

    #1. Button (not benjamin)
    match = BUTTON_ACTION_RE.search(sentence)
    if match:
        obj = match.group("obj").strip()
        enriched = f"{verb}:{obj}"
        return EnrichmentResult(
            verb= verb,
            obj= obj,
            enriched_action=enriched
        )

    #2. Button
    match = FIELD_ACTION_RE.search(sentence)
    if match:
        obj=match.group("obj").strip()
        enriched = f"{verb}:{obj}"
        return EnrichmentResult(
            verb=verb,
            obj=obj,
            enriched_action=enriched
        )
    
    #3. Button
    match = SELECT_ACTION_RE.search(sentence)
    if match:
        obj=match.group("obj").strip()
        enriched= f"{verb}:{obj}"
        return EnrichmentResult(
            verb=verb,
            obj=obj,
            enriched_action=enriched
        )


    return EnrichmentResult (
            verb=verb,
            obj=None,
            enriched_action= verb
        )
   