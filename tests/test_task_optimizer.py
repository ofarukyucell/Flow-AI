"""
FlowAI Task Optimizer testleri
- Öğrenci senaryosu (kütüphane + müzik + vize)
- Seyahat sırasında async görev
- Darboğaz tespiti
- Önceliklendirme
- Boş liste
- Endpoint testi
"""

import pytest
from fastapi.testclient import TestClient

from backend.core.task_optimizer import optimize_tasks
from backend.main import app

client = TestClient(app)


# ─── Unit Testler ─────────────────────────────────────────────────────────────

def test_student_scenario():
    """Senin tarif ettiğin tam senaryo: müzik + kitap + ders + kütüphane + vize"""
    tasks = ["müzik dinle", "kitap oku", "ders çalış", "kütüphaneye git", "vizeye bak"]
    result = optimize_tasks(tasks)

    assert len(result.optimized_steps) >= 1

    # Kütüphaneye gitme adımında müzik paralel companion olmalı
    travel_steps = [s for s in result.optimized_steps if "kütüphane" in s.task.lower()]
    assert len(travel_steps) >= 1
    travel = travel_steps[0]
    assert any("müzik" in c.lower() for c in travel.async_companions), (
        "Kütüphaneye giderken müzik dinleme fırsatı tespit edilmeli"
    )


def test_high_priority_vize_comes_first_in_location():
    """Vize görevi kütüphanedeyken ilk yapılacaklar arasında öncelikli olmalı"""
    tasks = ["kitap oku", "vizeye bak", "ders çalış", "kütüphaneye git"]
    result = optimize_tasks(tasks)

    # Vize adımı önce gelmeli (konum içinde)
    vize_steps = [s for s in result.optimized_steps if "vize" in s.task.lower()]
    diger_steps = [s for s in result.optimized_steps
                   if "vize" not in s.task.lower() and "kütüphane" not in s.task.lower()]

    assert len(vize_steps) >= 1
    if diger_steps:
        assert vize_steps[0].order <= diger_steps[0].order, (
            "Vize görevi öncelikli olmalı ve daha önce sıralanmalı"
        )


def test_async_task_attached_to_travel():
    """Seyahat görevi varsa async görev ona eklenmeli, ayrı adım olmamalı"""
    tasks = ["müzik dinle", "markete git", "alışveriş yap"]
    result = optimize_tasks(tasks)

    # Müzik bağımsız adım olarak olmamalı, travel'a companion olmalı
    standalone_muzik = [
        s for s in result.optimized_steps
        if "müzik" in s.task.lower() and s.priority == "async"
    ]
    assert len(standalone_muzik) == 0, (
        "Müzik, seyahat adımına companion olarak eklenmeli, tek başına adım olmamalı"
    )

    assert len(result.async_opportunities) >= 1


def test_bottleneck_detected_with_many_location_tasks():
    """Bir konumda 3+ sıralı görev varsa darboğaz uyarısı vermeli"""
    tasks = [
        "kütüphaneye git",
        "ders çalış",
        "kitap oku",
        "not al",
        "vizeye bak",
    ]
    result = optimize_tasks(tasks)
    assert len(result.bottlenecks) >= 1, "Kütüphanede 4 sıralı görev = darboğaz uyarısı beklenir"


def test_empty_tasks():
    result = optimize_tasks([])
    assert result.optimized_steps == []
    assert result.summary == "Görev listesi boş."


def test_single_task():
    result = optimize_tasks(["ders çalış"])
    assert len(result.optimized_steps) == 1


def test_no_location_all_standalone():
    """Konum görevi yoksa görevler olduğu gibi (öncelik sırası ile) döner"""
    tasks = ["email gönder", "rapor hazırla", "toplantı oluştur"]
    result = optimize_tasks(tasks)
    assert len(result.optimized_steps) == 3


def test_async_without_travel():
    """Seyahat görevi yoksa async görev bağımsız adım olarak listelenmeli"""
    tasks = ["email oku", "müzik dinle"]
    result = optimize_tasks(tasks)
    muzik_steps = [s for s in result.optimized_steps if "müzik" in s.task.lower()]
    assert len(muzik_steps) == 1
    assert muzik_steps[0].priority == "async"


# ─── Endpoint Testleri ────────────────────────────────────────────────────────

def test_optimize_endpoint_student_scenario():
    payload = {
        "tasks": ["müzik dinle", "kitap oku", "ders çalış", "kütüphaneye git", "vizeye bak"],
        "context": "öğrenci",
    }
    r = client.post("/api/optimize", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert isinstance(data["optimized_steps"], list)
    assert len(data["optimized_steps"]) >= 1
    assert isinstance(data["summary"], str)
    assert len(data["summary"]) > 0


def test_optimize_endpoint_empty_tasks():
    payload = {"tasks": []}
    r = client.post("/api/optimize", json=payload)
    assert r.status_code != 200
    data = r.json()
    assert data.get("ok") is False


def test_optimize_endpoint_whitespace_only():
    payload = {"tasks": ["   ", "  "]}
    r = client.post("/api/optimize", json=payload)
    assert r.status_code != 200


def test_optimize_endpoint_response_structure():
    payload = {"tasks": ["kütüphaneye git", "ders çalış", "müzik dinle"]}
    r = client.post("/api/optimize", json=payload)
    assert r.status_code == 200
    data = r.json()
    required_fields = [
        "ok", "original_tasks", "optimized_steps",
        "bottlenecks", "async_opportunities", "time_saving_tips", "summary"
    ]
    for field in required_fields:
        assert field in data, f"'{field}' alanı response'da eksik"
