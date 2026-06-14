"""搜索 API - 全文检索"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from app.core.database import get_db
from app.models.user import User
from app.models.order import Service, Demand

router = APIRouter(prefix="/api/search", tags=["搜索"])


@router.get("/services")
def search_services(
    q: str = "",           # 关键词
    skill_type: str = "",  # 技能类型过滤
    price_min: float = 0,   # 价格范围
    price_max: float = 999999,
    city: str = "",        # 城市
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """搜索服务"""
    query = db.query(Service).filter(Service.is_active == True)
    
    # 全文搜索（标题、描述、技能类型）
    if q:
        search_pattern = f"%{q}%"
        query = query.filter(
            or_(
                Service.title.ilike(search_pattern),
                Service.description.ilike(search_pattern),
                Service.skill_type.ilike(search_pattern)
            )
        )
    
    # 过滤条件
    if skill_type:
        query = query.filter(Service.skill_type == skill_type)
    if city:
        query = query.join(User, Service.seller_id == User.id).filter(
            User.residence_city.ilike(f"%{city}%")
        )
    query = query.filter(
        Service.price >= price_min,
        Service.price <= price_max
    )
    
    # 排序：默认按价格升序，可加热门排序
    query = query.order_by(Service.created_at.desc())
    
    # 分页
    total = query.count()
    services = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "data": [{
            "id": s.id,
            "title": s.title,
            "description": (s.description or "")[:100],
            "price": s.price,
            "skill_type": s.skill_type,
            "seller": {
                "id": s.seller_id,
                "nickname": s.seller.nickname,
                "avatar": s.seller.avatar or "",
                "city": s.seller.residence_city or ""
            },
            "created_at": s.created_at.isoformat() if s.created_at else ""
        } for s in services]
    }


@router.get("/demands")
def search_demands(
    q: str = "",
    skill_type: str = "",
    budget_min: float = 0,
    budget_max: float = 999999,
    city: str = "",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """搜索需求"""
    query = db.query(Demand)
    
    if q:
        search_pattern = f"%{q}%"
        query = query.filter(
            or_(
                Demand.title.ilike(search_pattern),
                Demand.description.ilike(search_pattern),
                Demand.skill_type.ilike(search_pattern)
            )
        )
    
    if skill_type:
        query = query.filter(Demand.skill_type == skill_type)
    if city:
        query = query.join(User, Demand.creator_id == User.id).filter(
            User.residence_city.ilike(f"%{city}%")
        )
    query = query.filter(
        Demand.budget >= budget_min,
        Demand.budget <= budget_max
    )
    
    total = query.count()
    demands = query.order_by(Demand.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "data": [{
            "id": d.id,
            "title": d.title,
            "description": (d.description or "")[:100],
            "budget": d.budget,
            "skill_type": d.skill_type,
            "creator": {
                "id": d.creator_id,
                "nickname": d.creator.nickname,
                "avatar": d.creator.avatar or ""
            }
        } for d in demands]
    }


@router.get("/suggest")
def search_suggest(q: str = "", limit: int = 5, db: Session = Depends(get_db)):
    """搜索建议（自动补全）"""
    if not q:
        return {"suggestions": []}
    
    # 从服务和需求中提取热门关键词
    keywords = set()
    
    # 服务标题
    for s in db.query(Service.title).filter(Service.title.ilike(f"%{q}%")).limit(3).all():
        keywords.add(s.title)
    
    # 技能类型
    for st in db.query(Service.skill_type).filter(
        Service.skill_type.ilike(f"%{q}%"),
        Service.skill_type.isnot(None)
    ).distinct().limit(3).all():
        keywords.add(st.skill_type)
    
    return {"suggestions": list(keywords)[:limit]}
