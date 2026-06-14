"""支付与充值 API（集成微信支付）"""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import hashlib
import hmac
import time
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, CashFlow
from app.core.wxpay import wxpay

router = APIRouter(prefix="/api/payment", tags=["支付"])


class RechargeRequest(BaseModel):
    amount: float


@router.post("/recharge")
async def recharge(
    req: RechargeRequest, 
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """充值（创建微信支付订单）"""
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="金额必须大于 0")
    if req.amount > 50000:
        raise HTTPException(status_code=400, detail="单次充值不能超过 50000")

    # 生成订单号：时间戳 + 用户 ID + 随机数
    order_no = f"{int(time.time()*1000)}{user.id}{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}"
    
    # 创建微信支付订单
    wxpay_result = wxpay.create_order(
        user_id=user.id,
        amount=req.amount,
        order_no=order_no,
        description=f"SkillGate 充值-{req.amount}元"
    )
    
    if not wxpay_result.get("success"):
        raise HTTPException(status_code=500, detail=wxpay_result.get("message", "支付接口调用失败"))
    
    return {
        "status": "pending",  # 等待支付
        "order_no": order_no,
        "amount": req.amount,
        "qr_url": wxpay_result.get("qr_url"),  # 二维码 URL
        "message": "请扫描二维码完成支付"
    }


@router.post("/notify")
async def payment_notify(request: Request, db: Session = Depends(get_db)):
    """微信支付回调"""
    try:
        # 解析请求（微信 POST 数据为 XML 格式）
        body = await request.body()
        
        # 验证签名（简化版，实际应完整验证）
        sign = hashlib.md5(body).hexdigest()
        
        # 解析订单信息（模拟）
        import xml.etree.ElementTree as ET
        root = ET.fromstring(body)
        out_trade_no = root.find("out_trade_no").text
        total_fee = int(root.find("total_fee").text) / 100  # 转换为元
        
        # 查找订单（实际应从数据库查询）
        # 这里简化处理：直接增加余额
        user = db.query(User).filter(User.phone == "13800000000").first()  # 模拟
        if user:
            user.cash_balance = (user.cash_balance or 0) + total_fee
            
            # 记录流水
            flow = CashFlow(
                user_id=user.id,
                amount=total_fee,
                flow_type="recharge",
                status="completed",
                remark=f"微信充值-{out_trade_no}",
            )
            db.add(flow)
            db.commit()
        
        # 返回微信成功标识
        return {
            "return_code": "SUCCESS",
            "return_msg": "OK"
        }
        
    except Exception as e:
        return {
            "return_code": "FAIL",
            "return_msg": str(e)
        }


@router.get("/balance")
async def get_balance(user: User = Depends(get_current_user)):
    """查询余额"""
    return {
        "cash_balance": user.cash_balance or 0,
        "points_balance": user.points_balance or 0
    }
