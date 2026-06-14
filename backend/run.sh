#!/usr/bin/env bash
# SkillGate 后端启动脚本
set -e
cd "$(dirname "$0")"
source .venv/bin/activate
exec uvicorn app.main:app --host 0.0.0.0 --port 9902 --reload
