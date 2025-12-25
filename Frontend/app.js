// const BASE_URL= "https://flowai-backend-3l6u.onrender.com";

const btn=document.getElementById("btn");
const txt=document.getElementById("txt");
const out=document.getElementById("out");

btn.addEventListener("click",async () =>{
    btn.disabled = true;
    btn.textContent = "Çalışıyor. . .";
    out.textContent="İstek atılıyor. . .";

    const payload={
        source:"text",
        payload:txt.value,
        options: {}
    };
    try {
        const res = await fetch(`/api/extract`,{
            method:"POST",
            headers: { "Content-Type":"application/json"},
            body: JSON.stringify(payload)
        });
        const data= await res.json();

        if(!res.ok) {
            out.innerHTML = `<div class="card">HTTP ${res.status}<br><pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre></div>`;
            return
        }

        out.innerHTML = renderResult(data);
        
    } catch(err){
        out.textContent = "Hata: " + err.message;
    }finally{
        btn.disabled = false;
        btn.textContent = "Extract";
    }

});
txt.addEventListener("keydown", (e)=>{
    if (e.key ==="Enter" && !e.shiftKey){
        e.preventDefault();
        btn.click();
    }
});

function renderResult(data){
    if (!data || data.ok !== true){
        return `<div class="card">Beklenmeyen çıktı: <pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre></div>`;

    }
    const steps = Array.isArray(data.steps) ? data.steps: [];
    const filtered = steps.filter(s => {
  const action = (s.action ?? "").trim().toLowerCase();
  // 1) boşsa at
  if (!action) return false;
  // 2) çok kısaysa at (mesela "aç" kalsın, ama 1 harf atılsın)
  if (action.length < 2) return false;
  // 3) demo/test kelimeleri at (istersen listeyi büyütürüz)
  const banned = ["deneme", "test", "asdf", "qwe"];
  if (banned.includes(action)) return false;
  return true;
});


    if (filtered.length === 0){
        return`
        <div class="card">
          <div class="step-title">Adım bulunamadı</div>
          <div class="muted">Girdi metninde aksiyon tespit edemedim. </div>
        </div>`;
    }

    const items = filtered.map((s,i) => {
        const action = s.action ?? "(action yok)";
        const snippet = s.snippet ?? "";
        const start = s.start_idx ?? "?";
        const end = s.end_idx ?? "?";

        return `
        <div class="step">
          <div class="step-title">${i+1}) <code>${escapeHtml(action)}</code></div>
          <div class= "muted">idx: ${start} - ${end}</div>
          <div>${escapeHtml(snippet)}</div>
        </div>
        `;
    }).join("");
    return `
    <div class="card">
      <div class="muted">flow_id:<code>${escapeHtml(data.flow_id)}</code></div>
      <div class="steps">${items}</div>
      </div>`
}
function escapeHtml(str){
    return String(str)
      .replaceAll("&","&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
}
