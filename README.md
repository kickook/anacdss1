# 麻醉生命体征预警系统

该仓库提供了一个麻醉生命体征预警系统的基础架构示例，包含基于 Python Flask 的后端与具备科技感的前端原型。系统旨在帮助麻醉医生在多个手术间对患者进行实时监测，并在超过预警阈值时调用 Dify LLM 获取处理建议。

## 架构概览

- **后端（`backend/`）**：
  - 使用 Flask + SQLAlchemy 提供 REST API。
  - 支持手术间、设备、监测参数、预警阈值的配置。
  - 集成 Dify API，触发预警时将患者资料、参数及告警信息发送给 LLM 获取建议。
- **前端（`frontend/`）**：
  - 使用原生 HTML/CSS/JS 搭建科技感监控面板，可选择手术间并展示实时模拟参数。
  - 预留入口用于配置预警及患者资料。

## 快速开始

1. **后端**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   export DIFY_API_KEY="your-key"
   export DIFY_APP_ID="your-app-id"
   python app.py
   ```

2. **前端**
   - 直接在浏览器中打开 `frontend/index.html`，即可体验监测面板。默认会请求本地 8000 端口的后端接口。

## 后续扩展建议

- 对接真实的监护仪、麻醉机、注射泵 API，封装为独立的设备适配器模块。
- 增加用户与权限管理接口，实现麻醉科室内不同角色的访问控制。
- 引入 WebSocket 或消息队列，实现实时推送和多手术间并发监测。
- 前端可以改造成基于 React/Vue 的 SPA，整合图表、趋势线和 Dify 的建议展示。

该项目为最小可运行原型，开发者可在此基础上继续扩展以满足实际临床场景需求。
