# Modular Monolith Feature Modules

Every backend feature module lives under `app/modules/<name>/` with its own standard components:
- `models.py`: SQLAlchemy database models
- `schemas.py`: Pydantic request/response schemas
- `service.py`: Business logic & database operations
- `router.py`: FastAPI endpoint route definitions

Example module structure:
```text
app/modules/example/
├── __init__.py
├── models.py
├── schemas.py
├── service.py
└── router.py
```
