# Rate Limiter v2

FastAPI asosida yozilgan rate limiting xizmati. Loyiha Redis yordamida so'rovlarni cheklaydi, PostgreSQL orqali dinamik qoidalarni saqlaydi va APScheduler bilan qoidalarni periodik yangilashni qo'llab-quvvatlaydi.

## Asosiy imkoniyatlar
- Bir nechta algoritm: `fixed_window`, `sliding_window_log`, `token_bucket`, `leaky_bucket`
- Middleware darajasida IP yoki user bo'yicha cheklash
- PostgreSQL'da rate limit qoidalarini CRUD qilish
- Redis'da tezkor hisoblash va qoidalarni cache qilish
- Docker Compose orqali tez ishga tushirish

## Texnologiyalar
- Python 3.11
- FastAPI
- Redis
- PostgreSQL 15
- SQLAlchemy (async)
- Alembic
- APScheduler

## Loyiha tuzilmasi
```text
app/
  api/                # Routerlar va endpointlar
  core/               # Config, middleware, lifespan
  db/                 # SQLAlchemy base, session, migrations, models
  repositories/       # Redis va DB repositorylari
  services/           # Rate limiter service va algorithm factory
  workers/            # Scheduler va background tasklar
docker/
  dev/Dockerfile
docker-compose.yml
```

## Talablar
- Docker va Docker Compose (tavsiya etiladi)
- Yoki lokal ishga tushirish uchun:
  - Python 3.11+
  - Redis
  - PostgreSQL

## 1) Docker orqali ishga tushirish
1. `.env` faylini tekshiring (`.env` loyihada bor).
2. Servislarni ko'taring:

```bash
docker compose up --build
```

3. API manzili:
- `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

## 2) Lokal ishga tushirish
1. Virtual muhit:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Kutubxonalar:

```bash
pip install -r requirements.txt
```

3. Redis va PostgreSQL'ni alohida ishga tushiring, keyin:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Migratsiyalar (Alembic)
Mavjud migration: `app/db/migrations/versions/1fb5d55e549a_first_table_added.py`

Qo'llash:
```bash
alembic upgrade head
```

Yangi migration yaratish:
```bash
alembic revision --autogenerate -m "your_message"
alembic upgrade head
```

## Muhim ENV o'zgaruvchilar
`.env`dagi asosiy sozlamalar:
- `DATABASE_URL=postgresql+asyncpg://...`
- `REDIS_DSN=redis://redis:6379/0`
- `RATE_LIMIT_ALGORITHM=sliding_window_log`
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`

## Endpointlar
### Health check
- `GET /health`

### Demo endpointlar (`/api/v1`)
- `GET /api/v1/posts`
- `GET /api/v1/users`
- `POST /api/v1/login`
- `GET /api/v1/rate-limited-endpoint`

### Rate limit qoidalari CRUD
- `POST /rate-limit/`
- `GET /rate-limit/`
- `GET /rate-limit/{rule_id}`
- `PUT /rate-limit/{rule_id}`

`POST /rate-limit/` uchun misol:
```json
{
  "path": "/api/v1/posts",
  "method": "GET",
  "algorithm": "fixed_window",
  "limit": 10,
  "window_seconds": 60,
  "key_type": "ip",
  "is_active": true,
  "priority": 10
}
```

## Rate limiting qanday ishlaydi
- Middleware har bir request uchun kalit yaratadi:
  - `rate_limit:user:{user_id}` yoki
  - `rate_limit:ip:{client_ip}`
- Tanlangan algoritm asosida Redis'da hisob-kitob qilinadi.
- Limit oshsa `429 Too Many Requests` va `Retry-After` header qaytadi.

## Scheduler
`app/workers/scheduler.py` har 1 daqiqada aktiv qoidalarni DB'dan olib Redis'ga yozish uchun job ishga tushiradi.

## Foydali buyruqlar
Format:
```bash
black .
```

Lint:
```bash
ruff check .
```

Test:
```bash
pytest
```
