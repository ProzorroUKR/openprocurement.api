# openprocurement.api — Agent Instructions

## Структура проекту

Репозиторій містить **два паралельних підпроекти** з однаковою бізнес-логікою:

| Підпроект | Пакет | Стек | Призначення |
|-----------|-------|------|-------------|
| Синхронний (основний) | `openprocurement` | Pyramid + pymongo | Продакшн API, повна функціональність |
| Асинхронний (новий) | `prozorro_cdb` | aiohttp + motor | Новий асинхронний API, розробляється паралельно |

### Ключові дзеркальні файли

| Синхронний | Асинхронний |
|------------|-------------|
| `src/openprocurement/api/database.py` | `src/prozorro_cdb/api/database/store.py` |
| `src/openprocurement/conftest.py` | `src/prozorro_cdb/conftest.py` *(поки відсутній)* |

## Правило: глобальні зміни вносяться в обидва підпроекти

Якщо зміна стосується інфраструктурного рівня (БД, фід, auth, middleware тощо) — її треба вносити **одночасно** в обидва підпроекти.

**Приклади глобальних змін:**
- логіка `list()` / фід (watermark, фільтри, сортування)
- `save_data()` / `get()` / `delete()`
- індекси колекцій (`get_indexes`)
- обробка `_rev`, `is_public`, `is_test`, `public_modified`
- конфігурація через env-змінні

**Як перевіряти:** після внесення змін у синхронний пакет — пошукати аналогічне місце в `prozorro_cdb` і застосувати ту ж логіку (з урахуванням `async/await` і motor замість pymongo).

## Документація по структурі підпроектів

Детальний опис файлів, шарів і правил розміщення коду — в окремих RST-документах:

- [Синхронний підпроект `openprocurement`](docs/source/developers/projects/cdb/structure/openprocurement.rst)
- [Асинхронний підпроект `prozorro_cdb`](docs/source/developers/projects/cdb/structure/prozorro_cdb.rst)

## Тести

- Тести синхронного пакету живуть у `src/openprocurement/**/tests/`
- Фікстури pytest — `src/openprocurement/conftest.py` (autouse, покриває весь `openprocurement`)
- Тестів для `prozorro_cdb` поки немає; при появі — додати `src/prozorro_cdb/conftest.py` з аналогічними фікстурами

### Важлива фікстура: `disable_feed_watermark`

`FEED_WATERMARK_SECONDS` (default: 5) затримує видачу свіжих документів у фіді, щоб уникнути race condition при паралельних записах (детально: `docs/source/developers/projects/cdb/feed_ordering.rst`).

У тестах це призводить до того, що щойно створені об'єкти не видно у фіді. Тому в `conftest.py` є autouse-фікстура що обнуляє watermark:

```python
@pytest.fixture(autouse=True)
def disable_feed_watermark(monkeypatch):
    import openprocurement.api.database as db_module
    monkeypatch.setattr(db_module, "FEED_WATERMARK_SECONDS", 0)
```
