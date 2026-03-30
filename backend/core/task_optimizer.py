"""
FlowAI Task Optimizer
=====================
Görev listesini alır ve şunları yapar:
  1. Her görevi kategorize eder (konum, asenkron, öncelikli, normal)
  2. Konum bağımlılıklarını tespit eder (kütüphane gitme + orada ders çalışma = grupla)
  3. Asenkron fırsatları bulur (yolda müzik dinle)
  4. Darboğazları tespit eder (aynı konumda sıralı yapılması gereken çok iş)
  5. Öncelik sıralaması yapar (vize > normal görev > opsiyonel)
  6. Türkçe açıklamalarla optimize edilmiş sıra döner
"""
from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set

log = logging.getLogger("flowai.optimizer")

# ──────────────────────────────────────────────
# Bilgi tabanı: anahtar kelime -> kategori eşleşmeleri
# ──────────────────────────────────────────────

# Konum belirten görevler: görev metni -> konum adı
LOCATION_ANCHORS: Dict[str, str] = {
    "kütüphane": "kütüphane",
    "kütüphanede": "kütüphane",
    "kütüphaneye": "kütüphane",
    "market": "market",
    "markete": "market",
    "marketten": "market",
    "okul": "okul",
    "okulda": "okul",
    "okula": "okul",
    "kampüs": "kampüs",
    "kampüste": "kampüs",
    "hastane": "hastane",
    "hastaneye": "hastane",
    "banka": "banka",
    "bankaya": "banka",
    "spor salonu": "spor salonu",
    "spor salonuna": "spor salonu",
    "gym": "spor salonu",
    "eve": "ev",
    "evde": "ev",
    "ofis": "ofis",
    "ofiste": "ofis",
    "ofise": "ofis",
    "cafe": "cafe",
    "kafede": "cafe",
    "kafeterya": "kafeterya",
}

# Konum bağımlı görevler: görev içerdiği kelime -> tercih ettiği konum
LOCATION_DEPENDENT: Dict[str, str] = {
    "kitap oku": "kütüphane",
    "ders çalış": "kütüphane",
    "çalış": "kütüphane",
    "not al": "kütüphane",
    "vize": "kütüphane",
    "vizeye": "kütüphane",
    "vize çalış": "kütüphane",
    "sınava çalış": "kütüphane",
    "sınav": "kütüphane",
    "final": "kütüphane",
    "ödev yap": "kütüphane",
    "ödev": "kütüphane",
    "alışveriş yap": "market",
    "alışveriş": "market",
    "ürün al": "market",
    "egzersiz": "spor salonu",
    "antrenman": "spor salonu",
    "koş": "spor salonu",
}

# Asenkron (paralel yapılabilir) görevler
ASYNC_KEYWORDS: List[str] = [
    "müzik dinle",
    "müzik",
    "podcast dinle",
    "podcast",
    "sesli kitap",
    "haber dinle",
    "telefonda konuş",
    "telefon et",
    "mesaj at",
    "düşün",
    "plan yap",
    "not tut",
]

# Yüksek öncelikli görev işaretleri
HIGH_PRIORITY_KEYWORDS: List[str] = [
    "vize",
    "vizeye",
    "sınav",
    "final",
    "deadline",
    "teslim",
    "randevu",
    "acil",
    "ödev teslim",
    "son tarih",
    "bitir",
    "tamamla",
]

# Seyahat/geçiş anı (async görevlerin ekleneceği an)
TRAVEL_KEYWORDS: List[str] = [
    "git",
    "gel",
    "yürü",
    "yola çık",
    "hareket et",
    "ulaş",
    "bindir",
    "al",
]


# ──────────────────────────────────────────────
# Görev veri modeli
# ──────────────────────────────────────────────

@dataclass
class TaskItem:
    raw: str                          # Kullanıcının yazdığı orijinal metin
    cleaned: str                      # Normalize edilmiş metin
    is_async: bool = False            # Paralel yapılabilir mi?
    is_high_priority: bool = False    # Öncelikli mi (vize, deadline)?
    location_anchor: Optional[str] = None   # Bu görev bir konuma "gider" mi?
    location_dependent: Optional[str] = None  # Bu görevin tercih ettiği konum
    parallel_with: List[str] = field(default_factory=list)  # Hangi görevle birlikte?
    note: str = ""                    # Açıklama


@dataclass
class OptimizedStep:
    order: int
    task: str
    original: str
    async_companions: List[str] = field(default_factory=list)  # Aynı anda yapılabilecekler
    note: str = ""
    priority: str = "normal"  # "high" / "normal" / "async"


@dataclass
class OptimizeResult:
    original_tasks: List[str]
    optimized_steps: List[OptimizedStep]
    bottlenecks: List[str]
    async_opportunities: List[str]
    time_saving_tips: List[str]
    summary: str


# ──────────────────────────────────────────────
# Yardımcı fonksiyonlar
# ──────────────────────────────────────────────

def _normalize(text: str) -> str:
    return text.strip().lower()


def _detect_location_anchor(text: str) -> Optional[str]:
    """Metinde konum belirten kelime var mı?"""
    t = _normalize(text)
    for kw, loc in LOCATION_ANCHORS.items():
        if kw in t:
            return loc
    return None


def _detect_location_dependent(text: str) -> Optional[str]:
    """Bu görev belli bir konumda yapılmayı gerektiriyor mu?"""
    t = _normalize(text)
    for kw, loc in LOCATION_DEPENDENT.items():
        if kw in t:
            return loc
    return None


def _is_async(text: str) -> bool:
    t = _normalize(text)
    return any(kw in t for kw in ASYNC_KEYWORDS)


def _is_high_priority(text: str) -> bool:
    t = _normalize(text)
    return any(kw in t for kw in HIGH_PRIORITY_KEYWORDS)


def _is_travel(text: str) -> bool:
    t = _normalize(text)
    return any(kw in t for kw in TRAVEL_KEYWORDS)


def _categorize_tasks(raw_tasks: List[str]) -> List[TaskItem]:
    items: List[TaskItem] = []
    for raw in raw_tasks:
        cleaned = _normalize(raw)
        item = TaskItem(raw=raw, cleaned=cleaned)
        item.is_async = _is_async(cleaned)
        item.is_high_priority = _is_high_priority(cleaned)
        item.location_anchor = _detect_location_anchor(cleaned)
        item.location_dependent = _detect_location_dependent(cleaned)
        items.append(item)
    return items


# ──────────────────────────────────────────────
# Ana optimizasyon motoru
# ──────────────────────────────────────────────

