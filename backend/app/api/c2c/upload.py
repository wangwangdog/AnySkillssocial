"""文件上传 API"""
import io
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from app.core.security import get_current_user
from app.models.user import User
from app.core.storage import upload_file, StorageFactory
from app.core.config import settings

router = APIRouter(prefix="/api/upload", tags=["上传"])


@router.post("/image")
def upload_image(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user)
):
    """上传图片（头像、服务图片、打卡照片等）"""
    try:
        # 读取文件内容
        contents = file.file.read()
        
        # 验证文件类型
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="仅支持图片文件")
        
        # 调用存储服务
        result = upload_file(
            file_bytes=contents,
            filename=file.filename or "upload.jpg",
            content_type=file.content_type
        )
        
        return {
            "success": True,
            "url": result.url,
            "filename": result.filename,
            "size": result.size
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败：{str(e)}")


@router.post("/video")
def upload_video(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user)
):
    """上传视频（技能展示视频）"""
    try:
        contents = file.file.read()
        
        if not file.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="仅支持视频文件")
        
        result = upload_file(
            file_bytes=contents,
            filename=file.filename or "upload.mp4",
            content_type=file.content_type
        )
        
        return {
            "success": True,
            "url": result.url,
            "filename": result.filename,
            "size": result.size
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败：{str(e)}")


@router.get("/config")
def get_storage_config():
    """获取存储配置（前端用）"""
    config = StorageFactory._config
    return {
        "mode": config.mode,
        "max_size_mb": config.max_size / 1024 / 1024,
        "allowed_types": [t.split(",")[-1] for t in config.allowed_types]
    }
