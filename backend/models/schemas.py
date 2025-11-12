from pydantic import BaseModel, Field
from typing import Optional, Literal, Any ,Dict

class ExtractRequest(BaseModel):
    source: Literal["text", "url","file"] = Field(...,description="Kaynak tipi")
    payload: str = Field(...,min_length=1, description="Ham içerik veya URL")
    options: Optional[Dict[str,Any]] = Field(default=None,description="ek ayarlar")

class ExtractResponse(BaseModel):
    ok: bool=True
    flow_id:str = Field(...,description="oluşan flow için kimlik")
    steps:list[str]=Field (default_factory=list,description="çıkarılan adımlar")