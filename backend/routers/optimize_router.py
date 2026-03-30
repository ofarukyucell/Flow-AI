import logging
from fastapi import APIRouter, Body

from backend.core.task_optimizer import optimize_tasks
from backend.core.errors import ValidationAppError
from backend.models.optimizer_schemas import OptimizeRequest, OptimizeResponse, OptimizedStepOut

router = APIRouter(prefix="/api", tags=["optimize"])
log = logging.getLogger("flowai.optimize")

OPTIMIZE_EXAMPLE = {
    "tasks": [
        "müzik dinle",
        "kitap oku",
        "ders çalış",
        "kütüphaneye git",
        "vizeye bak",
    ],
    "context": "öğrenci",
}


@router.post(
    "/optimize",
    response_model=OptimizeResponse,
    summary="Görev Listesini Optimize Et",
    description=(
        "Verilen görev listesini analiz eder ve şunları yapar:\n\n"
        "- **Konum gruplandırma**: Aynı konuma ait görevleri bir araya getirir\n"
        "- **Asenkron fırsatlar**: Yolda / beklerken yapılabilecek görevleri tespit eder\n"
        "- **Önceliklendirme**: Vize, deadline, acil görevleri öne alır\n"
        "- **Darboğaz tespiti**: Sıralı yapılması gereken görev yığılmalarını bildirir\n"
        "- **Türkçe gerekçe**: Her adım için açıklama üretir"
    ),
    response_description="Optimize edilmiş görev sırası ve öneriler",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "ok": True,
                        "original_tasks": ["müzik dinle", "kitap oku", "ders çalış", "kütüphaneye git", "vizeye bak"],
                        "optimized_steps": [
                            {"order": 1, "task": "kütüphaneye git",
                             "async_companions": ["müzik dinle"],
                             "note": "Kütüphane'ye gidiyorsunuz. Yolda şunları da yapabilirsiniz: müzik dinle.",
                             "priority": "normal"},
                            {"order": 2, "task": "vizeye bak",
                             "async_companions": [],
                             "note": "Öncelikli — Kütüphane'deyken ilk yapın.",
                             "priority": "high"},
                            {"order": 3, "task": "ders çalış",
                             "async_companions": [],
                             "note": "Kütüphane'deyken yapın.",
                             "priority": "normal"},
                            {"order": 4, "task": "kitap oku",
                             "async_companions": [],
                             "note": "Kütüphane'deyken yapın.",
                             "priority": "normal"},
                        ],
                        "bottlenecks": [],
                        "async_opportunities": ["kütüphaneye git sırasında paralel yapılabilir: müzik dinle"],
                        "time_saving_tips": [
                            "Konum optimizasyonu: kütüphane görevlerini tek seferde grupladınız.",
                            "Asenkron fırsat: Seyahat sırasında ek görevler eklendi.",
                        ],
                        "summary": "5 görev analiz edildi. 1 görev paralel yapılabilir olarak işaretlendi. 4 görev konum bazında gruplandı.",
                    }
                }
            }
        }
    },
)
async def optimize(
    req: OptimizeRequest = Body(..., example=OPTIMIZE_EXAMPLE),
) -> OptimizeResponse:
    log.info("optimize:start task_count=%d", len(req.tasks))

    tasks = [t.strip() for t in req.tasks if t.strip()]
    if not tasks:
        raise ValidationAppError("Görev listesi boş olamaz.", code="empty_tasks")
    if len(tasks) > 100:
        raise ValidationAppError("En fazla 100 görev gönderilebilir.", code="too_many_tasks")

    result = optimize_tasks(tasks)

    steps_out = [
        OptimizedStepOut(
            order=s.order,
            task=s.task,
            async_companions=s.async_companions,
            note=s.note,
            priority=s.priority,
        )
        for s in result.optimized_steps
    ]

    log.info(
        "optimize:done tasks=%d steps=%d bottlenecks=%d async=%d",
        len(tasks),
        len(steps_out),
        len(result.bottlenecks),
        len(result.async_opportunities),
    )

    return OptimizeResponse(
        ok=True,
        original_tasks=result.original_tasks,
        optimized_steps=steps_out,
        bottlenecks=result.bottlenecks,
        async_opportunities=result.async_opportunities,
        time_saving_tips=result.time_saving_tips,
        summary=result.summary,
    )
