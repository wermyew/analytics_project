// Демо поиска по order_id через /api/hash/search/{order_id}.
// Показывает найденную строку и сравнивает время hash vs linear.

const form = document.getElementById("hash-form");
const input = document.getElementById("order-id");
const submitBtn = document.getElementById("hash-submit");
const randomBtn = document.getElementById("hash-random");
const resultBox = document.getElementById("hash-result");
const errorBox = document.getElementById("hash-error");

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

function renderResult(data) {
    hideError();
    resultBox.classList.remove("hidden");

    const speedup = data.speedup ? data.speedup.toFixed(1) + "×" : "—";
    const found = data.found
        ? `<span class="result-good">найден</span>`
        : `<span class="result-bad">не найден</span>`;

    let rowHtml = "";
    if (data.row) {
        const r = data.row;
        rowHtml = `
            <dl class="kv">
                <dt>order_id</dt><dd>${r.order_id}</dd>
                <dt>user_id</dt><dd>${r.user_id}</dd>
                <dt>product_id</dt><dd>${r.product_id}</dd>
                <dt>category</dt><dd>${r.category}</dd>
                <dt>quantity</dt><dd>${r.quantity}</dd>
                <dt>price</dt><dd>${r.price.toFixed(2)}</dd>
                <dt>total</dt><dd>${r.total.toFixed(2)}</dd>
                <dt>created_at</dt><dd>${r.created_at}</dd>
                <dt>row_id (hash)</dt><dd>${data.hash_row_id}</dd>
                <dt>row_id (linear)</dt><dd>${data.linear_row_id}</dd>
            </dl>
        `;
    } else {
        rowHtml = `<p>Заказ с таким <code>order_id</code> в датасете не найден.</p>`;
    }

    resultBox.innerHTML = `
        <p>Статус: ${found}</p>
        ${rowHtml}
        <div class="metric-row">
            <div class="metric">
                <span class="metric-label">Hash lookup</span>
                <span class="metric-value">${fmtMs(data.hash_ms)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Linear search</span>
                <span class="metric-value">${fmtMs(data.linear_ms)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Ускорение</span>
                <span class="metric-value">${speedup}</span>
            </div>
        </div>
    `;
}

async function runSearch(orderId) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="spinner"></span>Ищу…`;
    try {
        const resp = await fetch(`/api/hash/search/${encodeURIComponent(orderId)}`);
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
        submitBtn.textContent = "Найти";
    }
}

form.addEventListener("submit", (e) => {
    e.preventDefault();
    const id = parseInt(input.value, 10);
    if (!id || id < 1) {
        showError("Введи положительное целое");
        return;
    }
    runSearch(id);
});

randomBtn.addEventListener("click", () => {
    const id = 1 + Math.floor(Math.random() * 120000);
    input.value = id;
    runSearch(id);
});

// первый запрос сразу при открытии страницы
runSearch(parseInt(input.value, 10));