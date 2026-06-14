#!/usr/bin/env python3
"""
SkillGate + Chanlun-Pro 统一反向代理

运行在 :9900 → 对外暴露（Tailscale Funnel → :9900）
- /skillgate/* → http://127.0.0.1:9902 (SkillGate)
- /*           → http://127.0.0.1:9903 (Chanlun-Pro 原始服务)
"""
import sys
import io
from http.server import HTTPServer, BaseHTTPRequestHandler
from http.client import HTTPConnection
from urllib.error import URLError

BACKEND_SKILLGATE = ("127.0.0.1", 9902)
BACKEND_CHANLUN = ("127.0.0.1", 9903)
BACKEND_ASTOCK = ("127.0.0.1", 9901)


def proxy(method, target, path, headers, body):
    """转发请求到目标后端（使用 HTTPConnection 避免自动跟重定向）"""
    conn = HTTPConnection(target[0], target[1], timeout=30)
    try:
        conn.request(method, path, body=body, headers=headers)
        resp = conn.getresponse()
        status = resp.status
        resp_headers = dict(resp.getheaders())
        resp_body = resp.read()
        return status, resp_headers, resp_body
    except Exception as e:
        return 502, {}, str(e).encode()
    finally:
        conn.close()


class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")

    def do_PUT(self):
        self._handle("PUT")

    def do_DELETE(self):
        self._handle("DELETE")

    def do_HEAD(self):
        self._handle("GET")

    def do_OPTIONS(self):
        self._handle("OPTIONS")

    def _handle(self, method):
        path = self.path
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        # 兼容旧JS（浏览器未刷新的双前缀）
        if path.startswith("/api/v1/api/v1/"):
            path = path[len("/api/v1"):]
            target = BACKEND_ASTOCK
            # 路由规则
        elif path.startswith("/skillgate/c2c"):
            # C2C 前端 - FastAPI 挂载在 /skillgate/c2c，补末尾斜杠防 307 重定向
            target = BACKEND_SKILLGATE
            if not path.endswith("/") and "." not in path.split("/")[-1]:
                # 302 重定向到带斜杠版本
                self.send_response(302)
                self.send_header("Location", f"https://dogzi-ms-7d73.tailbc211b.ts.net{path}/")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                return
        elif path.startswith("/skillgate"):
            # SkillGate 根路径 - 剥离前缀到 :9902 根（显示 API 信息）
            target = BACKEND_SKILLGATE
            path = path[len("/skillgate"):] or "/"
        elif path.startswith("/admin"):
            # 运营端后台 → FastAPI :9902
            target = BACKEND_SKILLGATE
            if path == "/admin":
                self.send_response(302)
                self.send_header("Location", "https://dogzi-ms-7d73.tailbc211b.ts.net/admin/")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                return
        elif path.startswith("/c2c"):
            # /c2c → FastAPI C2C 前端（挂载在 /skillgate/c2c）
            target = BACKEND_SKILLGATE
            if not path.endswith("/") and "." not in path.split("/")[-1]:
                # 302 重定向到带斜杠版本
                self.send_response(302)
                self.send_header("Location", f"https://dogzi-ms-7d73.tailbc211b.ts.net{path}/")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                return
            rest = path[len("/c2c"):]
            path = f"/skillgate/c2c{rest}" if rest else "/skillgate/c2c"
        elif path == "/openapi.json":
            # SkillGate Swagger UI 需要加载 /openapi.json
            target = BACKEND_SKILLGATE
        elif path.startswith("/api/v1/kronos/"):
            # kronos 预测 → a-stock-analyst 后端 :8765
            target = ("127.0.0.1", 8765)
        elif path.startswith('/api/c2c/') or path.startswith('/api/demands/') or path.startswith('/api/services/'):
            # SkillGate 相关 API → :9902
            target = BACKEND_SKILLGATE
        elif path.startswith('/api/auth/'):
            # a-stock 登录/缓存 → FastAPI :9901
            target = BACKEND_ASTOCK
        elif path.startswith('/api/v1/') or path.startswith('/api/signals/') or path.startswith('/api/ai/') or path.startswith('/api/data/') or path.startswith('/uploads/'):
            # a-stock 相关 API → FastAPI :9901
            target = BACKEND_ASTOCK
        elif path.startswith("/tv/"):
            # TV 图表数据 → Chanlun-Chart Flask :9903
            target = BACKEND_CHANLUN
        elif path.startswith("/dashboard"):
            # Hermes Dashboard → :9119
            target = ("127.0.0.1", 9119)
            path = path[len("/dashboard"):] or "/"
        elif path.startswith("/big-buy-summary/") or path.startswith("/bigbuy/") or path.startswith("/big-deal-summary/"):
            # 资金流向/大单子图数据 → a-stock FastAPI :9901
            target = BACKEND_ASTOCK
        elif path.startswith("/api/"):
            # 其他 /api/ 路径 → SkillGate
            target = BACKEND_SKILLGATE
        else:
            target = BACKEND_CHANLUN

        # 转发头部（过滤掉 hop-by-hop 头部）
        headers = {k: v for k, v in self.headers.items()
                   if k.lower() not in ("host", "connection", "transfer-encoding")}

        status, resp_headers, resp_body = proxy(method, target, path, headers, body)

        # 重写 Location 头部：将内部地址转为外部域名
        if 300 <= status < 400:
            for k in list(resp_headers.keys()):
                if k.lower() == "location":
                    resp_headers[k] = resp_headers[k].replace(
                        "http://127.0.0.1:9902", "https://dogzi-ms-7d73.tailbc211b.ts.net"
                    ).replace(
                        "http://localhost:9902", "https://dogzi-ms-7d73.tailbc211b.ts.net"
                    )

        # 回写响应
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

        for k, v in resp_headers.items():
            if k.lower() not in ("transfer-encoding", "connection", "content-encoding"):
                self.send_header(k, v)
        self.end_headers()
        if resp_body:
            self.wfile.write(resp_body)

    def log_message(self, format, *args):
        try:
            print(f"[Proxy] {self.client_address[0]} - {' '.join(str(a) for a in args)}")
        except Exception:
            pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9900
    server = HTTPServer(("0.0.0.0", port), ProxyHandler)
    print(f"🚀 Reverse proxy running on :{port}")
    print(f"   /skillgate/* → :9902 (SkillGate)")
    print(f"   /*          → :9903 (Chanlun-Pro)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
