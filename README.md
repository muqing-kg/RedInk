![](images/logo.png)

---

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Vue 3](https://img.shields.io/badge/vue-3.x-green.svg)](https://vuejs.org/)

# 红墨 - 小红书AI图文生成器

> 让传播不再需要门槛，让创作从未如此简单

![](images/index.gif)

<p align="center">
  <em>红墨首页</em>
</p>

<p align="center">
  <img src="images/showcase-grid.png" alt="使用红墨生成的各类小红书封面" width="600"/>
</p>

<p align="center">
  <em>使用红墨生成的各类小红书封面 - AI驱动，风格统一，文字准确</em>
</p>



## 写在前面

前段时间默子在 Linux.do 发了一个用 Nano banana Pro 做 PPT 的帖子,收获了 600 多个赞。很多人用🍌Nano banana Pro 去做产品宣传图、直接生成漫画等等。我就在想:**为什么不拿🍌2来做点更功利、更刺激的事情?**

于是就有了这个项目。一句话一张图片生成小红书图文

---

## ✨ 效果展示

### 输入一句话,就能生成完整的小红书图文

#### 提示词：秋季显白美甲（暗广一个：默子牌美甲），图片 是我的小红书主页。符合我的风格生成

#### 同时我还截图了我的小红书主页，包括我的头像，签名，背景，姓名什么的

![示例1](./images/example-1.png)

#### 然后等待10-20秒后，就会有每一页的大纲，大家可以根据的自己的需求去调整页面顺序（不建议），自定义每一个页面的内容（这个很建议）

![示例2](./images/example-2.png)

#### 首先生成的是封面页

![示例3](./images/example-3.png)

#### 然后稍等一会儿后，会生成后面的所有页面（这里是并发生成的所有页面（默认是15个），如果大家的API供应商无法支持高并发的话，记得要去改一下设置）

![示例4](./images/example-4.png)

## ✨ 核心功能

### 📝 智能文案生成
- 基于 Google Gemini 3 的强大文案生成能力
- 自动生成符合小红书风格的标题和内容
- 支持自定义每一页的描述和调整

### 🎨 AI 图片生成
- 支持多种图片生成服务提供商
- 并行/串行生成模式切换，适配不同 API 配额
- 支持上传参考图片，保持品牌视觉风格
- 支持单张图片重新生成，不满意就换

### 💾 统一数据管理
- 所有数据持久化存储在 `/data` 目录
- SQLite 数据库管理，数据安全可靠
- 历史记录完整保存，支持随时查看和编辑
- 生成的图片自动分类存储

### ⚙️ 灵活配置管理
- 支持 Web 界面可视化配置
- 支持 YAML 文件配置
- 支持环境变量文件配置
- API Key 脱敏显示，保护密钥安全

### 🚀 快速部署
- Docker 一键部署，无需复杂配置
- 统一的 `/data` 目录挂载，管理方便
- 支持本地开发部署

### 📱 优秀的用户体验
- 现代化的 Vue 3 + TypeScript 前端
- 实时生成进度展示
- 一键下载所有生成的图片
- 历史记录便捷管理

---

## 🏗️ 技术架构

### 整体架构

红墨采用前后端分离的架构设计，前端使用现代化的 Vue 3 + TypeScript 技术栈，后端采用 Python Flask 框架，数据持久化存储在 SQLite 数据库中，所有用户数据和配置统一管理在 `/data` 目录下。

### 后端架构

- **语言**: Python 3.11+
- **框架**: Flask
- **AI 模型**:
  - Gemini 3 (文案生成)
  - 🍌Nano banana Pro (图片生成)
  - 支持多种 AI 服务商扩展
- **包管理**: uv
- **数据库**: SQLite (存储在 `/data/redink.db`)
- **路由设计**: 模块化蓝图设计
  - `/api/generation`: 生成相关 API
  - `/api/images`: 图片管理 API
  - `/api/history`: 历史记录 API
  - `/api/config`: 配置管理 API

### 前端架构

- **框架**: Vue 3 + TypeScript
- **构建**: Vite
- **状态管理**: Pinia
- **路由**: Vue Router
- **UI 组件**: 自定义组件库
- **核心页面**:
  - 首页: 主题输入和参考图片上传
  - 大纲页: 内容大纲编辑
  - 生成页: 图片生成和展示
  - 历史页: 历史记录管理
  - 设置页: API 配置管理

### 数据管理

- **统一存储目录**: `/data`
  - `/data/redink.db`: SQLite 数据库
  - `/data/output`: 生成的图片存储
  - `/data/history`: 历史记录存储
  - `/data/text_providers.yaml`: 文本生成配置
  - `/data/image_providers.yaml`: 图片生成配置
  - `/data/.env`: 环境变量配置

### 配置管理

- **配置加载顺序**: `/data/.env` → 系统环境变量 → 默认配置
- **配置持久化**: 所有配置自动保存到 `/data` 目录
- **配置更新**: 支持热更新，无需重启服务

### 核心功能模块

1. **文案生成模块**: 调用 AI 模型生成小红书风格的文案
2. **图片生成模块**: 调用图片生成 API 生成符合要求的图片
3. **历史记录模块**: 管理和查询历史创作记录
4. **配置管理模块**: 管理 API 配置和系统设置
5. **文件管理模块**: 管理生成的图片和历史记录文件

### 部署架构

- **Docker 部署**: 单容器部署，所有服务和数据统一管理
- **端口暴露**: 默认 12398
- **持久化存储**: 挂载 `/data` 目录实现数据持久化
- **环境变量**: 支持通过 `.env` 文件配置

### 目录结构

```
RedInk/
├── backend/                  # 后端代码
│   ├── app.py                # 应用入口
│   ├── config.py             # 配置管理
│   ├── db.py                 # 数据库连接
│   ├── models/               # 数据模型
│   ├── services/             # 业务逻辑服务
│   │   ├── image.py          # 图片生成服务
│   │   └── text.py           # 文本生成服务
│   └── routes/               # API 路由
├── frontend/                 # 前端代码
│   ├── src/
│   │   ├── components/       # Vue 组件
│   │   ├── views/            # 页面组件
│   │   ├── store/            # Pinia 状态管理
│   │   └── utils/            # 工具函数
│   ├── vite.config.ts        # Vite 配置
│   └── package.json          # 前端依赖
├── data/                     # 数据存储目录（运行时创建）
├── Dockerfile                # Docker 构建文件
├── docker-compose.yml        # Docker Compose 配置
├── README.md                 # 项目说明文档
└── requirements.txt          # Python 依赖
```

---

## 📦 如何自己部署

### 方式一：Docker 部署（推荐）

**最简单的部署方式，一行命令即可启动：**

```bash
docker run -d -p 12398:12398 -v ./data:/data muqingw/redink:latest
```

访问 http://localhost:12398，在 Web 界面的**设置页面**配置你的 API Key 即可使用。

**使用 docker-compose（可选）：**

下载 [docker-compose.yml](https://github.com/HisMax/RedInk/blob/main/docker-compose.yml) 后：

```bash
docker-compose up -d
```

**Docker 部署说明：**
- 容器内不包含任何 API Key，需要在 Web 界面配置
- 使用 `-v ./data:/data` 统一持久化存储，包括：
  - 历史记录（/data/history）
  - 生成的图片（/data/output）
  - 配置文件（/data/text_providers.yaml 和 /data/image_providers.yaml）
  - SQLite 数据库（/data/redink.db）
  - 环境变量文件（/data/.env，可选）

---

### 方式二：本地开发部署

**前置要求：**
- Python 3.11+
- Node.js 18+
- pnpm
- uv

### 1. 克隆项目
```bash
git clone https://github.com/HisMax/RedInk.git
cd RedInk
```

### 2. 配置 API 服务

复制配置模板文件：
```bash
cp text_providers.yaml.example text_providers.yaml
cp image_providers.yaml.example image_providers.yaml
```

编辑配置文件，填入你的 API Key 和服务配置。也可以启动后在 Web 界面的**设置页面**进行配置。

### 3. 安装后端依赖
```bash
uv sync
```

### 4. 安装前端依赖
```bash
cd frontend
pnpm install
```

### 5. 启动服务

**启动后端:**
```bash
uv run python -m backend.app
```
访问: http://localhost:12398

**启动前端:**
```bash
cd frontend
pnpm dev
```
访问: http://localhost:5173

---

## 🎮 使用指南

### 快速开始

#### 1. 部署服务

**Docker 部署（推荐）：**
```bash
docker run -d -p 12398:12398 -v ./data:/data muqingw/redink:latest
```

**本地开发部署：**
详见「本地开发部署」章节

#### 2. 访问服务

打开浏览器，访问 http://localhost:12398

#### 3. 配置 API 服务

1. 点击页面右上角的「设置」图标
2. 在「文本生成配置」中选择服务商并填写 API Key
3. 在「图片生成配置」中选择服务商并填写 API Key
4. 点击「保存配置」

### 基础使用流程

1. **输入主题**: 在首页输入想要创作的主题,如"如何在家做拿铁"
   - 可选择上传参考图片，保持品牌视觉风格
   - 可调整生成页面数量（默认 15 页）

2. **生成大纲**: 点击「生成大纲」，AI 自动生成完整的内容大纲
   - 生成时间约 10-20 秒
   - 系统会根据主题生成符合小红书风格的内容结构

3. **编辑确认**: 在大纲页面可以：
   - 调整页面顺序
   - 编辑每一页的标题和内容描述
   - 删除不需要的页面
   - 添加新页面

4. **生成图片**: 点击「开始生成」，实时查看生成进度
   - 生成时间根据页面数量和 API 速度而定
   - 可在生成过程中查看已完成的图片
   - 支持高并发/串行生成模式切换

5. **查看和管理**:
   - 在「生成页」查看所有生成的图片
   - 点击「下载」按钮获取所有图片
   - 点击「保存到历史」将当前创作保存到历史记录

### 历史记录管理

1. **查看历史**: 点击首页的「时光机」图标进入历史记录页面
2. **重新编辑**: 点击历史记录卡片，可重新编辑大纲和生成图片
3. **重新生成**: 选择历史记录中的某个创作，点击「重新生成」
4. **删除历史**: 可删除不需要的历史记录

### 进阶使用技巧

- **上传参考图片**: 适合品牌方，保持品牌视觉风格一致性
- **修改描述词**: 精确控制每一页的内容、构图和风格
- **单页重新生成**: 对不满意的页面单独重新生成，无需重新生成全部
- **调整生成参数**: 根据 API 配额情况调整高并发模式
- **配置持久化**: 所有配置自动保存到 `/data` 目录，重启服务不丢失

### 常见问题

**Q: 生成的图片不满意怎么办？**
A: 可以点击图片下方的「重新生成」按钮，单独重新生成该页面的图片

**Q: 生成过程中可以离开页面吗？**
A: 建议不要离开页面，否则可能导致生成中断

**Q: 如何修改生成的页面数量？**
A: 在首页生成大纲前，可调整「页面数量」参数

**Q: 历史记录保存在哪里？**
A: 历史记录保存在 `/data/history` 目录，生成的图片保存在 `/data/output` 目录

---

## 🔧 配置说明

### 配置方式

项目支持三种配置方式，优先级从高到低：

1. **Web 界面配置（推荐）**：启动服务后，在设置页面可视化配置
2. **YAML 文件配置**：直接编辑 `/data` 目录下的配置文件
3. **环境变量配置**：通过 `.env` 文件或系统环境变量配置

### 配置文件位置

配置文件默认存储在 `/data` 目录下：
- 文本生成配置：`/data/text_providers.yaml`
- 图片生成配置：`/data/image_providers.yaml`
- 环境变量文件：`/data/.env`（可选）

### 文本生成配置

配置文件: `/data/text_providers.yaml`

```yaml
# 当前激活的服务商
active_provider: openai

providers:
  # OpenAI 官方或兼容接口
  openai:
    type: openai_compatible
    api_key: sk-xxxxxxxxxxxxxxxxxxxx
    base_url: https://api.openai.com/v1
    model: gpt-4o

  # Google Gemini（原生接口）
  gemini:
    type: google_gemini
    api_key: AIzaxxxxxxxxxxxxxxxxxxxxxxxxx
    model: gemini-2.0-flash
```

### 图片生成配置

配置文件: `/data/image_providers.yaml`

```yaml
# 当前激活的服务商
active_provider: gemini

providers:
  # Google Gemini 图片生成
  gemini:
    type: google_genai
    api_key: AIzaxxxxxxxxxxxxxxxxxxxxxxxxx
    model: gemini-3-pro-image-preview
    high_concurrency: false  # 高并发模式

  # OpenAI 兼容接口
  openai_image:
    type: image_api
    api_key: sk-xxxxxxxxxxxxxxxxxxxx
    base_url: https://your-api-endpoint.com
    model: dall-e-3
    high_concurrency: false
```

### 环境变量配置

环境变量文件: `/data/.env`（可选）

```env
# 应用配置
PORT=12398
HOST=0.0.0.0

# 数据库配置
DATABASE_URL=sqlite:///redink.db

# 日志配置
LOG_LEVEL=INFO

# API 配置
GEMINI_API_KEY=AIzaxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 高并发模式说明

- **关闭（默认）**：图片逐张生成，适合 GCP 300$ 试用账号或有速率限制的 API
- **开启**：图片并行生成（最多15张同时），速度更快，但需要 API 支持高并发

⚠️ **GCP 300$ 试用账号不建议启用高并发**，可能会触发速率限制导致生成失败。

---

## 📡 API 说明

### 认证 API

| 接口 | 方法 | 路径 | 功能描述 |
|------|------|------|----------|
| 注册 | POST | `/api/auth/register` | 用户注册 |
| 登录 | POST | `/api/auth/login` | 用户登录 |
| 获取当前用户 | GET | `/api/auth/me` | 获取当前登录用户信息 |
| 修改密码 | POST | `/api/auth/change-password` | 修改用户密码 |

### 大纲生成 API

| 接口 | 方法 | 路径 | 功能描述 |
|------|------|------|----------|
| 生成大纲 | POST | `/api/outline` | 生成小红书图文大纲，支持图片上传 |

### 图片生成 API

| 接口 | 方法 | 路径 | 功能描述 |
|------|------|------|----------|
| 批量生成图片 | POST | `/api/generate` | 批量生成图片，SSE 流式返回结果 |
| 获取图片 | GET | `/api/images/<task_id>/<filename>` | 获取生成的图片文件 |
| 重试单张图片 | POST | `/api/retry` | 重试生成单张失败的图片 |
| 批量重试失败图片 | POST | `/api/retry-failed` | 批量重试失败的图片，SSE 流式返回 |
| 重新生成图片 | POST | `/api/regenerate` | 重新生成图片（即使成功的也可以重新生成） |
| 获取任务状态 | GET | `/api/task/<task_id>` | 获取图片生成任务状态 |
| 健康检查 | GET | `/api/health` | 图片服务健康检查 |

### 历史记录 API

| 接口 | 方法 | 路径 | 功能描述 |
|------|------|------|----------|
| 获取历史记录列表 | GET | `/api/history` | 获取历史记录列表，支持分页和筛选 |
| 创建历史记录 | POST | `/api/history` | 创建新的历史记录 |
| 获取历史记录详情 | GET | `/api/history/<record_id>` | 获取历史记录详细信息 |
| 更新历史记录 | PUT | `/api/history/<record_id>` | 更新历史记录信息 |
| 删除历史记录 | DELETE | `/api/history/<record_id>` | 删除历史记录 |
| 搜索历史记录 | GET | `/api/history/search` | 根据关键词搜索历史记录 |
| 获取历史记录统计 | GET | `/api/history/stats` | 获取历史记录统计信息 |
| 扫描任务图片 | GET | `/api/history/scan/<task_id>` | 扫描单个任务并同步图片列表 |
| 下载历史记录图片 | GET | `/api/history/<record_id>/download` | 下载历史记录的所有图片为 ZIP 文件 |
| 获取即将过期记录 | GET | `/api/history/expiring-soon` | 获取即将过期的历史记录 |

### 配置管理 API

| 接口 | 方法 | 路径 | 功能描述 |
|------|------|------|----------|
| 获取配置 | GET | `/api/config` | 获取当前配置 |
| 更新配置 | POST | `/api/config` | 更新配置信息 |
| 测试服务商连接 | POST | `/api/config/test` | 测试服务商连接是否正常 |

### 服务商管理 API（管理员）

| 接口 | 方法 | 路径 | 功能描述 |
|------|------|------|----------|
| 创建服务商 | POST | `/api/admin/providers` | 管理员创建服务商配置 |
| 用户创建服务商 | POST | `/api/user/providers` | 用户创建服务商配置 |
| 同步服务商 | POST | `/api/admin/providers/sync` | 管理员同步服务商配置 |
| 获取用户服务商 | GET | `/api/user/providers` | 获取用户的服务商配置 |
| 获取管理员用户 | GET | `/api/admin/users` | 获取管理员用户列表 |
| 更新管理员用户 | PUT | `/api/admin/users/<int:user_id>` | 管理员更新用户信息 |
| 删除管理员用户 | DELETE | `/api/admin/users/<int:user_id>` | 管理员删除用户 |

### API 认证

- 大部分 API 需要认证，使用 JWT Token
- Token 可以通过 `Authorization: Bearer <token>` 头传递
- 部分图片相关 API 支持通过 `token` 查询参数传递

### 响应格式

成功响应：
```json
{
  "success": true,
  "data": {...}
}
```

失败响应：
```json
{
  "success": false,
  "error": "错误消息"
}
```

---

## ⚠️ 注意事项

1. **API 配额限制**:
   - 注意 Gemini 和图片生成 API 的调用配额
   - GCP 试用账号建议关闭高并发模式

2. **生成时间**:
   - 图片生成需要时间,请耐心等待（不要离开页面）

---

## 🤝 参与贡献

欢迎提交 Issue 和 Pull Request!

如果这个项目对你有帮助,欢迎给个 Star ⭐

### 未来计划
- [ ] 支持更多图片格式，例如一句话生成一套PPT什么的
- [x] 历史记录管理优化
- [ ] 导出为各种格式(PDF、长图等)

---

## 更新日志

### v1.5.0 (2025-12-11)
- 🏗️ 统一数据持久化存储：所有用户数据、配置文件和数据库统一管理在 `/data` 目录下
- 🔧 更新 Docker 配置：
  - 使用 `muqingw/redink` 作为 Docker Hub 镜像名称
  - 统一挂载 `/data` 目录实现数据持久化
  - 优化 Dockerfile，自动创建 `/data` 目录结构
- 🔧 配置文件管理优化：
  - 配置文件默认存储路径变更为 `/data` 目录
  - 支持 `/data/.env` 环境变量文件
  - 配置加载顺序优化：`/data/.env` → 系统环境变量 → 默认配置
- 🔧 数据库存储更新：SQLite 数据库统一存储在 `/data/redink.db`
- 🔧 路由和服务更新：
  - 优化配置管理 API，支持配置文件自动保存
  - 修复卡片显示问题，优化前端渲染逻辑
  - 改进按钮定位和 UI 设计
- 📝 更新 README 文档：
  - 详细的 API 说明文档
  - 统一的部署和使用指南
  - 完整的配置说明
  - 项目架构详细描述

### v1.4.0 (2025-11-30)
- 🏗️ 后端架构重构：拆分单体路由为模块化蓝图（history、images、generation、outline、config）
- 🏗️ 前端组件重构：提取可复用组件（ImageGalleryModal、OutlineModal、ShowcaseBackground等）
- ✨ 优化首页设计，移除冗余内容区块
- ✨ 背景图片预加载和渐入动画，提升加载体验
- ✨ 历史记录持久化支持（Docker部署）
- 🔧 修复历史记录预览和大纲查看功能
- 🔧 优化Modal组件可见性控制
- 🧪 新增65个后端单元测试

### v1.3.0 (2025-11-26)
- ✨ 新增 Docker 支持，一键部署
- ✨ 发布官方 Docker 镜像到 Docker Hub: `muqingw/redink`
- 🔧 Flask 自动检测前端构建产物，支持单容器部署
- 🔧 Docker 镜像内置空白配置模板，保护 API Key 安全
- 📝 更新 README，添加 Docker 部署说明

### v1.2.0 (2025-11-26)
- ✨ 新增版权信息展示，所有页面显示开源协议和项目链接
- ✨ 优化图片重新生成功能，支持单张图片重绘
- ✨ 重新生成图片时保持风格一致，传递完整上下文（封面图、大纲、用户输入）
- ✨ 修复图片缓存问题，重新生成的图片立即刷新显示
- ✨ 统一文本生成客户端接口，支持 Google Gemini 和 OpenAI 兼容接口自动切换
- ✨ 新增 Web 界面配置功能，可视化管理 API 服务商
- ✨ 新增高并发模式开关，适配不同 API 配额
- ✨ API Key 脱敏显示，保护密钥安全
- ✨ 配置自动保存，修改即时生效
- 🔧 调整默认 max_output_tokens 为 8000，兼容更多模型限制
- 🔧 优化前端路由和页面布局，提升用户体验
- 🔧 简化配置文件结构，移除冗余参数
- 🔧 优化历史记录图片显示，使用缩略图节省带宽
- 🔧 历史记录重新生成时自动从文件系统加载封面图作为参考
- 🐛 修复 `store.updateImage` 方法缺失导致的重新生成失败问题
- 🐛 修复历史记录加载时图片 URL 拼接错误
- 🐛 修复下载功能中原图参数处理问题
- 🐛 修复图片加载 500 错误问题

---

## 交流讨论与赞助

- **GitHub Issues**: [https://github.com/HisMax/RedInk/issues](https://github.com/HisMax/RedInk/issues)

### 联系作者

- **Email**: histonemax@gmail.com
- **微信**: Histone2024（添加请注明来意）
- **GitHub**: [@HisMax](https://github.com/HisMax)

### 用爱发电，如果可以，请默子喝一杯☕️咖啡吧

<img src="images/coffee.jpg" alt="赞赏码" width="300"/>

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=HisMax/RedInk&type=Date)](https://star-history.com/#HisMax/RedInk&Date)

---

## 📄 开源协议

### 个人使用 - CC BY-NC-SA 4.0

本项目采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 协议进行开源

**你可以自由地：**
- ✅ **个人使用** - 用于学习、研究、个人项目
- ✅ **分享** - 在任何媒介以任何形式复制、发行本作品
- ✅ **修改** - 修改、转换或以本作品为基础进行创作

**但需要遵守以下条款：**
- 📝 **署名** - 必须给出适当的署名，提供指向本协议的链接，同时标明是否对原始作品作了修改
- 🚫 **非商业性使用** - 不得将本作品用于商业目的
- 🔄 **相同方式共享** - 如果你修改、转换或以本作品为基础进行创作，你必须以相同的协议分发你的作品

### 商业授权

如果你希望将本项目用于**商业目的**（包括但不限于）：
- 提供付费服务
- 集成到商业产品
- 作为 SaaS 服务运营
- 其他盈利性用途

**请联系作者获取商业授权：**
- 📧 Email: histonemax@gmail.com
- 💬 微信: Histone2024（请注明"商业授权咨询"）

默子会根据你的具体使用场景提供灵活的商业授权方案。

---

### 免责声明

本软件按"原样"提供，不提供任何形式的明示或暗示担保，包括但不限于适销性、特定用途的适用性和非侵权性的担保。在任何情况下，作者或版权持有人均不对任何索赔、损害或其他责任负责。

---

## 🙏 致谢

- [Google Gemini](https://ai.google.dev/) - 强大的文案生成能力
- 图片生成服务提供商 - 惊艳的图片生成效果
- [Linux.do](https://linux.do/) - 优秀的开发者社区

---

## 👨‍💻 作者

**默子 (Histone)** - AI 创业者 | Python & 深度学习

- 🏠 位置: 中国杭州
- 🚀 状态: 创业中
- 💡 专注: Transformers、GANs、多模态AI
- 📧 Email: histonemax@gmail.com
- 💬 微信: Histone2024
- 🐙 GitHub: [@HisMax](https://github.com/HisMax)

*"让 AI 帮我们做更有创造力的事"*

---

**如果这个项目帮到了你,欢迎分享给更多人!** ⭐

有任何问题或建议,欢迎提 Issue 或者在 Linux.do 原帖讨论!
