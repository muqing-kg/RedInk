import logging
import sys
from pathlib import Path
from flask import Flask, send_from_directory
from flask_cors import CORS
from backend.config import Config
from backend.routes import register_routes
from flask_jwt_extended import JWTManager
from backend.db import Base, engine
from backend.db import SessionLocal
from backend.models import User
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv


def setup_logging():
    """配置日志系统"""
    # 创建根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # 清除已有的处理器
    root_logger.handlers.clear()

    # 控制台处理器 - 详细格式
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_format = logging.Formatter(
        '\n%(asctime)s | %(levelname)-8s | %(name)s\n'
        '  └─ %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)

    # 设置各模块的日志级别
    logging.getLogger('backend').setLevel(logging.DEBUG)
    logging.getLogger('werkzeug').setLevel(logging.INFO)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    return root_logger

def _ensure_admin_from_env(logger):
    # 从环境变量获取管理员账户信息，如果没有则使用默认值
    username = os.getenv('ADMIN_USERNAME', 'admin')
    password = os.getenv('ADMIN_PASSWORD', 'admin123')
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(username=username).first()
        if not user:
            user = User(username=username, email=None, password_hash=generate_password_hash(password), role='admin')
            db.add(user)
            db.commit()
            logger.info(f"✅ 已创建管理员账户: {username}, 密码: {password}")
        else:
            user.role = 'admin'
            user.password_hash = generate_password_hash(password)
            db.commit()
            logger.info(f"✅ 已更新管理员账户密码与角色: {username}, 密码: {password}")
    except Exception as e:
        logger.error(f"❌ 管理员账户创建失败: {e}")
    finally:
        db.close()


def create_app():
    # 设置日志
    logger = setup_logging()
    logger.info("🚀 正在启动 小红书AI图文生成器...")
    # 加载 .env 环境变量文件（可选）
    try:
        from pathlib import Path
        # 优先从 /data 目录加载 .env 文件
        env_path = Path('/data') / '.env'
        if not env_path.exists():
            # 如果 /data 目录下没有 .env 文件，则从项目根目录加载（兼容旧部署）
            env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)
        logger.info(f"🔑 已从 {env_path} 加载 .env 环境变量")
    except Exception:
        logger.info("🔑 未检测到 .env 或加载失败，使用系统环境变量")

    # 检查是否存在前端构建产物（Docker 环境）
    frontend_dist = Path(__file__).parent.parent / 'frontend' / 'dist'
    if frontend_dist.exists():
        logger.info("📦 检测到前端构建产物，启用静态文件托管模式")
        app = Flask(
            __name__,
            static_folder=str(frontend_dist),
            static_url_path=''
        )
    else:
        logger.info("🔧 开发模式，前端请单独启动")
        app = Flask(__name__)

    app.config.from_object(Config)
    app.config["JWT_SECRET_KEY"] = app.config.get("JWT_SECRET_KEY") or "dev-secret"
    jwt = JWTManager(app)

    CORS(app, resources={
        r"/api/*": {
            "origins": Config.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    })

    Base.metadata.create_all(engine)
    _ensure_admin_from_env(logger)
    # 注册所有 API 路由
    register_routes(app)

    # 启动时验证配置
    _validate_config_on_startup(logger)
    
    # 启动后台任务
    _start_background_tasks(app, logger)

    # 根据是否有前端构建产物决定根路由行为
    if frontend_dist.exists():
        @app.route('/')
        def serve_index():
            return send_from_directory(app.static_folder, 'index.html')

        # 处理 Vue Router 的 HTML5 History 模式
        @app.errorhandler(404)
        def fallback(e):
            return send_from_directory(app.static_folder, 'index.html')
    else:
        @app.route('/')
        def index():
            return {
                "message": "小红书AI图文生成器 API",
                "version": "0.1.0",
                "endpoints": {
                    "health": "/api/health",
                    "outline": "POST /api/outline",
                    "generate": "POST /api/generate",
                    "images": "GET /api/images/<filename>"
                }
            }

    return app


def _validate_config_on_startup(logger):
    """启动时验证配置"""
    from pathlib import Path
    import yaml
    from backend.config import Config

    logger.info("📋 检查配置文件...")

    # 使用修改后的配置加载逻辑，会优先从 /data 目录加载
    try:
        # 检查文本生成配置
        text_config = Config.load_text_providers_config()
        active_text = text_config.get('active_provider', '未设置')
        text_providers = list(text_config.get('providers', {}).keys())
        logger.info(f"✅ 文本生成配置: 激活={active_text}, 可用服务商={text_providers}")
        
        # 检查图片生成配置
        image_config = Config.load_image_providers_config()
        active_image = image_config.get('active_provider', '未设置')
        image_providers = list(image_config.get('providers', {}).keys())
        logger.info(f"✅ 图片生成配置: 激活={active_image}, 可用服务商={image_providers}")
        
    except Exception as e:
        logger.error(f"❌ 配置检查失败: {e}")
    
    logger.info("✅ 配置检查完成")


def _start_background_tasks(app, logger):
    """启动后台任务"""
    import threading
    import time
    from backend.services.cleanup_service import get_cleanup_service
    
    # 防止在 reloader 的主进程中启动
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        def cleanup_loop():
            with app.app_context():
                logger.info("🕒 启动自动清理调度器...")
                while True:
                    try:
                        # 启动后先等待一会再检查，避免刚启动就冲突
                        time.sleep(3600)  # 每小时执行一次
                        
                        logger.info("🧹 执行自动清理任务...")
                        service = get_cleanup_service()
                        res = service.cleanup_expired_records()
                        if res["deleted_count"] > 0:
                            logger.info(f"🧹 清理完成: 删除了 {res['deleted_count']} 条过期记录")
                    except Exception as e:
                        logger.error(f"❌ 清理任务异常: {e}")

        thread = threading.Thread(target=cleanup_loop, daemon=True)
        thread.start()


if __name__ == '__main__':
    app = create_app()
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
