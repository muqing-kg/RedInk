from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey, DateTime, UniqueConstraint, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(128), unique=True, nullable=True)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(16), nullable=False, default="user")
    created_at = Column(DateTime, default=datetime.utcnow)

class ProviderConfig(Base):
    __tablename__ = "provider_configs"
    id = Column(Integer, primary_key=True)
    category = Column(String(16), nullable=False, default="image")
    provider_name = Column(String(64), nullable=False)
    type = Column(String(64), nullable=True)
    api_key = Column(String(256), nullable=True)
    base_url = Column(String(256), nullable=True)
    model = Column(String(128), nullable=True)
    quality = Column(String(32), nullable=True)
    default_size = Column(String(32), nullable=True)
    default_aspect_ratio = Column(String(16), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("category", "provider_name", name="uq_provider_name"),)

class UserProviderConfig(Base):
    __tablename__ = "user_provider_configs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String(16), nullable=False, default="image")
    provider_name = Column(String(64), nullable=False)
    api_key = Column(String(256), nullable=True)
    base_url = Column(String(256), nullable=True)
    model = Column(String(128), nullable=True)
    quality = Column(String(32), nullable=True)
    default_size = Column(String(32), nullable=True)
    default_aspect_ratio = Column(String(16), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("user_id", "category", "provider_name", name="uq_user_provider"),)

class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(String(64), nullable=False)
    index = Column(Integer, nullable=False)
    filename = Column(String(128), nullable=False)
    image_data = Column(LargeBinary, nullable=False)
    thumbnail_data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("user_id", "task_id", "filename", name="uq_image_key"),)

class Copywriting(Base):
    __tablename__ = "copywritings"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String(256), nullable=False)
    outline_text = Column(String(4096), nullable=True)
    pages_json = Column(String(8192), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class History(Base):
    __tablename__ = "histories"
    id = Column(String(36), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(256), nullable=False)
    outline = Column(Text, nullable=False)
    status = Column(String(32), default="draft")
    thumbnail = Column(String(128), nullable=True)
    expires_at = Column(DateTime, nullable=True)  # 过期时间
    keyword = Column(String(64), nullable=True)   # 图片命名前缀
    task_id = Column(String(64), nullable=True)
    images_json = Column(Text, nullable=True)
    page_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
