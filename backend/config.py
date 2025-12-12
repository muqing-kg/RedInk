import logging
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)


class Config:
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 12398
    CORS_ORIGINS = ['http://localhost:5173', 'http://localhost:3000']

    # 动态数据目录，根据系统类型自动选择
    @classmethod
    def _get_data_dir(cls):
        """获取数据存储目录，与app.py保持一致的回退逻辑"""
        import os
        import platform
        
        # 检查当前系统是否为Windows
        is_windows = platform.system() == "Windows"
        data_dir = '/data'
        
        try:
            # 对于Windows系统，默认回退到项目根目录的data目录
            if is_windows:
                project_root = os.path.dirname(os.path.dirname(__file__))
                data_dir = os.path.join(project_root, "data")
            else:
                # 非Windows系统（如Linux/Docker），检查/data目录是否存在且可写
                if not os.path.exists(data_dir) or not os.access(data_dir, os.W_OK):
                    project_root = os.path.dirname(os.path.dirname(__file__))
                    data_dir = os.path.join(project_root, "data")
        except (PermissionError, OSError, AttributeError):
            # 捕获任何可能出现的错误，回退到项目根目录的data目录
            project_root = os.path.dirname(os.path.dirname(__file__))
            data_dir = os.path.join(project_root, "data")
        
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        return data_dir

    # 动态计算的类属性，使用getter方法
    @classmethod
    def get_output_dir(cls):
        """获取输出目录"""
        import os
        output_dir = os.path.join(cls._get_data_dir(), "output")
        # 确保目录存在
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    @classmethod
    def get_history_dir(cls):
        """获取历史目录"""
        import os
        history_dir = os.path.join(cls._get_data_dir(), "history")
        # 确保目录存在
        os.makedirs(history_dir, exist_ok=True)
        return history_dir

    # 注意：OUTPUT_DIR和HISTORY_DIR已改为通过getter方法获取
    # 为了保持向后兼容性，我们通过类方法动态返回路径
    # 直接使用 Config.get_output_dir() 和 Config.get_history_dir() 替代 Config.OUTPUT_DIR 和 Config.HISTORY_DIR

    _image_providers_config = None
    _text_providers_config = None

    @classmethod
    def _get_config_dir(cls):
        """获取配置文件存储目录，与app.py保持一致的回退逻辑"""
        import os
        import platform
        
        # 检查当前系统是否为Windows
        is_windows = platform.system() == "Windows"
        config_dir = '/data'
        
        try:
            # 对于Windows系统，默认回退到项目根目录的data目录
            if is_windows:
                project_root = os.path.dirname(os.path.dirname(__file__))
                config_dir = os.path.join(project_root, "data")
            else:
                # 非Windows系统（如Linux/Docker），检查/data目录是否存在且可写
                if not os.path.exists(config_dir) or not os.access(config_dir, os.W_OK):
                    project_root = os.path.dirname(os.path.dirname(__file__))
                    config_dir = os.path.join(project_root, "data")
        except (PermissionError, OSError, AttributeError):
            # 捕获任何可能出现的错误，回退到项目根目录的data目录
            project_root = os.path.dirname(os.path.dirname(__file__))
            config_dir = os.path.join(project_root, "data")
        
        return Path(config_dir)

    @classmethod
    def load_image_providers_config(cls):
        if cls._image_providers_config is not None:
            return cls._image_providers_config

        # 获取配置文件存储目录
        config_dir = cls._get_config_dir()
        config_path = config_dir / 'image_providers.yaml'
        logger.debug(f"加载图片服务商配置: {config_path}")

        if not config_path.exists():
            logger.warning(f"图片配置文件不存在: {config_path}，使用默认配置")
            cls._image_providers_config = {
                'active_provider': 'google_genai',
                'providers': {}
            }
            # 确保配置目录存在，然后保存默认配置
            config_dir.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(cls._image_providers_config, f, allow_unicode=True, default_flow_style=False)
            logger.info(f"已创建默认图片配置文件: {config_path}")
            return cls._image_providers_config

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                cls._image_providers_config = yaml.safe_load(f) or {}
            logger.debug(f"图片配置加载成功: {list(cls._image_providers_config.get('providers', {}).keys())}")
        except yaml.YAMLError as e:
            logger.error(f"图片配置文件 YAML 格式错误: {e}")
            raise ValueError(
                f"配置文件格式错误: image_providers.yaml\n"
                f"YAML 解析错误: {e}\n"
                "解决方案：\n"
                "1. 检查 YAML 缩进是否正确（使用空格，不要用Tab）\n"
                "2. 检查引号是否配对\n"
                "3. 使用在线 YAML 验证器检查格式"
            )

        return cls._image_providers_config

    @classmethod
    def load_text_providers_config(cls):
        """加载文本生成服务商配置"""
        if cls._text_providers_config is not None:
            return cls._text_providers_config

        # 获取配置文件存储目录
        config_dir = cls._get_config_dir()
        config_path = config_dir / 'text_providers.yaml'
        logger.debug(f"加载文本服务商配置: {config_path}")

        if not config_path.exists():
            logger.warning(f"文本配置文件不存在: {config_path}，使用默认配置")
            cls._text_providers_config = {
                'active_provider': 'google_gemini',
                'providers': {}
            }
            # 确保配置目录存在，然后保存默认配置
            config_dir.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(cls._text_providers_config, f, allow_unicode=True, default_flow_style=False)
            logger.info(f"已创建默认文本配置文件: {config_path}")
            return cls._text_providers_config

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                cls._text_providers_config = yaml.safe_load(f) or {}
            logger.debug(f"文本配置加载成功: {list(cls._text_providers_config.get('providers', {}).keys())}")
        except yaml.YAMLError as e:
            logger.error(f"文本配置文件 YAML 格式错误: {e}")
            raise ValueError(
                f"配置文件格式错误: text_providers.yaml\n"
                f"YAML 解析错误: {e}\n"
                "解决方案：\n"
                "1. 检查 YAML 缩进是否正确（使用空格，不要用Tab）\n"
                "2. 检查引号是否配对\n"
                "3. 使用在线 YAML 验证器检查格式"
            )

        return cls._text_providers_config

    @classmethod
    def get_active_image_provider(cls):
        config = cls.load_image_providers_config()
        active = config.get('active_provider', 'google_genai')
        logger.debug(f"当前激活的图片服务商: {active}")
        return active

    @classmethod
    def get_image_provider_config(cls, provider_name: str = None):
        config = cls.load_image_providers_config()

        if provider_name is None:
            provider_name = cls.get_active_image_provider()

        logger.info(f"获取图片服务商配置: {provider_name}")

        providers = config.get('providers', {})
        if not providers:
            raise ValueError(
                "未找到任何图片生成服务商配置。\n"
                "解决方案：\n"
                "1. 在系统设置页面添加图片生成服务商\n"
                "2. 或手动编辑 image_providers.yaml 文件\n"
                "3. 确保文件中有 providers 字段"
            )

        if provider_name not in providers:
            available = ', '.join(providers.keys()) if providers else '无'
            logger.error(f"图片服务商 [{provider_name}] 不存在，可用服务商: {available}")
            raise ValueError(
                f"未找到图片生成服务商配置: {provider_name}\n"
                f"可用的服务商: {available}\n"
                "解决方案：\n"
                "1. 在系统设置页面添加该服务商\n"
                "2. 或修改 active_provider 为已存在的服务商\n"
                "3. 检查 image_providers.yaml 文件"
            )

        provider_config = providers[provider_name].copy()

        # 验证必要字段
        if not provider_config.get('api_key'):
            logger.error(f"图片服务商 [{provider_name}] 未配置 API Key")
            raise ValueError(
                f"服务商 {provider_name} 未配置 API Key\n"
                "解决方案：\n"
                "1. 在系统设置页面编辑该服务商，填写 API Key\n"
                "2. 或手动在 image_providers.yaml 中添加 api_key 字段"
            )

        provider_type = provider_config.get('type', provider_name)
        if provider_type in ['openai', 'openai_compatible', 'image_api']:
            if not provider_config.get('base_url'):
                logger.error(f"服务商 [{provider_name}] 类型为 {provider_type}，但未配置 base_url")
                raise ValueError(
                    f"服务商 {provider_name} 未配置 Base URL\n"
                    f"服务商类型 {provider_type} 需要配置 base_url\n"
                    "解决方案：在系统设置页面编辑该服务商，填写 Base URL"
                )

        logger.info(f"图片服务商配置验证通过: {provider_name} (type={provider_type})")
        return provider_config

    @classmethod
    def get_image_provider_config_for_user(cls, user_id: int, provider_name: str = None):
        base = cls.get_image_provider_config(provider_name)
        try:
            from backend.db import SessionLocal
            from backend.models import ProviderConfig, UserProviderConfig
            db = SessionLocal()
            try:
                if provider_name is None:
                    provider_name = cls.get_active_image_provider()
                effective = base.copy()
                
                # 1. 先获取数据库中的全局配置
                gp = db.query(ProviderConfig).filter_by(category='image', provider_name=provider_name).first()
                if gp:
                    for k in ["api_key","base_url","model","quality","default_size","default_aspect_ratio","type"]:
                        v = getattr(gp, k)
                        if v:
                            effective[k] = v
                
                # 2. 然后获取用户配置（如果有则覆盖全局配置）
                up = db.query(UserProviderConfig).filter_by(user_id=user_id, category='image', provider_name=provider_name).first()
                if up:
                    # 如果用户配置了api_key，则完全使用用户配置，忽略全局配置
                    if up.api_key:
                        effective = {
                            **effective,
                            **{
                                k: getattr(up, k)
                                for k in ["api_key","base_url","model","quality","default_size","default_aspect_ratio"]
                                if getattr(up, k)
                            }
                        }
                    # 如果用户只配置了部分其他参数，则只覆盖这些参数
                    else:
                        for k in ["base_url","model","quality","default_size","default_aspect_ratio"]:
                            v = getattr(up, k)
                            if v:
                                effective[k] = v
                
                return effective
            finally:
                db.close()
        except Exception:
            return base

    @classmethod
    def get_text_provider_config_for_user(cls, user_id: int, provider_name: str = None):
        config = cls.load_text_providers_config()
        if provider_name is None:
            provider_name = config.get('active_provider', 'google_gemini')
        providers = config.get('providers', {})
        base = providers.get(provider_name, {}).copy() if providers.get(provider_name) else {}
        try:
            from backend.db import SessionLocal
            from backend.models import ProviderConfig, UserProviderConfig
            db = SessionLocal()
            try:
                effective = base.copy()
                
                # 1. 先获取数据库中的全局配置
                gp = db.query(ProviderConfig).filter_by(category='text', provider_name=provider_name).first()
                if gp:
                    for k in ["api_key","base_url","model","type"]:
                        v = getattr(gp, k)
                        if v:
                            effective[k] = v
                
                # 2. 然后获取用户配置（如果有则覆盖全局配置）
                up = db.query(UserProviderConfig).filter_by(user_id=user_id, category='text', provider_name=provider_name).first()
                if up:
                    # 如果用户配置了api_key，则完全使用用户配置，忽略全局配置
                    if up.api_key:
                        effective = {
                            **effective,
                            **{
                                k: getattr(up, k)
                                for k in ["api_key","base_url","model"]
                                if getattr(up, k)
                            }
                        }
                    # 如果用户只配置了部分其他参数，则只覆盖这些参数
                    else:
                        for k in ["base_url","model"]:
                            v = getattr(up, k)
                            if v:
                                effective[k] = v
                
                return effective
            finally:
                db.close()
        except Exception:
            return base

    @classmethod
    def reload_config(cls):
        """重新加载配置（清除缓存）"""
        logger.info("重新加载所有配置...")
        cls._image_providers_config = None
        cls._text_providers_config = None
