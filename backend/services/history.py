import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import desc
from backend.db import SessionLocal
from backend.models import History, Image

logger = logging.getLogger(__name__)

class HistoryService:
    def _extract_keyword(self, title: str) -> str:
        """从标题提取关键词（中文/英文/数字）"""
        import re
        clean = re.sub(r'[^\w\u4e00-\u9fff]', '', title)
        return clean[:10] if clean else "task"

    def create_record(
        self,
        user_id: int,
        topic: str,
        outline: Dict,
        task_id: Optional[str] = None
    ) -> str:
        db = SessionLocal()
        try:
            record_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            images_data = {"task_id": task_id, "generated": []} if task_id else None
            keyword = self._extract_keyword(topic)
            
            history = History(
                id=record_id,
                user_id=user_id,
                title=topic,
                outline=json.dumps(outline, ensure_ascii=False),
                status="draft",
                task_id=task_id,
                page_count=len(outline.get("pages", [])),
                created_at=now,
                updated_at=now,
                images_json=json.dumps(images_data) if images_data else None,
                expires_at=now + timedelta(days=7),
                keyword=keyword
            )
            db.add(history)
            db.commit()
            return record_id
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def start_expiry(self, record_id: str) -> bool:
        """开始倒计时（首次生成图片时调用）"""
        db = SessionLocal()
        try:
            record = db.query(History).filter(History.id == record_id).first()
            if record and not record.expires_at:
                from datetime import timedelta
                record.expires_at = datetime.utcnow() + timedelta(days=7)
                db.commit()
                return True
            return False
        finally:
            db.close()



    def get_record(self, record_id: str, user_id: Optional[int] = None) -> Optional[Dict]:
        """
        获取记录详情。如果提供了 user_id，则检查所属权。
        """
        db = SessionLocal()
        try:
            query = db.query(History).filter(History.id == record_id)
            if user_id is not None:
                query = query.filter(History.user_id == user_id)
                
            record = query.first()
            if not record:
                return None
                
            return self._record_to_dict(record, full=True)
        finally:
            db.close()

    def get_record_by_task_id(self, task_id: str) -> Optional[Any]:
        """通过 task_id 获取记录对象 (返回 ORM 对象)"""
        db = SessionLocal()
        try:
            return db.query(History).filter(History.task_id == task_id).first()
        finally:
            db.close()

    def update_record(
        self,
        record_id: str,
        user_id: Optional[int] = None,
        outline: Optional[Dict] = None,
        images: Optional[Dict] = None,
        status: Optional[str] = None,
        thumbnail: Optional[str] = None
    ) -> bool:
        db = SessionLocal()
        try:
            query = db.query(History).filter(History.id == record_id)
            if user_id is not None:
                query = query.filter(History.user_id == user_id)
                
            record = query.first()
            if not record:
                return False

            now = datetime.utcnow()
            record.updated_at = now

            if outline is not None:
                record.outline = json.dumps(outline, ensure_ascii=False)
                record.page_count = len(outline.get("pages", []))

            if images is not None:
                record.images_json = json.dumps(images)
                if images.get("task_id"):
                    record.task_id = images.get("task_id")

            if status is not None:
                record.status = status

            if thumbnail is not None:
                record.thumbnail = thumbnail
                
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()

    def delete_record(self, record_id: str, user_id: Optional[int] = None) -> bool:
        db = SessionLocal()
        try:
            query = db.query(History).filter(History.id == record_id)
            if user_id is not None:
                query = query.filter(History.user_id == user_id)
            
            record = query.first()
            if not record:
                return False

            # 删除关联的图片 (Image Table)
            # 是否要物理删除？Image 表通常存 Blob。我们这里先只删记录。
            # 如果 task_id存在，且没有其他记录引用它（通常是一对一）。
            if record.task_id:
                db.query(Image).filter(Image.task_id == record.task_id).delete()

            db.delete(record)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def list_records(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None
    ) -> Dict:
        db = SessionLocal()
        try:
            query = db.query(History).filter(History.user_id == user_id)
            if status:
                query = query.filter(History.status == status)
            
            total = query.count()
            records = query.order_by(desc(History.updated_at)).offset((page - 1) * page_size).limit(page_size).all()
            
            result_list = [self._record_to_dict(r, full=False) for r in records]
                
            return {
                "records": result_list,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 1
            }
        finally:
            db.close()

    def search_records(self, user_id: int, keyword: str) -> List[Dict]:
        db = SessionLocal()
        try:
            records = db.query(History).filter(
                History.user_id == user_id,
                History.title.ilike(f"%{keyword}%")
            ).order_by(desc(History.updated_at)).limit(50).all()
            
            return [self._record_to_dict(r, full=False) for r in records]
        finally:
            db.close()

    def get_statistics(self, user_id: int) -> Dict:
        db = SessionLocal()
        try:
            total = db.query(History).filter(History.user_id == user_id).count()
            
            status_counts = {}
            # Group by status
            from sqlalchemy import func
            rows = db.query(History.status, func.count(History.status)).filter(History.user_id == user_id).group_by(History.status).all()
            for status, count in rows:
                status_counts[status] = count
                
            return {
                "total": total,
                "by_status": status_counts
            }
        finally:
            db.close()

    def scan_and_sync_task_images(self, task_id: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        根据 task_id 查询 Image 表，并更新 History 表
        """
        db = SessionLocal()
        try:
            query = db.query(History).filter(History.task_id == task_id)
            if user_id:
                query = query.filter(History.user_id == user_id)
            
            record = query.first()
            
            # 即使没有记录，也可以返回 Image 表的信息，但无法更新记录
            images = db.query(Image).filter(Image.task_id == task_id).order_by(Image.index).all()
            image_files = [img.filename for img in images]
            
            if record:
                # 更新记录
                try:
                    outline_data = json.loads(record.outline)
                    expected_count = len(outline_data.get("pages", []))
                except:
                    expected_count = 0
                
                # 重新按索引排列文件名 (空缺位置留 None? 不，这里只负责文件名列表)
                # 实际上前端目前接收的是 dense array，但在 syncHistory 中处理了 sparse array。
                # 后端存储 images_json 还是简单存储 generated list 就可以。
                # generated 列表应该尽可能和 outline 对应？
                # 如果我们使用 {keyword}{index}.png，那么 filename 本身就包含 index 信息。
                # 这里我们还是存一个列表吧，顺序并不重要，因为 filename 包含 index。
                
                actual_count = len(image_files)
                
                if actual_count == 0:
                    status = "draft"
                elif actual_count >= expected_count and expected_count > 0:
                    status = "completed"
                else:
                    status = "partial" if actual_count > 0 else "draft"
                
                record.status = status
                # 尝试找到封面 (index 0)
                cover_img = next((img.filename for img in images if str(img.index) == '0'), None)
                if cover_img:
                    record.thumbnail = cover_img
                elif image_files:
                    record.thumbnail = image_files[0]
                
                record.images_json = json.dumps({
                    "task_id": task_id,
                    "generated": image_files # 这里存所有文件名
                })
                record.updated_at = datetime.utcnow()
                
                db.commit()
                
                return {
                    "success": True,
                    "record_id": record.id,
                    "task_id": task_id,
                    "images_count": actual_count,
                    "images": image_files,
                    "status": status
                }
            
            return {
                "success": True,
                "task_id": task_id,
                "images_count": len(image_files),
                "images": image_files,
                "no_record": True
            }
        finally:
            db.close()


    def _record_to_dict(self, record: History, full: bool = False) -> Dict:
        try:
            outline_data = json.loads(record.outline)
        except:
            outline_data = {}
            
        try:
            images_data = json.loads(record.images_json) if record.images_json else None
        except:
            images_data = None

        remaining_days = -1
        if record.expires_at:
            # Use ceiling for days to avoid 6 days 23 hours showing as 6 days
            delta = record.expires_at - datetime.utcnow()
            remaining_days = delta.days
            if delta.seconds > 0:
                remaining_days += 1
            # If remaining_days is 0 but not expired? The logic above handles it (0 days 23 hours -> 1 day)
            # If expired (negative delta), days is negative. Correct.
        
        base = {
            "id": record.id,
            "title": record.title,
            "created_at": record.created_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
            "status": record.status,
            "thumbnail": record.thumbnail,
            "page_count": record.page_count,
            "task_id": record.task_id,
            "expires_at": record.expires_at.isoformat() if record.expires_at else None,
            "remaining_days": remaining_days,
            "keyword": record.keyword
        }
        
        if full:
            base["outline"] = outline_data
            base["images"] = images_data or {"task_id": record.task_id, "generated": []}
            
        return base

_service_instance = None

def get_history_service() -> HistoryService:
    global _service_instance
    if _service_instance is None:
        _service_instance = HistoryService()
    return _service_instance
