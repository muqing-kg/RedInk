from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..db import SessionLocal
from ..models import ProviderConfig, UserProviderConfig, User
from werkzeug.security import generate_password_hash

def create_provider_blueprint():
    bp = Blueprint("provider", __name__)

    @bp.route('/admin/providers', methods=['POST'])
    @jwt_required()
    def set_global_provider():
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"success": False, "error": "无权限"}), 403
        data = request.get_json() or {}
        name = data.get('provider_name')
        category = data.get('category') or 'image'
        if not name:
            return jsonify({"success": False, "error": "缺少 provider_name"}), 400
        db = SessionLocal()
        try:
            cfg = db.query(ProviderConfig).filter_by(category=category, provider_name=name).first()
            if not cfg:
                cfg = ProviderConfig(category=category, provider_name=name)
                db.add(cfg)
            for k in ["type","api_key","base_url","model","quality","default_size","default_aspect_ratio"]:
                if k in data:
                    setattr(cfg, k, data[k])
            db.commit()
            return jsonify({"success": True}), 200
        finally:
            db.close()

    @bp.route('/user/providers', methods=['POST'])
    @jwt_required()
    def set_user_provider():
        uid = int(get_jwt_identity())
        data = request.get_json() or {}
        name = data.get('provider_name')
        category = data.get('category') or 'image'
        if not name:
            return jsonify({"success": False, "error": "缺少 provider_name"}), 400
        db = SessionLocal()
        try:
            cfg = db.query(UserProviderConfig).filter_by(user_id=uid, category=category, provider_name=name).first()
            if not cfg:
                cfg = UserProviderConfig(user_id=uid, category=category, provider_name=name)
                db.add(cfg)
            for k in ["api_key","base_url","model","quality","default_size","default_aspect_ratio"]:
                if k in data:
                    setattr(cfg, k, data[k])
            db.commit()
            return jsonify({"success": True}), 200
        finally:
            db.close()

    @bp.route('/admin/providers/sync', methods=['POST'])
    @jwt_required()
    def sync_global_to_users():
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"success": False, "error": "无权限"}), 403
        data = request.get_json() or {}
        name = data.get('provider_name')
        category = data.get('category') or 'image'
        if not name:
            return jsonify({"success": False, "error": "缺少 provider_name"}), 400
        db = SessionLocal()
        try:
            cfg = db.query(ProviderConfig).filter_by(category=category, provider_name=name).first()
            if not cfg:
                return jsonify({"success": False, "error": "未找到全局配置"}), 404
            users = db.query(User).all()
            for u in users:
                up = db.query(UserProviderConfig).filter_by(user_id=u.id, category=category, provider_name=name).first()
                if not up:
                    up = UserProviderConfig(user_id=u.id, category=category, provider_name=name)
                    db.add(up)
                up.api_key = cfg.api_key
                up.base_url = cfg.base_url
                up.model = cfg.model
                up.quality = cfg.quality
                up.default_size = cfg.default_size
                up.default_aspect_ratio = cfg.default_aspect_ratio
            db.commit()
            return jsonify({"success": True, "synced": len(users)}), 200
        finally:
            db.close()

    @bp.route('/user/providers', methods=['GET'])
    @jwt_required()
    def get_user_providers():
        uid = int(get_jwt_identity())
        category = request.args.get('category')
        db = SessionLocal()
        try:
            query = db.query(UserProviderConfig).filter_by(user_id=uid)
            if category:
                query = query.filter(UserProviderConfig.category == category)
            items = query.all()
            return jsonify({
                "success": True,
                "providers": [
                    {
                        "category": i.category,
                        "provider_name": i.provider_name,
                        "api_key": i.api_key,
                        "base_url": i.base_url,
                        "model": i.model,
                        "quality": i.quality,
                        "default_size": i.default_size,
                        "default_aspect_ratio": i.default_aspect_ratio,
                    } for i in items
                ]
            }), 200
        finally:
            db.close()

    @bp.route('/admin/users', methods=['GET'])
    @jwt_required()
    def list_users():
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"success": False, "error": "无权限"}), 403
        db = SessionLocal()
        try:
            users = db.query(User).all()
            return jsonify({
                "success": True,
                "users": [
                    {
                        "id": u.id,
                        "username": u.username,
                        "email": u.email,
                        "role": u.role,
                        "created_at": u.created_at.isoformat() if u.created_at else None
                    } for u in users
                ]
            }), 200
        finally:
            db.close()

    @bp.route('/admin/users/<int:user_id>', methods=['PUT'])
    @jwt_required()
    def update_user(user_id: int):
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"success": False, "error": "无权限"}), 403
        data = request.get_json() or {}
        new_username = data.get('username')
        new_password = data.get('password')
        db = SessionLocal()
        try:
            user = db.query(User).get(user_id)
            if not user:
                return jsonify({"success": False, "error": "用户不存在"}), 404
            if new_username:
                exists = db.query(User).filter(User.username == new_username, User.id != user_id).first()
                if exists:
                    return jsonify({"success": False, "error": "用户名已存在"}), 400
                user.username = new_username
            if new_password:
                user.password_hash = generate_password_hash(new_password)
            db.commit()
            return jsonify({"success": True}), 200
        finally:
            db.close()

    return bp