def optimize_tasks(raw_tasks: List[str]) -> OptimizeResult:
    """
    Görev listesini alır, akıllı sıralama + paralel fırsatlar döner.
    """
    if not raw_tasks:
        return OptimizeResult(
            original_tasks=[],
            optimized_steps=[],
            bottlenecks=[],
            async_opportunities=[],
            time_saving_tips=[],
            summary="Görev listesi boş.",
        )

    items = _categorize_tasks(raw_tasks)

    # ─── Adım 1: Asenkron görevleri ayır
    async_tasks = [t for t in items if t.is_async]
    non_async_tasks = [t for t in items if not t.is_async]

    # ─── Adım 2: Konum seyahat görevlerini bul
    travel_tasks = [t for t in non_async_tasks if t.location_anchor is not None]
    regular_tasks = [t for t in non_async_tasks if t.location_anchor is None]

    # ─── Adım 3: Konum grupları oluştur
    # Her konum seyahat görevi için, o konumda yapılabilecekleri bul
    location_groups: Dict[str, List[TaskItem]] = {}
    for travel in travel_tasks:
        loc = travel.location_anchor
        if loc not in location_groups:
            location_groups[loc] = [travel]
        # Aynı konuma bağlı diğer görevleri ekle
        for reg in regular_tasks:
            if reg.location_dependent == loc and reg not in location_groups[loc]:
                location_groups[loc].append(reg)

    # Konum grubu içindeki görevler regular_tasks'tan çıkar
    grouped_tasks: Set[str] = set()
    for group in location_groups.values():
        for t in group:
            grouped_tasks.add(t.cleaned)

    standalone_tasks = [t for t in regular_tasks if t.cleaned not in grouped_tasks]

    # ─── Adım 4: Öncelik sıralama
    # Yüksek öncelikli görevler, konum grubu içinde öne alınır
    def sort_group(tasks: List[TaskItem]) -> List[TaskItem]:
        return sorted(tasks, key=lambda t: (
            0 if t.location_anchor else 1,   # Konum seyahati önce
            0 if t.is_high_priority else 1,  # Yüksek öncelikli
            tasks.index(t),                   # Orijinal sıra korunsun
        ))

    # ─── Adım 5: Optimize edilmiş sıralamayı oluştur
    optimized: List[OptimizedStep] = []
    order = 1
    bottlenecks: List[str] = []
    async_opportunities: List[str] = []
    tips: List[str] = []

    # Önce standalone görevler (konum bağımsız, öncelikli olanlar önce)
    standalone_sorted = sorted(standalone_tasks, key=lambda t: 0 if t.is_high_priority else 1)
    for t in standalone_sorted:
        step = OptimizedStep(
            order=order,
            task=t.raw,
            original=t.raw,
            priority="high" if t.is_high_priority else "normal",
            note="Öncelikli görev." if t.is_high_priority else "",
        )
        optimized.append(step)
        order += 1

    # Sonra konum grupları
    for loc, group in location_groups.items():
        sorted_group = sort_group(group)

        # Seyahat adımına asenkron görevleri ekle
        travel_step = sorted_group[0]
        companion_labels = [a.raw for a in async_tasks]

        step = OptimizedStep(
            order=order,
            task=travel_step.raw,
            original=travel_step.raw,
            async_companions=companion_labels,
            priority="normal",
            note=f"{loc.capitalize()}'ye gidiyorsunuz." + (
                f" Yolda şunları da yapabilirsiniz: {', '.join(companion_labels)}."
                if companion_labels else ""
            ),
        )
        optimized.append(step)
        order += 1

        if companion_labels:
            async_opportunities.append(
                f"{travel_step.raw.capitalize()} sırasında paralel yapılabilir: {', '.join(companion_labels)}"
            )

        # Konumdaki diğer görevler
        loc_tasks = sorted_group[1:]
        if len(loc_tasks) >= 2:
            bottlenecks.append(
                f"{loc.capitalize()}'de sıralı yapılması gereken {len(loc_tasks)} görev var — "
                f"bu bir darboğaz olabilir. Bir kısmını farklı bir oturuma taşıyın."
            )

        for t in loc_tasks:
            step = OptimizedStep(
                order=order,
                task=t.raw,
                original=t.raw,
                priority="high" if t.is_high_priority else "normal",
                note=(
                    f"Öncelikli — {loc.capitalize()}'deyken ilk yapın."
                    if t.is_high_priority
                    else f"{loc.capitalize()}'deyken yapın."
                ),
            )
            optimized.append(step)
            order += 1

    # Asenkron görevlerin kendisi listeye eklenmez (zaten bir adımla birleşti)
    # Ama hiç seyahat yoksa bağımsız olarak listeye ekle
    if not travel_tasks:
        for a in async_tasks:
            step = OptimizedStep(
                order=order,
                task=a.raw,
                original=a.raw,
                priority="async",
                note="Bu görev başka bir görevle aynı anda yapılabilir.",
            )
            optimized.append(step)
            order += 1

    # ─── Adım 6: İpuçları üret
    if location_groups:
        locs = list(location_groups.keys())
        tips.append(
            f"Konum optimizasyonu: {', '.join(locs)} görevlerini tek seferde grupladınız. "
            "Bu gereksiz yolculukları önler."
        )
    if async_opportunities:
        tips.append(
            "Asenkron fırsat: Seyahat sırasında ek görevler eklendi, böylece boşa giden zaman sıfırlandı."
        )
    if len([t for t in items if t.is_high_priority]) > 0:
        tips.append("Öncelikli görevler (vize, sınav, deadline) listenin başına alındı.")

    # ─── Özet
    n_orig = len(raw_tasks)
    n_async = len(async_tasks)
    n_loc = sum(len(g) for g in location_groups.values())
    summary_parts = [f"{n_orig} görev analiz edildi."]
    if n_async:
        summary_parts.append(f"{n_async} görev paralel yapılabilir olarak işaretlendi.")
    if n_loc:
        summary_parts.append(f"{n_loc} görev konum bazında gruplandı.")
    if bottlenecks:
        summary_parts.append(f"{len(bottlenecks)} olası darboğaz tespit edildi.")

    return OptimizeResult(
        original_tasks=raw_tasks,
        optimized_steps=optimized,
        bottlenecks=bottlenecks,
        async_opportunities=async_opportunities,
        time_saving_tips=tips,
        summary=" ".join(summary_parts),
    )
