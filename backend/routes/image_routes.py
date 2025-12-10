"""
图片生成相关 API 路由

包含功能：
- 批量生成图片（SSE 流式返回）
- 获取图片
- 重试/重新生成单张图片
- 批量重试失败图片
- 获取任务状态
"""

import os
import json
import base64
import logging
from flask import Blueprint, request, jsonify, Response, send_file, make_response
from backend.services.image import get_image_service
from backend.services.history import get_history_service
from .utils import log_request, log_error
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token, verify_jwt_in_request
from backend.db import SessionLocal
from backend.models import Image

logger = logging.getLogger(__name__)


def create_image_blueprint():
    """创建图片路由蓝图（工厂函数，支持多次调用）"""
    image_bp = Blueprint('image', __name__)

    # ==================== 图片生成 ====================

    @image_bp.route('/generate', methods=['POST'])
    @jwt_required()
    def generate_images():
        """
        批量生成图片（SSE 流式返回）

        请求体：
        - pages: 页面列表（必填）
        - task_id: 任务 ID
        - full_outline: 完整大纲文本
        - user_topic: 用户原始输入主题
        - user_images: base64 编码的用户参考图片列表

        返回：
        SSE 事件流，包含以下事件类型：
        - image: 单张图片生成完成
        - error: 生成错误
        - complete: 全部完成
        """
        try:
            data = request.get_json()
            pages = data.get('pages')
            task_id = data.get('task_id')
            full_outline = data.get('full_outline', '')
            user_topic = data.get('user_topic', '')

            # 解析 base64 格式的用户参考图片
            user_images = _parse_base64_images(data.get('user_images', []))

            log_request('/generate', {
                'pages_count': len(pages) if pages else 0,
                'task_id': task_id,
                'user_topic': user_topic[:50] if user_topic else None,
                'user_images': user_images
            })

            if not pages:
                logger.warning("图片生成请求缺少 pages 参数")
                return jsonify({
                    "success": False,
                    "error": "参数错误：pages 不能为空。\n请提供要生成的页面列表数据。"
                }), 400

            logger.info(f"🖼️  开始图片生成任务: {task_id}, 共 {len(pages)} 页")
            user_id = int(get_jwt_identity())
            image_service = get_image_service(user_id)

            image_service = get_image_service(user_id)
            
            # 获取关键词并启动过期计时
            keyword = ""
            try:
                hs = get_history_service()
                record = hs.get_record_by_task_id(task_id)
                if record:
                    hs.start_expiry(record.id)
                    keyword = record.keyword or ""
            except Exception as e:
                logger.warning(f"Failed to sync history info for task {task_id}: {e}")

            def generate():
                """SSE 事件生成器"""
                for event in image_service.generate_images(
                    pages, task_id, full_outline,
                    user_images=user_images if user_images else None,
                    user_topic=user_topic,
                    keyword=keyword
                ):
                    event_type = event["event"]
                    event_data = event["data"]

                    # 格式化为 SSE 格式
                    yield f"event: {event_type}\n"
                    yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"

            return Response(
                generate(),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no',
                }
            )

        except Exception as e:
            log_error('/generate', e)
            error_msg = str(e)
            return jsonify({
                "success": False,
                "error": f"图片生成异常。\n错误详情: {error_msg}\n建议：检查图片生成服务配置和后端日志"
            }), 500

    # ==================== 图片获取 ====================

    @image_bp.route('/images/<task_id>/<filename>', methods=['GET'])
    def get_image(task_id, filename):
        """
        获取图片文件（支持 Header 或 Query Param 认证）
        """
        try:
            # logger.debug(f"获取图片: {task_id}/{filename}")
            
            # 自定义认证逻辑
            user_id = None
            auth_error = None
            try:
                # 1. 尝试 Header
                if request.headers.get('Authorization'):
                    verify_jwt_in_request()
                    user_id = int(get_jwt_identity())
                    logger.debug(f"从 Header 获取 user_id: {user_id}")
                # 2. 尝试 Query Param
                elif request.args.get('token'):
                    token = request.args.get('token')
                    logger.debug(f"尝试从 Query Param 解析 token (长度={len(token)})")
                    decoded = decode_token(token)
                    user_id = int(decoded['sub'])
                    logger.debug(f"从 Token 获取 user_id: {user_id}")
                else:
                    auth_error = "未提供认证信息"
            except Exception as e:
                auth_error = str(e)
                logger.warning(f"Token 解析失败: {auth_error}")
            
            if not user_id:
                logger.warning(f"图片访问被拒绝: {task_id}/{filename}, 原因: {auth_error or '未知'}")
                return jsonify({"success": False, "error": f"未授权访问: {auth_error or '无有效认证'}"}), 401

            thumbnail = request.args.get('thumbnail', 'true').lower() == 'true'
            db = SessionLocal()
            try:
                img = db.query(Image).filter_by(user_id=user_id, task_id=task_id, filename=filename).first()
                if not img:
                    return jsonify({"success": False, "error": f"图片不存在或无权访问"}), 404
                data = img.thumbnail_data if thumbnail else img.image_data
                resp = make_response(data)
                resp.headers.set('Content-Type', 'image/png')
                # 设置缓存控制，因为带了 token，url 是唯一的吗？不一定。
                # 但图片内容是不变的。
                resp.headers.set('Cache-Control', 'private, max-age=3600') 
                return resp
            finally:
                db.close()

        except Exception as e:
            log_error('/images', e)
            error_msg = str(e)
            return jsonify({
                "success": False,
                "error": f"获取图片失败: {error_msg}"
            }), 500

    # ==================== 重试和重新生成 ====================

    @image_bp.route('/retry', methods=['POST'])
    @jwt_required()
    def retry_single_image():
        """
        重试生成单张失败的图片

        请求体：
        - task_id: 任务 ID（必填）
        - page: 页面信息（必填）
        - use_reference: 是否使用参考图（默认 true）

        返回：
        - success: 是否成功
        - image_url: 新图片 URL
        """
        try:
            data = request.get_json()
            task_id = data.get('task_id')
            page = data.get('page')
            use_reference = data.get('use_reference', True)

            log_request('/retry', {
                'task_id': task_id,
                'page_index': page.get('index') if page else None
            })

            if not task_id or not page:
                logger.warning("重试请求缺少必要参数")
                return jsonify({
                    "success": False,
                    "error": "参数错误：task_id 和 page 不能为空。\n请提供任务ID和页面信息。"
                }), 400

            logger.info(f"🔄 重试生成图片: task={task_id}, page={page.get('index')}")
            user_id = int(get_jwt_identity())
            image_service = get_image_service(user_id)
            result = image_service.retry_single_image(task_id, page, use_reference)

            if result["success"]:
                logger.info(f"✅ 图片重试成功: {result.get('image_url')}")
            else:
                logger.error(f"❌ 图片重试失败: {result.get('error')}")

            return jsonify(result), 200 if result["success"] else 500

        except Exception as e:
            log_error('/retry', e)
            error_msg = str(e)
            return jsonify({
                "success": False,
                "error": f"重试图片生成失败。\n错误详情: {error_msg}"
            }), 500

    @image_bp.route('/retry-failed', methods=['POST'])
    @jwt_required()
    def retry_failed_images():
        """
        批量重试失败的图片（SSE 流式返回）

        请求体：
        - task_id: 任务 ID（必填）
        - pages: 要重试的页面列表（必填）

        返回：
        SSE 事件流
        """
        try:
            data = request.get_json()
            task_id = data.get('task_id')
            pages = data.get('pages')

            log_request('/retry-failed', {
                'task_id': task_id,
                'pages_count': len(pages) if pages else 0
            })

            if not task_id or not pages:
                logger.warning("批量重试请求缺少必要参数")
                return jsonify({
                    "success": False,
                    "error": "参数错误：task_id 和 pages 不能为空。\n请提供任务ID和要重试的页面列表。"
                }), 400

            logger.info(f"🔄 批量重试失败图片: task={task_id}, 共 {len(pages)} 页")
            user_id = int(get_jwt_identity())
            image_service = get_image_service(user_id)

            def generate():
                """SSE 事件生成器"""
                for event in image_service.retry_failed_images(task_id, pages):
                    event_type = event["event"]
                    event_data = event["data"]

                    yield f"event: {event_type}\n"
                    yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"

            return Response(
                generate(),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no',
                }
            )

        except Exception as e:
            log_error('/retry-failed', e)
            error_msg = str(e)
            return jsonify({
                "success": False,
                "error": f"批量重试失败。\n错误详情: {error_msg}"
            }), 500

    @image_bp.route('/regenerate', methods=['POST'])
    @jwt_required()
    def regenerate_image():
        """
        重新生成图片（即使成功的也可以重新生成）

        请求体：
        - task_id: 任务 ID（必填）
        - page: 页面信息（必填）
        - use_reference: 是否使用参考图（默认 true）
        - full_outline: 完整大纲文本（用于上下文）
        - user_topic: 用户原始输入主题

        返回：
        - success: 是否成功
        - image_url: 新图片 URL
        """
        try:
            data = request.get_json()
            task_id = data.get('task_id')
            page = data.get('page')
            use_reference = data.get('use_reference', True)
            full_outline = data.get('full_outline', '')
            user_topic = data.get('user_topic', '')

            log_request('/regenerate', {
                'task_id': task_id,
                'page_index': page.get('index') if page else None
            })

            if not task_id or not page:
                logger.warning("重新生成请求缺少必要参数")
                return jsonify({
                    "success": False,
                    "error": "参数错误：task_id 和 page 不能为空。\n请提供任务ID和页面信息。"
                }), 400

            logger.info(f"🔄 重新生成图片: task={task_id}, page={page.get('index')}")
            user_id = int(get_jwt_identity())
            # 获取 keyword
            keyword = ""
            try:
                hs = get_history_service()
                record = hs.get_record_by_task_id(task_id)
                if record:
                    keyword = record.keyword or ""
            except Exception:
                pass

            image_service = get_image_service(user_id)
            result = image_service.regenerate_image(
                task_id, page, use_reference,
                full_outline=full_outline,
                user_topic=user_topic,
                keyword=keyword
            )

            if result["success"]:
                logger.info(f"✅ 图片重新生成成功: {result.get('image_url')}")
            else:
                logger.error(f"❌ 图片重新生成失败: {result.get('error')}")

            return jsonify(result), 200 if result["success"] else 500

        except Exception as e:
            log_error('/regenerate', e)
            error_msg = str(e)
            return jsonify({
                "success": False,
                "error": f"重新生成图片失败。\n错误详情: {error_msg}"
            }), 500

    # ==================== 任务状态 ====================

    @image_bp.route('/task/<task_id>', methods=['GET'])
    @jwt_required()
    def get_task_state(task_id):
        """
        获取任务状态

        路径参数：
        - task_id: 任务 ID

        返回：
        - success: 是否成功
        - state: 任务状态
          - generated: 已生成的图片
          - failed: 失败的图片
          - has_cover: 是否有封面图
        """
        try:
            user_id = int(get_jwt_identity())
            image_service = get_image_service(user_id)
            state = image_service.get_task_state(task_id)

            if state is None:
                return jsonify({
                    "success": False,
                    "error": f"任务不存在：{task_id}\n可能原因：\n1. 任务ID错误\n2. 任务已过期或被清理\n3. 服务重启导致状态丢失"
                }), 404

            # 不返回封面图片数据（太大）
            safe_state = {
                "generated": state.get("generated", {}),
                "failed": state.get("failed", {}),
                "has_cover": state.get("cover_image") is not None
            }

            return jsonify({
                "success": True,
                "state": safe_state
            }), 200

        except Exception as e:
            error_msg = str(e)
            return jsonify({
                "success": False,
                "error": f"获取任务状态失败。\n错误详情: {error_msg}"
            }), 500

    # ==================== 健康检查 ====================

    @image_bp.route('/health', methods=['GET'])
    def health_check():
        """
        健康检查接口

        返回：
        - success: 服务是否正常
        - message: 状态消息
        """
        return jsonify({
            "success": True,
            "message": "服务正常运行"
        }), 200

    return image_bp


# ==================== 辅助函数 ====================

def _parse_base64_images(images_base64: list) -> list:
    """
    解析 base64 编码的图片列表

    Args:
        images_base64: base64 编码的图片字符串列表

    Returns:
        list: 解码后的图片二进制数据列表
    """
    if not images_base64:
        return []

    images = []
    for img_b64 in images_base64:
        # 移除可能的 data URL 前缀（如 data:image/png;base64,）
        if ',' in img_b64:
            img_b64 = img_b64.split(',')[1]
        images.append(base64.b64decode(img_b64))

    return images
