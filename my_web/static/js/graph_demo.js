// Демо Йена: K кратчайших путей между двумя товарами.
// Форма → /api/graph/paths?source=&target=&k= → список путей.

const form = document.getElementById("graph-form");
const sourceInput = document.getElementById("source-input");
const targetInput = document.getElementById("target-input");
const kInput = document.getElementById("k-input");
const submitBtn = document.getElementById("graph-submit");
const randomBtn = document.getElementById("graph-random");
const resultBox = document.getElementById("graph-result");
const errorBox = document.getElementById("graph-error");

function showError(msg) {
    errorBox.textContent = msg;
    errorBox.classList.remove("hidden");
    resultBox.classList.add("hidden");
}

function hideError() {
    errorBox.classList.add("hidden");
}

function fmtMs(v) {
    if (v === null || v === undefined) return "—";
    if (v < 1) return v.toFixed(3) + " ms";
    return v.toFixed(1) + " ms";
}

function fmtNum(v) {
    return Number(v).toLocaleString("ru-RU", { maximumFractionDigits: 3 });
}

function renderResult(data) {
    hideError();
    resultBox.classList.remove("hidden");

    const speedup = (data.dijkstra_ms > 0 && data.yen_ms > 0)
        ? (data.yen_ms / data.dijkstra_ms).toFixed(1) + "×"
        : "—";

    let pathsHtml = "";
    if (data.paths.length === 0) {
        pathsHtml = `<p class="result-bad">Путей между ${data.source} и ${data.target} не найдено.</p>`;
    } else {
        pathsHtml = data.paths.map((p, i) => {
            const chain = p.nodes.map(n => `<code>${n}</code>`).join(" → ");
            return `
                <div class="path-item">
                    <div class="path-header">
                        <strong>Путь ${i + 1}</strong>
                        <span class="muted">distance = ${fmtNum(p.distance)} · рёбер = ${p.length}</span>
                    </div>
                    <div class="path-chain">${chain}</div>
                </div>
            `;
        }).join("");
    }

    resultBox.innerHTML = `
        <p>
            <strong>${data.source}</strong> → <strong>${data.target}</strong>,
            запрошено K = ${data.k}, найдено: ${data.paths.length}
        </p>
        <div class="path-list">
            ${pathsHtml}
        </div>
        <div class="metric-row">
            <div class="metric">
                <span class="metric-label">Дейкстра (1 путь)</span>
                <span class="metric-value">${fmtMs(data.dijkstra_ms)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Йен (${data.k} путей)</span>
                <span class="metric-value">${fmtMs(data.yen_ms)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Йен / Дейкстра</span>
                <span class="metric-value">${speedup}</span>
            </div>
        </div>
    `;
}

async function runSearch(source, target, k) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="spinner"></span>Ищу…`;
    try {
        const url = `/api/graph/paths?source=${encodeURIComponent(source)}`
                  + `&target=${encodeURIComponent(target)}`
                  + `&k=${encodeURIComponent(k)}`;
        const resp = await fetch(url);
        if (!resp.ok) {
            const body = await resp.json().catch(() => ({}));
            throw new Error(body.detail || `HTTP ${resp.status}`);
        }
        const data = await resp.json();
        renderResult(data);
    } catch (e) {
        showError("Ошибка: " + e.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Найти пути";
    }
}

form.addEventListener("submit", (e) => {
    e.preventDefault();
    const source = parseInt(sourceInput.value, 10);
    const target = parseInt(targetInput.value, 10);
    const k = parseInt(kInput.value, 10);

    if (!Number.isInteger(source) || source < 1) {
        showError("source должен быть положительным целым");
        return;
    }
    if (!Number.isInteger(target) || target < 1) {
        showError("target должен быть положительным целым");
        return;
    }
    if (!Number.isInteger(k) || k < 1) {
        showError("K должен быть положительным целым");
        return;
    }
    if (source === target) {
        showError("source и target должны различаться");
        return;
    }

    runSearch(source, target, k);
});

randomBtn.addEventListener("click", () => {
    // случайные product_id из 1..1000
    let source = 1 + Math.floor(Math.random() * 1000);
    let target = 1 + Math.floor(Math.random() * 1000);
    while (target === source) {
        target = 1 + Math.floor(Math.random() * 1000);
    }
    sourceInput.value = source;
    targetInput.value = target;
    runSearch(source, target, parseInt(kInput.value, 10));
});

// первый запрос сразу при открытии страницы
runSearch(
    parseInt(sourceInput.value, 10),
    parseInt(targetInput.value, 10),
    parseInt(kInput.value, 10)
);