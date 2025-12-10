"""
历史记录相关 API 路由

包含功能：
- 创建/获取/更新/删除历史记录 (CRUD)
- 搜索历史记录
- 获取统计信息
- 扫描和同步任务图片
- 打包下载图片
"""

import os
import io
import zipfile
import logging
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.history import get_history_service
from backend.services.cleanup_service import get_cleanup_service

logger = logging.getLogger(__name__)


def create_history_blueprint():
    """创建历史记录路由蓝图（工厂函数，支持多次调用）"""
    history_bp = Blueprint('history', __name__)

    # ==================== CRUD 操作 ====================



    @history_bp.route('/history/expiring-soon', methods=['GET'])
    @jwt_required()
    def get_expiring_soon_routes():
        current_user_id = get_jwt_identity()
        c_service = get_cleanup_service()
        records = c_service.get_expiring_soon(current_user_id, days=1)
        return jsonify({"success": True, "records": records}), 200

    @history_bp.route('/history', methods=['POST'])
    @jwt_required()
    def create_history():
        """
        创建历史记录

        请求体：
        - topic: 主题标题（必填）
        - outline: 大纲内容（必填）
        - task_id: 关联的任务 ID（可选）

        返回：
        - success: 是否成功
        - record_id: 新创建的记录 ID
        """
        try:
            data = request.get_json()
            topic = data.get('topic')
            outline = data.get('outline')
            task_id = data.get('task_id')

            if not topic or not outline:
                return jsonify({
                    "success": False,
                    "error": "参数错误：topic 和 outline 不能为空。\n请提供主题和大纲内容。"
                }), 400

            user_id = int(get_jwt_identity())
            history_service = get_history_service()
            record_id = history_service.create_record(user_id, topic, outline, task_id)

            return jsonify({
                "success": True,
                "record_id": record_id
            }), 200

        except Exception as e:
            error_msg = str(e)
            return jsonify({
                "success": False,
                "error": f"创建历史记录失败。\n错误详情: {error_msg}"
            }), 500

    @history_bp.route('/history', methods=['GET'])
    @jwt_required()
    def list_history():
        """
        获取历史记录列表（分页）

        查询参数：
        - page: 页码（默认 1）
        - page_size: 每页数量（默认 20）
        - status: 状态过滤（可选：all/completed/draft）

        返回：
        - success: 是否成功
        - records: 记录列表
        - total: 总数
        - total_pages: 总页数
        """
        try:
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 20))
            status = request.args.get('status')
            
            user_id = int(get_jwt_identity())
            history_service = get_history_service()
            result = history_service.list_records(user_id, page, page_size, status)

            return jsonify({
                "success": True,
                **result
            }), 200

        except Exception as e:
            error_msg = str(e)
            return jsonify({
                "success": False,
                "error": f"获取历史记录列表失败。\n错误详情: {error_msg}"
            }), 500

    @history_bp.route('/history/<record_id>', methods=['GET'])
    @jwt_required()
    def get_history(record_id):
        """
        获取历史记录详情

        路径参数：
        - record_id: 记录 ID

        返回：
        - success: 是否成功
        - record: 完整的记录数据
        """
        try:
            user_id = int(get_jwt_identity())
            history_service = get_history_service()
            record = history_service.get_record(record_id, user_id)

            if not record:
                return jsonify({
                    "success": False,
                    "error": f"历史记录不存在：{record_id}\n可能原因：记录已被删除或无权访问"
                }), 404

            return jsonify({
                "success": True,
                "record": record
            }), 200

        except Exception as e:
            error_msg = str(e)
            return jsonify({
                "success": False,
                "error": f"获取历史记录详情失败。\n错误详情: {error_msg}"
            }), 500

    @history_bp.route('/history/<record_id>', methods=['PUT'])
    @jwt_required()
    def update_history(record_id):
        """
        更新历史记录

        路径参数：
        - record_id: 记录 ID

        请求体（均为可选）：
        - outline: 大纲内容
        - images: 图片信息
        - status: 状态
        - thumbnail: 缩略图文件名

        返回：
        - success: 是否成功
        """
        try:
            data = request.get_json()
            outline = data.get('outline')
            images = data.get('images')
            status = data.get('status')
            thumbnail = data.get('thumbnail')

            user_id = int(get_jwt_identity())
            history_service = get_history_service()
            success = history_service.update_record(
                record_id,
                user_id=user_id,
                outline=outline,
                images=images,
                status=status,
                thumbnail=thumbnail
            )

            if not success:
                return jsonify({
                    "success": False,
                    "error": f"更新历史记录失败：{record_id}\n可能原因：记录不存在或无权访问"
                }), 404

            return jsonify({
                "success": True
            }), 200

        except Exception as e:
            error_msg = str(e)
            return jsonify({
                "success": False,
                "error": f"更新历史记录失败。\n错误详情: {error_msg}"
            }), 500

    @history_bp.route('/history/<record_id>', methods=['DELETE'])
    @jwt_required()
    def delete_history(record_id):
        """
        删除历史记录

        路径参数：
        - record_id: 记录 ID

        返回：
        - success: 是否成功
        """
        try:
            user_id = int(get_jwt_identity())
            history_service = get_history_service()
            success = history_service.delete_record(record_id, user_id)

            if not success:
                return jsonify({
                    "success": False,
                    "error": f"删除历史记录失败：{record_id}\n可能原因：记录不存在或无权操作"
                }), 404

            return jsonify({
                "success": True
            }), 200

        except Exception as e:
            error_msg = str(e)
            return jsonify({
                "success": False,
                "error": f"删除历史记录失败。\n错误详情: {error_msg}"
            }), 500

    # ==================== 搜索和统计 ====================

    @history_bp.route('/history/search', methods=['GET'])
    @jwt_required()
    def search_history():
        """
        搜索历史记录

        查询参数：
        - keyword: 搜索关键词（必填）

        返回：
        - success: 是否成功
        - records: 匹配的记录列表
        """
        try:
            keyword = request.args.get('keyword', '')

            if not keyword:
                return jsonify({
                    "success": False,
                    "error": "参数错误：keyword 不能为空。\n请提供搜索关键词。"
                }), 400
            
            user_id = int(get_jwt_identity())
            history_service = get_history_service()
            results = history_service.search_records(user_id, keyword)

            return jsonify({
                "success": True,
                "records": results
            }), 200

        except Exception as e:
            error_msg = str(e)
            return jsonify({
                "success": False,
                "error": f"搜索历史记录失败。\n错误详情: {error_msg}"
            }), 500

    @history_bp.route('/history/stats', methods=['GET'])
    @jwt_required()
    def get_history_stats():
        """
        获取历史记录统计信息

        返回：
        - success: 是否成功
        - total: 总记录数
        - by_status: 按状态分组的统计
        """
        try:
            user_id = int(get_jwt_identity())
            history_service = get_history_service()
            stats = history_service.get_statistics(user_id)

            return jsonify({
                "success": True,
                **stats
            }), 200

        except Exception as e:
            error_msg = str(e)
            return jsonify({
                "success": False,
                "error": f"获取历史记录统计失败。\n错误详情: {error_msg}"
            }), 500

    # ==================== 扫描和同步 ====================

    @history_bp.route('/history/scan/<task_id>', methods=['GET'])
    @jwt_required()
    def scan_task(task_id):
        """
        扫描单个任务并同步图片列表
        """
        try:
            user_id = int(get_jwt_identity())
            history_service = get_history_service()
            result = history_service.scan_and_sync_task_images(task_id, user_id)

            if not result.get("success"):
                return jsonify(result), 404

            return jsonify(result), 200

        except Exception as e:
            error_msg = str(e)
            return jsonify({
                "success": False,
                "error": f"扫描任务失败。\n错误详情: {error_msg}"
            }), 500


    # ==================== 下载功能 ====================

    # ==================== 下载功能 ====================
    
    @history_bp.route('/history/<record_id>/download', methods=['GET'])
    def download_history_zip(record_id):
        """
        下载历史记录的所有图片为 ZIP 文件
        支持通过 Authorization Header 或 token Query Param 进行认证
        """
        return download_history_zip_impl(record_id)
        
    return history_bp

