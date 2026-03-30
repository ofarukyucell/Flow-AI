from pydantic import BaseModel, Field
from typing import List, Optional


class OptimizeRequest(BaseModel):
    tasks: List[str] = Field(
        ...,
        min_length=1,
        description="Ham görev listesi. Her eleman bir görev metnidir.",
        examples=[["müzik dinle", "kitap oku", "ders çalış", "kütüphaneye git", "vizeye bak"]],
    )
    context: Optional[str] = Field(
        default=None,
        description="Opsiyonel bağlam bilgisi (öğrenci, üretim, ofis vs.)",
    )


class OptimizedStepOut(BaseModel):
    order: int = Field(..., description="Önerilen sıra numarası")
    task: str = Field(..., description="Görev metni")
    async_companions: List[str] = Field(
        default_factory=list,
        description="Bu adımla aynı anda yapılabilecek görevler",
    )
    note: str = Field(default="", description="Türkçe açıklama / gerekçe")
    priority: str = Field(default="normal", description="'high', 'normal' veya 'async'")


class OptimizeResponse(BaseModel):
    ok: bool = True
    original_tasks: List[str] = Field(..., description="Kullanıcının girdiği orijinal görevler")
    optimized_steps: List[OptimizedStepOut] = Field(..., description="Optimize edilmiş adım sırası")
    bottlenecks: List[str] = Field(default_factory=list, description="Tespit edilen darboğazlar")
    async_opportunities: List[str] = Field(
        default_factory=list, description="Paralel yapılabilecek fırsatlar"
    )
    time_saving_tips: List[str] = Field(default_factory=list, description="Zaman kazandıran ipuçları")
    summary: str = Field(..., description="Kısa Türkçe özet")
