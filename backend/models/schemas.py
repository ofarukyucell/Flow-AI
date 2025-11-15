from pydantic import BaseModel, Field
from typing import Optional, Literal, Any ,Dict,List

class StepProof(BaseModel):
    action:str = Field(...,description="Normalize edilmiş eylem kökü, ör:'giriş yap' ")
    start_idx:int = Field(...,ge=0,description="Metin içinde başlangıç index")
    end_idx:int=Field(...,ge=0,description="metin içinde bitiş index(exclusive)")
    snippet:str=Field(...,description="Eşleşen ham parça")

class ExtractRequest(BaseModel):
    source: Literal["text", "url","file"] = Field(...,description="Kaynak tipi")
    payload: str = Field(...,min_length=1, description="Ham içerik veya URL")
    options: Optional[Dict[str,Any]] = Field(default=None,description="ek ayarlar")

class ExtractResponse(BaseModel):
    ok: bool=True
    flow_id:str = Field(...,description="oluşan flow için kimlik")
    steps:List[StepProof]=Field (default_factory=list,description="çıkarılan adımların kanıtlı listesi")