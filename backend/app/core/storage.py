"""图片存储服务 - 支持本地和阿里云 OSS 双模式"""
import os
import uuid
from pathlib import Path
from typing import Optional, Union
from pydantic import BaseModel


class UploadResult(BaseModel):
    url: str
    filename: str
    size: int
    content_type: str
    path: str  # 本地路径或 OSS 键


class StorageConfig:
    def __init__(self):
        # 从环境变量读取配置
        self.mode = os.getenv("STORAGE_MODE", "local").lower()  # local 或 oss
        
        # 本地配置
        self.local_upload_dir = os.getenv("UPLOAD_DIR", "/home/dogzi/.openclaw/workspace/skillgate/backend/uploads")
        self.local_url_prefix = os.getenv("LOCAL_URL_PREFIX", "/uploads")
        
        # OSS 配置（阿里云）
        self.oss_endpoint = os.getenv("OSS_ENDPOINT", "oss-cn-hangzhou.aliyuncs.com")
        self.oss_access_key_id = os.getenv("OSS_ACCESS_KEY_ID", "")
        self.oss_access_key_secret = os.getenv("OSS_ACCESS_KEY_SECRET", "")
        self.oss_bucket_name = os.getenv("OSS_BUCKET_NAME", "")
        self.oss_url_prefix = os.getenv("OSS_URL_PREFIX", f"https://{self.oss_bucket_name}.{self.oss_endpoint}")
        
        # 允许的文件类型
        self.allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp", "video/mp4"]
        self.max_size = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB 默认
        
        # 确保目录存在
        if self.mode == "local":
            Path(self.local_upload_dir).mkdir(parents=True, exist_ok=True)


class StorageProvider:
    """存储抽象基类"""
    def upload(self, file_bytes: bytes, original_filename: str, content_type: str) -> UploadResult:
        raise NotImplementedError
    
    def delete(self, path: str) -> bool:
        raise NotImplementedError


class LocalStorageProvider(StorageProvider):
    """本地存储实现"""
    def __init__(self, config: StorageConfig):
        self.config = config
    
    def upload(self, file_bytes: bytes, original_filename: str, content_type: str) -> UploadResult:
        if content_type not in self.config.allowed_types:
            raise ValueError(f"不支持的文件类型：{content_type}")
        
        if len(file_bytes) > self.config.max_size:
            raise ValueError(f"文件大小超过限制：{len(file_bytes)} > {self.config.max_size}")
        
        # 生成唯一文件名
        ext = os.path.splitext(original_filename)[1] or ".jpg"
        unique_name = f"{uuid.uuid4().hex}{ext}"
        
        # 按日期分目录
        from datetime import datetime
        date_dir = datetime.now().strftime("%Y/%m/%d")
        file_path = os.path.join(self.config.local_upload_dir, date_dir, unique_name)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        
        # 构建 URL
        url_path = f"{date_dir}/{unique_name}"
        url = f"{self.config.local_url_prefix}/{url_path}"
        
        return UploadResult(
            url=url,
            filename=original_filename,
            size=len(file_bytes),
            content_type=content_type,
            path=file_path
        )
    
    def delete(self, path: str) -> bool:
        try:
            if os.path.exists(path):
                os.remove(path)
                return True
        except Exception as e:
            print(f"删除文件失败：{e}")
        return False


class OSSStorageProvider(StorageProvider):
    """阿里云 OSS 存储实现"""
    def __init__(self, config: StorageConfig):
        self.config = config
        self.client = None
        self._init_client()
    
    def _init_client(self):
        try:
            from oss2 import Auth, Bucket
            if not self.config.oss_access_key_id or not self.config.oss_access_key_secret:
                raise ValueError("OSS 配置不完整，请设置 OSS_ACCESS_KEY_ID 和 OSS_ACCESS_KEY_SECRET")
            auth = Auth(self.config.oss_access_key_id, self.config.oss_access_key_secret)
            self.client = Bucket(auth, self.config.oss_endpoint, self.config.oss_bucket_name)
        except ImportError:
            raise ImportError("需要安装 oss2: pip install oss2")
        except Exception as e:
            print(f"OSS 初始化失败：{e}")
            self.client = None
    
    def upload(self, file_bytes: bytes, original_filename: str, content_type: str) -> UploadResult:
        if not self.client:
            raise RuntimeError("OSS 未正确初始化")
        
        if content_type not in self.config.allowed_types:
            raise ValueError(f"不支持的文件类型：{content_type}")
        
        if len(file_bytes) > self.config.max_size:
            raise ValueError(f"文件大小超过限制")
        
        # 生成 OSS 键
        ext = os.path.splitext(original_filename)[1] or ".jpg"
        from datetime import datetime
        date_path = datetime.now().strftime("%Y/%m/%d")
        oss_key = f"uploads/{date_path}/{uuid.uuid4().hex}{ext}"
        
        # 上传到 OSS
        self.client.put_object(oss_key, file_bytes)
        
        # 生成 URL
        url = f"{self.config.oss_url_prefix}/{oss_key}"
        
        return UploadResult(
            url=url,
            filename=original_filename,
            size=len(file_bytes),
            content_type=content_type,
            path=oss_key
        )
    
    def delete(self, path: str) -> bool:
        if not self.client:
            return False
        try:
            self.client.delete_object(path)
            return True
        except Exception as e:
            print(f"OSS 删除失败：{e}")
            return False


# 单例
class StorageFactory:
    _instance: Optional[StorageProvider] = None
    _config: Optional[StorageConfig] = None
    
    @classmethod
    def get_storage(cls) -> StorageProvider:
        if cls._instance is None:
            cls._config = StorageConfig()
            if cls._config.mode == "oss":
                cls._instance = OSSStorageProvider(cls._config)
            else:
                cls._instance = LocalStorageProvider(cls._config)
        return cls._instance


# 便捷函数
def upload_file(file_bytes: bytes, filename: str, content_type: str) -> UploadResult:
    """上传文件"""
    return StorageFactory.get_storage().upload(file_bytes, filename, content_type)

def delete_file(path: str) -> bool:
    """删除文件"""
    return StorageFactory.get_storage().delete(path)
