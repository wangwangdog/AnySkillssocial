"""微信支付集成"""
import hashlib
import hmac
import time
import requests
import base64
import os
from typing import Optional, Dict, Any

class WeChatPay:
    """微信支付（沙箱环境）"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            # 沙箱环境配置（生产环境需替换）
            "mch_id": os.getenv("WXPAY_MCH_ID", "sandbox_merchant_id"),
            "api_key": os.getenv("WXPAY_API_KEY", "sandbox_api_key"),
            "app_id": os.getenv("WXPAY_APP_ID", "sandbox_app_id"),
            "notify_url": os.getenv("WXPAY_NOTIFY_URL", "http://localhost:9902/api/payment/notify"),
            "sandbox": True
        }
        
        # 微信支付 API 端点
        self.sandbox_url = "https://api.mch.weixin.qq.com/sandboxnew/pay/unifiedorder"
        self.prod_url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        
    def _generate_sign(self, params: Dict[str, Any]) -> str:
        """生成签名"""
        # 移除空值
        params = {k: v for k, v in params.items() if v is not None and v != ""}
        
        # 排序
        sorted_params = sorted(params.items())
        
        # 拼接
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
        sign_str += f"&key={self.config['api_key']}"
        
        # MD5 签名
        return hashlib.md5(sign_str.encode("utf-8")).hexdigest().upper()
    
    def create_order(self, 
                    user_id: int, 
                    amount: float, 
                    order_no: str,
                    description: str = "SkillGate 充值") -> Dict[str, Any]:
        """创建微信支付订单"""
        
        # 构建参数
        params = {
            "appid": self.config["app_id"],
            "mch_id": self.config["mch_id"],
            "nonce_str": self._generate_nonce(),
            "body": description,
            "detail": f"用户{user_id}充值",
            "out_trade_no": order_no,
            "fee_type": "CNY",
            "total_fee": int(amount * 100),  # 分
            "spbill_create_ip": "127.0.0.1",  # 实际应使用用户 IP
            "notify_url": self.config["notify_url"],
            "trade_type": "NATIVE"  # Native 支付（扫码支付），移动端可用 JSAPI
        }
        
        # 生成签名
        params["sign"] = self._generate_sign(params)
        
        # 请求微信（沙箱模式仅模拟）
        if self.config.get("sandbox"):
            # 沙箱模式：直接返回模拟的支付参数
            return {
                "success": True,
                "payment_code": f"sandbox_qr_{order_no}",
                "qr_url": f"weixin://wxpay/bizpayurl?pr={base64.b64encode(order_no.encode()).decode()}",
                "message": "沙箱模式：模拟支付成功"
            }
        
        # 生产环境
        url = self.prod_url
        try:
            response = requests.post(url, json=params, timeout=10)
            result = response.json()
            
            if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
                return {
                    "success": True,
                    "payment_code": result.get("code_url"),
                    "qr_url": result.get("code_url"),
                    "message": "支付订单创建成功"
                }
            else:
                return {
                    "success": False,
                    "message": result.get("return_msg", "支付失败"),
                    "error_code": result.get("err_code")
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"请求失败：{str(e)}"
            }
    
    def query_order(self, order_no: str) -> Dict[str, Any]:
        """查询订单状态"""
        if self.config.get("sandbox"):
            return {
                "success": True,
                "trade_state": "SUCCESS",
                "message": "沙箱模式：订单成功"
            }
        
        url = "https://api.mch.weixin.qq.com/pay/orderquery"
        params = {
            "appid": self.config["app_id"],
            "mch_id": self.config["mch_id"],
            "nonce_str": self._generate_nonce(),
            "out_trade_no": order_no
        }
        params["sign"] = self._generate_sign(params)
        
        try:
            response = requests.post(url, json=params, timeout=10)
            return response.json()
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def _generate_nonce(self) -> str:
        """生成随机字符串"""
        return f"{time.time()}_{os.urandom(8).hex()}"


# 实例化
wxpay = WeChatPay()
