// Bootstrap-анализ: медиана чека на покупателя.

const runBtn = document.getElementById("run-bootstrap");
const repeatsInput = document.getElementById("repeats");
const resultBox = document.getElementById("boot-result");
const errorBox = document.getElementById("boot-error");

function showError(msg) {
    errorBox.textContent = msg;
    errorBox.classList.remove("hidden");
    resultBox.classList.add("hidden");
}

function hideError() {
    errorBox.classList.add("hidden");
}

function fmtNum(v) {
    return Number(v).toLocaleString("ru-RU", { maximumFractionDigits: 2 });
}

runBtn.addEventListener("click", async () => {
    hideError();
    const repeats = parseInt(repeatsInput.value, 10) || 1000;

    // 1. Проверка на клиенте (до отправки на сервер)
    if (repeats < 100 || repeats > 10000) {
        showError("Количество ресемплов должно быть от 100 до 10000");
        return;
    }

    runBtn.disabled = true;
    runBtn.innerHTML = `<span class="spinner"></span>Считаю...`;

    try {
        const r = await fetch(`/api/bootstrap/interval?repeats=${repeats}`);
        const data = await r.json();

        if (!r.ok) {
            // 2. Красивая обработка ошибок FastAPI
            let errMsg = "Ошибка запроса";
            if (typeof data.detail === "string") {
                errMsg = data.detail;
            } else if (Array.isArray(data.detail)) {
                // Извлекаем сообщения из массива ошибок валидации Pydantic
                errMsg = data.detail.map(e => e.msg).join("; ");
            }
            throw new Error(errMsg);
        }

        // 3. Отрисовка результата
        resultBox.classList.remove("hidden");
        resultBox.innerHTML = `
            <dl class="kv">
                <dt>Покупателей в выборке</dt><dd>${data.units.toLocaleString("ru-RU")}</dd>
                <dt>Медиана</dt><dd><strong>${fmtNum(data.observed_median)}</strong></dd>
                <dt>Среднее (для сравнения)</dt><dd>${fmtNum(data.mean)}</dd>
                <dt>95% CI</dt><dd><strong>[${fmtNum(data.ci_low)}; ${fmtNum(data.ci_high)}]</strong></dd>
                <dt>Ресемплов</dt><dd>${data.repeats}</dd>
                <dt>Время</dt><dd>${data.elapsed_ms.toFixed(1)} ms</dd>
            </dl>
            <p class="muted" style="margin-top: 12px;">
                Медиана ${fmtNum(data.observed_median)} vs среднее ${fmtNum(data.mean)} —
                разница показывает, насколько в данных есть выбросы (крупные закупки).
            </p>
        `;
    } catch (e) {
        showError("Ошибка: " + e.message);
    } finally {
        runBtn.disabled = false;
        runBtn.textContent = "Запустить";
    }
});