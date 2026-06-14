"""SkillGate - 娱乐技能变现平台

架构：
- C2C 端：服务提供者/需求者的双向客户端
- 运营端：系统管理员后台
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# 数据库初始化
from app.core.database import engine, Base
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动/关闭生命周期"""
    print("🚀 SkillGate 启动中...")
    print(f"📁 项目根目录：{project_root}")
    yield
    print("👋 SkillGate 关闭")


app = FastAPI(
    title="SkillGate",
    description="娱乐技能变现平台（C2C + 运营端）",
    version="2.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== C2C 端路由 ====================
from app.api.c2c import (
    auth, demands, services, orders, checkin, users,
    messages, community, favorites, payment, recommend,
    upload, chat, slot, search, coupon
)

# C2C 端路由（已有 /api 前缀，直接挂载）
app.include_router(auth.router, tags=["C2C-认证"])
app.include_router(demands.router, tags=["C2C-需求"])
app.include_router(services.router, tags=["C2C-服务"])
app.include_router(orders.router, tags=["C2C-订单"])
app.include_router(checkin.router, tags=["C2C-签到"])
app.include_router(users.router, tags=["C2C-用户"])
app.include_router(messages.router, tags=["C2C-消息"])
app.include_router(community.router, tags=["C2C-社区"])
app.include_router(favorites.router, tags=["C2C-收藏"])
app.include_router(chat.router, tags=["C2C-聊天"])
app.include_router(payment.router, tags=["C2C-支付"])
app.include_router(coupon.router, tags=["C2C-优惠券"])
app.include_router(recommend.router, tags=["C2C-推荐"])
app.include_router(upload.router, tags=["C2C-上传"])
app.include_router(slot.router, tags=["C2C-预约"])
app.include_router(search.router, tags=["C2C-搜索"])


# ==================== 运营端路由 ====================
from app.api.admin import admin

# 运营端路由（已有 /api/admin 前缀）
app.include_router(admin.router, tags=["运营 - 管理"])


# ==================== 静态文件 ====================
# C2C 端前端（注意：frontend 在 project_root 的上级目录）
frontend_path = project_root.parent / "frontend" / "dist"
if frontend_path.exists():
    app.mount("/skillgate/c2c", StaticFiles(directory=str(frontend_path), html=True), name="c2c-static")

# 运营端前端（注意：admin-frontend 在 project_root 的上级目录）
admin_frontend_path = project_root.parent / "admin-frontend" / "dist"
if admin_frontend_path.exists():
    app.mount("/admin", StaticFiles(directory=str(admin_frontend_path), html=True), name="admin-static")

# 上传文件
uploads_path = project_root / "uploads"
if uploads_path.exists():
    app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")


@app.get("/")
def root():
    """根路径"""
    return {
        "message": "SkillGate API",
        "version": "2.0.0",
        "endpoints": {
            "c2c": {
                "api": "https://your-domain.com/api/c2c/docs",
                "frontend": "https://your-domain.com/c2c",
                "description": "C2C 端（服务提供者/需求者）"
            },
            "admin": {
                "api": "https://your-domain.com/api/admin/docs",
                "frontend": "https://your-domain.com/admin",
                "description": "运营端（系统管理员）"
            }
        }
    }


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": "now"}
