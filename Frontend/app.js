console.log("FLOWAI UI app.js LOADED v-clean-1");

const btn = document.getElementById("btn");
const txt = document.getElementById("txt");
const out = document.getElementById("out");

btn.addEventListener("click", async () => {
  btn.disabled = true;
  btn.textContent = "Çalışıyor...";
  out.textContent = "İstek atılıyor...";

  const payload = {
    source: "text",
    payload: txt.value,
    options: {}
  };

  const diagram = document.getElementById("diagram");
  const mermaidSrc = document.getElementById("mermaid_src");

  diagram.innerHTML = "";
  mermaidSrc.textContent = "---";

  try {
    // 1) Extract (JSON)
    const res1 = await fetch(`/api/extract`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data1 = await res1.json();

    if (!res1.ok) {
      out.innerHTML = `<div class="card">EXTRACT HTTP ${res1.status}<br><pre>${escapeHtml(
        JSON.stringify(data1, null, 2)
      )}</pre></div>`;
      return;
    }

    out.innerHTML = renderResult(data1);

    // 2) Mermaid (plain text)
    const res2 = await fetch(`/api/flow/mermaid.txt`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const mermaidText = await res2.text();

    if (!res2.ok) {
      diagram.innerHTML = `<div class="card">MERMAID HTTP ${res2.status}<br><pre>${escapeHtml(
        mermaidText
      )}</pre></div>`;
      return;
    }

    // Kaynağı göster
    mermaidSrc.textContent = mermaidText;

    // Mermaid yoksa bile text görünsün
    diagram.textContent = mermaidText;

    // Render
    if (!window.mermaid) {
      diagram.innerHTML = `<div class="card">Mermaid kütüphanesi yüklenmedi. (index.html CDN kontrol)</div>`;
      return;
    }

    const id = "flowaiDiagram_" + Date.now();
    const { svg } = await window.mermaid.render(id, mermaidText);
    diagram.innerHTML = svg;

  } catch (err) {
    out.innerHTML = `<div class="card">Hata: ${escapeHtml(err.message)}</div>`;
  } finally {
    btn.disabled = false;
    btn.textContent = "Çalıştır";
  }
});

txt.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    btn.click();
  }
});

function renderResult(data) {
  if (!data || data.ok !== true) {
    return `<div class="card">Beklenmeyen çıktı: <pre>${escapeHtml(
      JSON.stringify(data, null, 2)
    )}</pre></div>`;
  }

  const steps = Array.isArray(data.steps) ? data.steps : [];
  const filtered = steps.filter((s) => {
    const action = (s.action ?? "").trim().toLowerCase();
    if (!action) return false;
    if (action.length < 2) return false;
    const banned = ["deneme", "test", "asdf", "qwe"];
    if (banned.includes(action)) return false;
    return true;
  });

  if (filtered.length === 0) {
    return `
      <div class="card">
        <div class="step-title">Adım bulunamadı</div>
        <div class="muted">Girdi metninde aksiyon tespit edemedim.</div>
      </div>`;
  }

  const items = filtered
    .map((s, i) => {
      const action = s.action ?? "(action yok)";
      const snippet = s.snippet ?? "";
      const start = s.start_idx ?? "?";
      const end = s.end_idx ?? "?";

      return `
      <div class="step">
        <div class="step-title">${i + 1}) <code>${escapeHtml(action)}</code></div>
        <div class="muted">idx: ${start} - ${end}</div>
        <div>${escapeHtml(snippet)}</div>
      </div>
    `;
    })
    .join("");

  return `
    <div class="card">
      <div class="muted">flow_id: <code>${escapeHtml(data.flow_id ?? "")}</code></div>
      <div class="steps">${items}</div>
    </div>`;
}

function escapeHtml(str) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
