// Загрузка датасета: 5 шагов, polling прогресса.

let uploadId = null;

const $ = (id) => document.getElementById(id);

function showError(step, msg) {
    const box = $(`error-${step}`);
    box.textContent = msg;
    box.classList.remove("hidden");
}

function hideError(step) {
    $(`error-${step}`).classList.add("hidden");
}

function showStep(n) {
    for (let i = 1; i <= 5; i++) {
        $(`step-${i}`).classList.toggle("hidden", i !== n);
    }
}

// ---------- Шаг 1: загрузка ----------
$("upload-btn").addEventListener("click", async () => {
    hideError(1);
    const file = $("file-input").files[0];
    if (!file) {
        showError(1, "Выберите CSV-файл");
        return;
    }

    const btn = $("upload-btn");
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span>Загружаю...`;

    try {
        const fd = new FormData();
        fd.append("file", file);

        const r = await fetch("/api/dataset/upload", { method: "POST", body: fd });
        const data = await r.json();
        if (!r.ok) throw new Error(data.detail || `HTTP ${r.status}`);

        uploadId = data.upload_id;
        $("rows-info").textContent = data.rows.toLocaleString("ru-RU");
        $("cols-info").textContent = data.columns.length;

        // заполнить dropdowns
        for (const id of ["field-unique", "field-order", "field-value", "field-source", "field-target"]) {
            const sel = $(id);
            sel.innerHTML = "";
            for (const col of data.columns) {
                const opt = document.createElement("option");
                opt.value = col;
                opt.textContent = col;
                sel.appendChild(opt);
            }
        }

        // дефолтные значения
        $("field-unique").value = data.columns[0] || "";
        $("field-order").value = data.columns[1] || "";
        $("field-value").value = data.columns[2] || "";
        $("field-source").value = data.columns[0] || "";
        $("field-target").value = data.columns[1] || "";

        showStep(2);
    } catch (e) {
        showError(1, e.message);
    } finally {
        btn.disabled = false;
        btn.textContent = "Загрузить";
    }
});

// ---------- Шаг 2: конфигурация ----------
$("configure-btn").addEventListener("click", async () => {
    hideError(2);

    const fields = {
        unique_id: $("field-unique").value,
        order: $("field-order").value,
        value: $("field-value").value,
        source: $("field-source").value,
        target: $("field-target").value,
    };

    const btn = $("configure-btn");
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span>Проверяю...`;

    try {
        const r = await fetch("/api/dataset/configure", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ upload_id: uploadId, fields }),
        });
        const data = await r.json();
        if (!r.ok) throw new Error(data.detail || `HTTP ${r.status}`);

        showStep(3);
    } catch (e) {
        showError(2, e.message);
    } finally {
        btn.disabled = false;
        btn.textContent = "Далее";
    }
});

// ---------- Шаг 3: выбор структур ----------
$("build-btn").addEventListener("click", async () => {
    hideError(3);

    const structures = [];
    if ($("s-hash").checked) structures.push("hash");
    if ($("s-segment").checked) structures.push("segment");
    if ($("s-graph").checked) structures.push("graph");

    if (structures.length === 0) {
        showError(3, "Выберите хотя бы одну структуру");
        return;
    }

    const btn = $("build-btn");
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span>Запускаю...`;

    try {
        const r = await fetch("/api/dataset/build", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ structures }),
        });
        const data = await r.json();
        if (!r.ok) throw new Error(data.detail || `HTTP ${r.status}`);

        showStep(4);
        pollBuild();
    } catch (e) {
        showError(3, e.message);
        btn.disabled = false;
        btn.textContent = "Построить";
    }
});

// ---------- Шаг 4: polling ----------
async function pollBuild() {
    while (true) {
        try {
            const r = await fetch("/api/dataset/build/status");
            const data = await r.json();

            const pct = Math.round(data.progress * 100);
            $("progress-fill").style.width = `${pct}%`;
            $("progress-text").textContent = `${pct}% — ${data.structures.join(", ")}`;

            if (data.status === "ready") {
                showStep(5);
                return;
            }
            if (data.status === "error") {
                showError(4, "Ошибка: " + data.error);
                $("build-btn").disabled = false;
                $("build-btn").textContent = "Построить";
                return;
            }
        } catch (e) {
            console.warn("poll error:", e);
        }
        await new Promise(r => setTimeout(r, 500));
    }
}

$("reset-btn")?.addEventListener("click", async () => {
    if (!confirm("Вернуть дефолтный датасет? Текущие индексы будут перестроены.")) return;

    const btn = $("reset-btn");
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span>Сбрасываю...`;

    try {
        const r = await fetch("/api/dataset/reset", { method: "POST" });
        const data = await r.json();
        if (!r.ok) throw new Error(data.detail || `HTTP ${r.status}`);
        alert(`Готово: ${data.rows} строк. Перехожу на главную.`);
        location.href = "/";
    } catch (e) {
        $("error-5").textContent = "Ошибка: " + e.message;
        $("error-5").classList.remove("hidden");
    } finally {
        btn.disabled = false;
        btn.textContent = "Сбросить к дефолту";
    }
});