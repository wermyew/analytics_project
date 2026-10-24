// Демо Segment Tree: query(l, r) и update(pos, value).

const lSlider = document.getElementById("range-l");
const rSlider = document.getElementById("range-r");
const lLabel = document.getElementById("label-l");
const rLabel = document.getElementById("label-r");
const queryBtn = document.getElementById("query-run");
const queryResult = document.getElementById("query-result");
const queryError = document.getElementById("query-error");

const updateForm = document.getElementById("update-form");
const updatePos = document.getElementById("update-pos");
const updateValue = document.getElementById("update-value");
const updateSubmit = document.getElementById("update-submit");
const updateResult = document.getElementById("update-result");
const updateError = document.getElementById("update-error");

const MAX_IDX = 119999;

function fmtMs(v) {
    if (v === null || v === undefined) return "—";
    if (v < 1) return v.toFixed(3) + " ms";
    return v.toFixed(1) + " ms";
}

function fmtNum(v) {
    return Number(v).toLocaleString("ru-RU", { maximumFractionDigits: 2 });
}

function syncLabels() {
    let l = parseInt(lSlider.value, 10);
    let r = parseInt(rSlider.value, 10);
    if (l > r) {
        // если l переехал за r — подтолкнём r
        rSlider.value = l;
        r = l;
    }
    lLabel.textContent = l;
    rLabel.textContent = r;
}

async function runQuery() {
    syncLabels();
    const l = parseInt(lSlider.value, 10);
    const r = parseInt(rSlider.value, 10);

    queryBtn.disabled = true;
    queryBtn.innerHTML = `<span class="spinner"></span>Считаю…`;
    queryError.classList.add("hidden");

    try {
        const resp = await fetch(`/api/segment/query?l=${l}&r=${r}`);
        if (!resp.ok) {
            const body = await resp.json().catch(() => ({}));
            throw new Error(body.detail || `HTTP ${resp.status}`);
        }
        const data = await resp.json();
        queryResult.classList.remove("hidden");
        const matchBadge = data.matches
            ? `<span class="result-good">совпадает с naive</span>`
            : `<span class="result-bad">расхождение!</span>`;

        queryResult.innerHTML = `
            <dl class="kv">
                <dt>диапазон</dt><dd>[${data.l}, ${data.r}]</dd>
                <dt>даты</dt><dd>${data.date_from} → ${data.date_to}</dd>
                <dt>сумма (tree)</dt><dd>${fmtNum(data.tree_sum)}</dd>
                <dt>сумма (naive)</dt><dd>${fmtNum(data.naive_sum)}</dd>
                <dt>сверка</dt><dd>${matchBadge}</dd>
            </dl>
            <div class="metric-row">
                <div class="metric">
                    <span class="metric-label">Segment Tree</span>
                    <span class="metric-value">${fmtMs(data.tree_ms)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Naive</span>
                    <span class="metric-value">${fmtMs(data.naive_ms)}</span>
                </div>
            </div>
        `;
    } catch (e) {
        queryError.textContent = "Ошибка: " + e.message;
        queryError.classList.remove("hidden");
        queryResult.classList.add("hidden");
    } finally {
        queryBtn.disabled = false;
        queryBtn.textContent = "Посчитать";
    }
}

async function runUpdate(e) {
    e.preventDefault();
    const pos = parseInt(updatePos.value, 10);
    const value = parseFloat(updateValue.value);

    if (!Number.isInteger(pos) || pos < 0 || pos > MAX_IDX) {
        updateError.textContent = "pos должен быть в диапазоне 0..119999";
        updateError.classList.remove("hidden");
        return;
    }
    if (Number.isNaN(value) || value < 0) {
        updateError.textContent = "value должно быть неотрицательным числом";
        updateError.classList.remove("hidden");
        return;
    }

    updateSubmit.disabled = true;
    updateSubmit.innerHTML = `<span class="spinner"></span>Обновляю…`;
    updateError.classList.add("hidden");

    try {
        const resp = await fetch("/api/segment/update", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pos, value }),
        });
        if (!resp.ok) {
            const body = await resp.json().catch(() => ({}));
            throw new Error(body.detail || `HTTP ${resp.status}`);
        }
        const data = await resp.json();
        updateResult.classList.remove("hidden");
        updateResult.innerHTML = `
            <dl class="kv">
                <dt>позиция</dt><dd>${data.pos}</dd>
                <dt>было</dt><dd>${fmtNum(data.old_value)}</dd>
                <dt>стало</dt><dd>${fmtNum(data.new_value)}</dd>
                <dt>новое значение в точке</dt><dd>${fmtNum(data.new_sum)}</dd>
            </dl>
            <div class="metric-row">
                <div class="metric">
                    <span class="metric-label">Время update</span>
                    <span class="metric-value">${fmtMs(data.update_ms)}</span>
                </div>
            </div>
            <p class="muted">
                Дерево обновилось за O(log n). Теперь запрос по диапазону,
                включающему pos=${data.pos}, покажет новую сумму.
            </p>
        `;
    } catch (e) {
        updateError.textContent = "Ошибка: " + e.message;
        updateError.classList.remove("hidden");
        updateResult.classList.add("hidden");
    } finally {
        updateSubmit.disabled = false;
        updateSubmit.textContent = "Обновить";
    }
}

lSlider.addEventListener("input", syncLabels);
rSlider.addEventListener("input", syncLabels);
lSlider.addEventListener("change", runQuery);
rSlider.addEventListener("change", runQuery);
queryBtn.addEventListener("click", runQuery);
updateForm.addEventListener("submit", runUpdate);

const resetBtn = document.getElementById("reset-btn");
resetBtn.addEventListener("click", async () => {
    const pos = parseInt(updatePos.value, 10);
    if (!Number.isInteger(pos) || pos < 0 || pos > MAX_IDX) {
        updateError.textContent = "pos должен быть в диапазоне 0..119999";
        updateError.classList.remove("hidden");
        return;
    }

    resetBtn.disabled = true;
    resetBtn.innerHTML = `<span class="spinner"></span>Сбрасываю…`;
    updateError.classList.add("hidden");

    try {
        const resp = await fetch("/api/segment/reset", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pos }),
        });
        if (!resp.ok) {
            const body = await resp.json().catch(() => ({}));
            throw new Error(body.detail || `HTTP ${resp.status}`);
        }
        const data = await resp.json();
        updateResult.classList.remove("hidden");
        updateResult.innerHTML = `
            <dl class="kv">
                <dt>позиция</dt><dd>${data.pos}</dd>
                <dt>было</dt><dd>${fmtNum(data.old_value)}</dd>
                <dt>восстановлено</dt><dd>${fmtNum(data.new_value)}</dd>
            </dl>
            <div class="metric-row">
                <div class="metric">
                    <span class="metric-label">Время reset</span>
                    <span class="metric-value">${fmtMs(data.update_ms)}</span>
                </div>
            </div>
        `;
    } catch (e) {
        updateError.textContent = "Ошибка: " + e.message;
        updateError.classList.remove("hidden");
        updateResult.classList.add("hidden");
    } finally {
        resetBtn.disabled = false;
        resetBtn.textContent = "Сбросить pos к исходному значению";
    }
});

// первый запрос сразу при открытии
runQuery();