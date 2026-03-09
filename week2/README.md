# Week 2 Action Item Extractor

## 项目背景

这是 `modern-software-dev-assignments` 仓库中的 Week 2 作业项目。项目基于 FastAPI、SQLite 和一个极简前端页面，实现“将自由文本会议记录或笔记转换为可执行待办事项”的工作流。

这个项目最初是一个最小可运行示例，随后扩展了以下能力：

- 使用 API 接收原始笔记内容
- 从笔记中提取 action items
- 将笔记和提取结果持久化到 SQLite
- 标记 action item 完成状态
- 通过 Ollama 调用本地大模型完成结构化抽取

## 项目目的

这个项目的目标是演示一个从“非结构化文本”到“结构化任务列表”的完整后端流程，适合作为以下场景的练习项目：

- 会议纪要整理
- 任务拆解与跟进
- FastAPI + SQLite 的基础工程实践
- 本地 LLM 接入与结构化输出

## 技术栈

- Python 3.10+
- FastAPI
- Pydantic v2
- SQLite
- Uvicorn
- Ollama Python SDK
- 原生 HTML / JavaScript 前端

## 项目结构

```text
week2/
├── app/
│   ├── config.py              # 应用配置与环境变量
│   ├── db.py                  # SQLite 数据访问层
│   ├── main.py                # FastAPI 应用入口
│   ├── routers/
│   │   ├── action_items.py    # action item 相关接口
│   │   └── notes.py           # note 相关接口
│   ├── schemas.py             # 请求/响应模型
│   └── services/
│       └── extract.py         # action item 抽取逻辑
├── frontend/
│   └── index.html             # 极简前端页面
├── tests/                     # 单元测试
├── assignment.md              # 作业说明
└── writeup.md                 # 作业记录
```

## 核心功能

- 提交一段笔记文本并抽取待办事项
- 可选保存原始笔记到数据库
- 保存抽取出的 action items 到数据库
- 查询单条 note
- 查询 action item 列表
- 更新 action item 的完成状态
- 提供一个简单前端页面用于手动体验接口

说明：

- 当前代码中 `/action-items/extract` 与 `/action-items/extract-llm` 最终都会走 LLM 抽取逻辑。
- LLM 功能依赖本地 Ollama 服务可用。

## 环境准备

本项目依赖定义在仓库根目录的 `pyproject.toml` 中，因此推荐在仓库根目录执行安装和启动命令。

### 1. 安装依赖

在仓库根目录执行：

```bash
poetry install
```

如果你不使用 Poetry，也可以在当前 Python 环境中自行安装这些依赖：`fastapi`、`uvicorn`、`pydantic`、`python-dotenv`、`ollama`、`pytest`。

### 2. 准备 Ollama

如果你要使用抽取接口，需要先安装并启动 Ollama，并拉取一个模型，例如：

```bash
ollama pull llama3.2
```

项目默认模型名来自环境变量 `OLLAMA_MODEL`，默认值为 `llama3.2`。

## 启动方式

### 从仓库根目录启动

```bash
poetry run uvicorn week2.app.main:app --reload
```

如果依赖已经安装到当前 Python 环境，也可以在仓库根目录执行：

```bash
python -m uvicorn week2.app.main:app --reload
```

启动后访问：

- 应用首页：http://127.0.0.1:8000/
- Swagger 文档：http://127.0.0.1:8000/docs
- ReDoc 文档：http://127.0.0.1:8000/redoc

### 数据文件

默认情况下，SQLite 文件位于：

```text
week2/data/app.db
```

## 环境变量

可通过 `.env` 或系统环境变量覆盖以下配置：

- `APP_TITLE`：应用标题，默认 `Action Item Extractor`
- `WEEK2_DB_PATH`：SQLite 数据库文件路径，默认 `week2/data/app.db`
- `OLLAMA_MODEL`：Ollama 模型名，默认 `llama3.2`

示例：

```bash
export OLLAMA_MODEL=llama3.2
export WEEK2_DB_PATH=week2/data/app.db
```

## API 接口说明

### 1. 创建笔记

`POST /notes`

请求体：

```json
{
  "content": "Discuss roadmap and write follow-up tasks"
}
```

返回：

```json
{
  "id": 1,
  "content": "Discuss roadmap and write follow-up tasks",
  "created_at": "2026-03-09 15:00:00"
}
```

### 2. 查询单条笔记

`GET /notes/{note_id}`

说明：根据 ID 查询已保存的 note，不存在时返回 `404`。

### 3. 抽取 action items

`POST /action-items/extract`

请求体：

```json
{
  "text": "- [ ] Set up database\n- Write tests",
  "save_note": true
}
```

返回：

```json
{
  "note_id": 1,
  "items": [
    { "id": 1, "text": "Set up database" },
    { "id": 2, "text": "Write tests" }
  ]
}
```

### 4. 使用 LLM 抽取 action items

`POST /action-items/extract-llm`

请求格式与 `/action-items/extract` 相同。

说明：当前实现中，这个接口和普通抽取接口最终都使用 LLM 服务完成抽取。

### 5. 查询 action items

`GET /action-items`

可选查询参数：

- `note_id`：只返回某条 note 关联的 action items

示例：

```text
GET /action-items?note_id=1
```

### 6. 标记 action item 完成/未完成

`POST /action-items/{action_item_id}/done`

请求体：

```json
{
  "done": true
}
```

返回：

```json
{
  "id": 1,
  "done": true
}
```

## 前端使用说明

访问首页后，可以直接在文本框中粘贴会议记录或任务笔记，然后：

- 勾选 `Save as note` 以保存原始笔记
- 点击 `Extract` 触发抽取
- 在结果区勾选复选框，更新 action item 完成状态

当前前端是一个最小示例页，主要用于验证后端接口联通性。

## 运行测试

在仓库根目录执行：

```bash
poetry run pytest week2/tests -q
```

如果你当前就在 `week2/` 目录下，也可以直接执行：

```bash
python -m pytest tests -q
```

说明：

- 测试覆盖了抽取逻辑、请求模型校验和部分路由行为。
- 测试中对 LLM 调用做了 mock，因此运行测试通常不需要本地 Ollama 服务在线。



## 前端测试用例

```
there are todo list
 - write a front-web
- [] write a backend serve
write test
fix the bug ,re-test the code,wite a readme file
```
## 常见问题

### 1. 启动后抽取接口返回 503

通常表示 LLM 抽取失败，常见原因包括：

- 未安装 `ollama` Python 包
- 本地 Ollama 服务未启动
- 配置的模型不存在
- 模型名称与 `OLLAMA_MODEL` 不一致

### 2. 数据库文件没有生成

应用启动时会自动初始化数据库，并在需要时创建 `data/` 目录。请确认进程对目标目录有写权限。

## 后续可扩展方向

- 为 notes 补充“列表查询”接口
- 区分规则抽取与 LLM 抽取两套实现
- 前端增加 LLM 抽取按钮和笔记列表展示
- 增加集成测试与错误场景测试
- 为 action items 增加删除、编辑、过滤能力

