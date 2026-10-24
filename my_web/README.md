# ds_learning_site

**ds** = **d**ata **s**tructures (не Data Science).
Учебный сайт-визуализатор хеш-таблицы и дерева отрезков
на синтетическом датасете заказов маркетплейса.

## Что внутри

- **Hash Map** — хеш-таблица с разрешением коллизий методом цепочек.
  Ключ — `order_id`, значение — `row_id`. Поиск O(1) в среднем.
- **Segment Tree** — дерево отрезков над массивом `total`, упорядоченным
  по `created_at`. Query и update за O(log n).
- Демо-страницы с живыми замерами и бенчмарками.

## Стек

FastAPI + Jinja2 + pandas/numpy. Индексы строятся один раз при старте
и живут в памяти всё время работы сервера.

## Установка

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt