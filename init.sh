#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

case "${1:-help}" in
  up)
    echo "==> Docker Compose 起動"
    docker compose -f "$ROOT/docker-compose.yml" up --build -d
    echo "Frontend: http://localhost:3000"
    echo "Backend:  http://localhost:8000/docs"
    ;;
  down)
    docker compose -f "$ROOT/docker-compose.yml" down
    ;;
  logs)
    docker compose -f "$ROOT/docker-compose.yml" logs -f "${2:-}"
    ;;
  migrate)
    echo "==> Alembic migrate"
    docker compose -f "$ROOT/docker-compose.yml" exec backend alembic upgrade head
    ;;
  seed)
    echo "==> Seed データ投入"
    docker compose -f "$ROOT/docker-compose.yml" exec backend python -m app.db.seed
    ;;
  test)
    echo "==> バックエンドテスト"
    docker compose -f "$ROOT/docker-compose.yml" exec backend pytest -v
    ;;
  shell-be)
    docker compose -f "$ROOT/docker-compose.yml" exec backend bash
    ;;
  shell-fe)
    docker compose -f "$ROOT/docker-compose.yml" exec frontend sh
    ;;
  psql)
    docker compose -f "$ROOT/docker-compose.yml" exec db psql -U ikesu -d ikesu_log
    ;;
  reset-db)
    echo "警告: DBを完全リセットします。続行しますか? [y/N]"
    read -r ans
    if [ "$ans" = "y" ]; then
      docker compose -f "$ROOT/docker-compose.yml" exec backend alembic downgrade base
      docker compose -f "$ROOT/docker-compose.yml" exec backend alembic upgrade head
      docker compose -f "$ROOT/docker-compose.yml" exec backend python -m app.db.seed
    fi
    ;;
  *)
    echo "Usage: $0 {up|down|logs|migrate|seed|test|shell-be|shell-fe|psql|reset-db}"
    ;;
esac
