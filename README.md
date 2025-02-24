alembic revision --autogenerate -m "Update tables"

alembic upgrade head

alembic revision -m "Add repairs"