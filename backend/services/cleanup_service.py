import logging
import os
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Any

from backend.db import SessionLocal
from backend.models import History

logger = logging.getLogger(__name__)

class CleanupService:
    def __init__(self, history_root_dir: str):
        self.history_root_dir = history_root_dir

    def cleanup_expired_records(self) -> Dict[str, Any]:
        """清理已过期的记录和文件"""
        db = SessionLocal()
        deleted_count = 0
        try:
            now = datetime.utcnow()
            logger.info(f"Checking for expired records before {now}")
            # 查找已过期的记录 (expires_at <= now)
            # 注意：expires_at 为空的记录不会过期
            expired_records = db.query(History).filter(History.expires_at <= now).all()
            
            for record in expired_records:
                task_id = record.task_id
                logger.info(f"Deleting expired record: {record.id}, task_id: {task_id}, title: {record.title}")
                
                # 删除数据库记录
                db.delete(record)
                
                # 删除文件系统
                if task_id:
                    task_dir = os.path.join(self.history_root_dir, task_id)
                    if os.path.exists(task_dir):
                        try:
                            shutil.rmtree(task_dir)
                            logger.info(f"Deleted directory: {task_dir}")
                        except Exception as e:
                            logger.error(f"Failed to delete directory {task_dir}: {e}")
                
                deleted_count += 1
                
            db.commit()
            return {"success": True, "deleted_count": deleted_count}
        except Exception as e:
            db.rollback()
            logger.error(f"Cleanup failed: {e}")
            return {"success": False, "error": str(e), "deleted_count": 0}
        finally:
            db.close()

    def get_expiring_soon(self, hours: int = 24) -> List[Dict]:
        """获取即将过期的记录"""
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            limit_time = now + timedelta(hours=hours)
            
            # 查找 expires_at 在未来24小时内的
            records = db.query(History).filter(
                History.expires_at > now,
                History.expires_at <= limit_time
            ).all()
            
            result = []
            for r in records:
                remaining = (r.expires_at - now).total_seconds() / 3600 # hours
                result.append({
                    "id": r.id,
                    "title": r.title,
                    "remaining_hours": round(remaining, 1),
                    "expires_at": r.expires_at.isoformat()
                })
            return result
        finally:
            db.close()

def get_cleanup_service() -> CleanupService:
    from backend.config import Config
    return CleanupService(Config.get_history_dir())