# 为了解决引用问题，把 download 逻辑独立出来
from flask_jwt_extended import decode_token

def download_history_zip_impl(record_id):
    # 自定义 Token 验证
    user_id = None
    try:
        # 1. Try Header
        if request.headers.get('Authorization'):
            from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
            verify_jwt_in_request()
            user_id = int(get_jwt_identity())
        # 2. Try Query Param
        elif request.args.get('token'):
            token = request.args.get('token')
            decoded = decode_token(token)
            user_id = int(decoded['sub']) # 'sub' usually stores identity
    except Exception as e:
        return jsonify({"success": False, "error": "认证失败"}), 401
    
    if not user_id:
         return jsonify({"success": False, "error": "未登录"}), 401

    try:
        history_service = get_history_service()
        record = history_service.get_record(record_id, user_id)

        if not record:
            return jsonify({
                "success": False,
                "error": f"历史记录不存在：{record_id}"
            }), 404

        task_id = record.get('images', {}).get('task_id')
        if not task_id:
            return jsonify({
                "success": False,
                "error": "该记录没有关联的任务图片"
            }), 404

        from backend.db import SessionLocal
        from backend.models import Image
        db = SessionLocal()
        try:
            imgs = db.query(Image).filter_by(task_id=task_id).all()
            if not imgs:
                return jsonify({"success": False, "error": "未找到图片"}), 404
            zip_buffer = _create_images_zip_from_db(imgs)
        finally:
            db.close()

        # 生成安全的下载文件名
        title = record.get('title', 'images')
        safe_title = _sanitize_filename(title)
        filename = f"{safe_title}.zip"

        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        error_msg = str(e)
        return jsonify({
            "success": False,
            "error": f"下载失败。\n错误详情: {error_msg}"
        }), 500


def _create_images_zip_from_db(images: list) -> io.BytesIO:
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for img in images:
            try:
                idx = int(img.filename.split('.')[0])
                name = f"page_{idx + 1}.png"
            except Exception:
                name = img.filename
            zf.writestr(name, img.image_data)
    memory_file.seek(0)
    return memory_file


def _sanitize_filename(title: str) -> str:
    """清理文件名"""
    safe_title = "".join(
        c for c in title
        if c.isalnum() or c in (' ', '-', '_', '\u4e00-\u9fff')
    ).strip()
    return safe_title if safe_title else 'images'
