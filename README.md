[![FlowAI CI](https://github.com/ofarukyucell/Flow-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/ofarukyucell/Flow-AI/actions/workflows/ci.yml)

# FlowAI

FlowAI, metin tabanlı süreç açıklamalarından yapılandırılmış süreç adımları
çıkarmayı amaçlayan Python tabanlı bir web uygulamasıdır.

Proje, doğal dil ile yazılmış ve yapılandırılmamış süreç anlatımlarını
daha anlaşılır ve takip edilebilir hale getirmeyi hedefler.

---

## FlowAI Ne Yapar?

- Metin tabanlı süreç açıklamalarını girdi olarak alır  
- Süreç adımlarını tespit eder ve ayrıştırır  
- Karmaşık anlatımları adım adım bir akış yapısına dönüştürür  
- Dokümantasyon ve süreç analizi çalışmalarını kolaylaştırır  

---

## Nasıl Çalışır?

FlowAI, metin işleme odaklı kural tabanlı yaklaşımlar kullanır.

Uygulama kapsamında:
- Regex tabanlı desen eşleştirme  
- Kural tabanlı NLP mantığı  
- Süreç adımlarının normalize edilmesi ve sıralanması  

yaklaşımları uygulanmıştır.

Bu projede, karmaşık makine öğrenmesi modelleri yerine
yorumlanabilir ve anlaşılır yöntemler tercih edilmiştir.

---

## Kullanılan Teknolojiler

- Python  
- FastAPI  
- Regex tabanlı metin işleme  
- Kural tabanlı NLP  
- Docker  

---

## Projeyi Çalıştırma (Temel)

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
