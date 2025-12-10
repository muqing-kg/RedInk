from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from ..db import SessionLocal
from ..models import User

def create_auth_blueprint():
    bp = Blueprint("auth", __name__)

    @bp.route('/auth/register', methods=['POST'])
    def register():
        data = request.get_json() or {}
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        if not username or not password:
            return jsonify({"success": False, "error": "缺少用户名或密码"}), 400
        db = SessionLocal()
        try:
            if db.query(User).filter_by(username=username).first():
                return jsonify({"success": False, "error": "用户名已存在"}), 400
            role = 'user'
            if db.query(User).count() == 0:
                role = 'admin'
            user = User(username=username, email=email, password_hash=generate_password_hash(password), role=role)
            db.add(user)
            db.commit()
            return jsonify({"success": True}), 200
        finally:
            db.close()

    @bp.route('/auth/login', methods=['POST'])
    def login():
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({"success": False, "error": "缺少用户名或密码"}), 400
        db = SessionLocal()
        try:
            user = db.query(User).filter_by(username=username).first()
            if not user or not check_password_hash(user.password_hash, password):
                return jsonify({"success": False, "error": "用户名或密码错误"}), 401
            token = create_access_token(identity=str(user.id), additional_claims={"role": user.role}, expires_delta=timedelta(hours=12))
            return jsonify({"success": True, "access_token": token, "role": user.role}), 200
        finally:
            db.close()

    @bp.route('/auth/me', methods=['GET'])
    @jwt_required()
    def me():
        uid = int(get_jwt_identity())
        db = SessionLocal()
        try:
            user = db.query(User).get(uid)
            return jsonify({"success": True, "user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role}})
        finally:
            db.close()
    
    @bp.route('/auth/change-password', methods=['POST'])
    @jwt_required()
    def change_password():
        uid = int(get_jwt_identity())
        data = request.get_json() or {}
        current_password = data.get('currentPassword')
        new_password = data.get('newPassword')
        
        if not current_password or not new_password:
            return jsonify({"success": False, "error": "缺少当前密码或新密码"}), 400
        
        db = SessionLocal()
        try:
            user = db.query(User).get(uid)
            if not user:
                return jsonify({"success": False, "error": "用户不存在"}), 404
            
            if not check_password_hash(user.password_hash, current_password):
                return jsonify({"success": False, "error": "当前密码错误"}), 401
            
            user.password_hash = generate_password_hash(new_password)
            db.commit()
            return jsonify({"success": True, "message": "密码修改成功"}), 200
        finally:
            db.close()

    return bp
