# 006-MCP协议：Model Context Protocol 学习笔记

> 【本目录定位】① MCP 是什么、为什么出现？② 协议里有哪些角色与原语？③ 如何手写一个生产可用的 MCP Server？④ 它与 OpenAI 插件 / A2A / OpenAPI 的边界在哪？

## 一、目录树

```text
006-mcp协议/
├── README.md                          # 本文件：导航 + 目录树 + 衔接说明
├── 00-背景篇-MCP前史与全景.md          # 从 M×N 集成地狱到事实标准（含 2026-07-28 新版考据）
├── diagrams/                          # 7 张 SVG 图册
│   ├── 006-01-MCP演进时间线.svg
│   ├── 006-02-三角色架构与M×N对比.svg
│   ├── 006-03-MCP核心概念地图.svg
│   ├── 006-04-一次MCP调用的完整序列.svg
│   ├── 006-05-三原语设计边界.svg
│   ├── 006-06-CTRM库存MCP服务器架构.svg
│   └── 006-07-安全威胁与防御纵深.svg
└── techniques/                        # 八章正文（问题→概念→原理→进阶→实战→生产→对比→自测）
    ├── README.md                      # 章节导览 + 学习路线
    ├── 01-问题篇-M×N集成地狱.md
    ├── 02-概念篇-核心概念精讲.md        # 12 张概念卡
    ├── 03-原理篇-协议架构与生命周期.md
    ├── 04-进阶篇-三原语与传输层.md
    ├── 05-实战篇-手写一个MCP服务器.md   # Python 全代码（FastMCP 风格）
    ├── 06-生产篇-授权安全与部署.md
    ├── 07-对比篇-MCP与OpenAI插件A2A对比.md
    └── 08-自测篇-题库与面试题.md
```

## 二、推荐阅读顺序

| 顺序 | 文件 | 一句话 | 优先级 |
|---|---|---|---|
| 1 | 00-背景篇 | MCP 从哪来、解决什么、现在多主流 | ★★★★★ |
| 2 | techniques/01-问题篇 | M×N 集成地狱，痛点共情 | ★★★★★ |
| 3 | techniques/02-概念篇 | Host/Client/Server、三原语、JSON-RPC | ★★★★★ |
| 4 | techniques/03-原理篇 | 一次调用的完整序列与握手 | ★★★★☆ |
| 5 | techniques/04-进阶篇 | 三原语设计边界 + 传输选型 | ★★★★☆ |
| 6 | techniques/05-实战篇 | 手写 CTRM 库存 MCP Server（Python） | ★★★★★ |
| 7 | techniques/06-生产篇 | OAuth 2.1、投毒攻击、部署与审计 | ★★★★☆ |
| 8 | techniques/07-对比篇 | MCP vs Function Calling vs A2A | ★★★☆☆ |
| 9 | techniques/08-自测篇 | 题库 + 面试题冲刺 | ★★★★☆ |

## 三、与前面主题的衔接

| 前序主题 | 衔接点 |
|---|---|
| **003-向量数据库与RAG** | 检索器（Retriever）可以包成 MCP **resource**——把 CTRM 合同/库存文档的向量检索暴露为 `ctrm://docs/{query}`，任意 MCP 客户端即可复用 |
| **004-Function Calling** | 004 回答"**模型怎么调工具**"（单次 LLM 私有协议）；006 回答"**工具怎么标准化分发**"（跨应用、跨模型的开放协议）。Function calling 是发动机，MCP 是把发动机装进任意汽车的国标接口 |
| **005-Agent框架** | 005 的 Agent（如 LangChain/LangGraph）可通过 MCP client 挂载任意 MCP server，工具生态从"代码内注册"升级为"协议外挂载" |

一句话记住三者关系：**004 教模型用筷子，006 建筷子的行业标准，005 把筷子和碗摆成一桌宴席。**

## 四、贯穿案例

本目录所有示例围绕同一个场景：**把中基集团 CTRM 贸易系统（Java 11 + Vue 2.7 + MySQL）的库存与期货价查询封装成 MCP Server**，让 Claude Desktop、Cursor、WorkBuddy 等任意 Agent 客户端都能即插即用地调用——这正是 MCP "USB-C" 类比的落地版本。完整 Python 代码见 `techniques/05-实战篇`。

## 五、版本考据基线

- 协议版本演进：2024-11-05 → 2025-03-26 → 2025-06-18 → 2025-11-25 → **2026-07-28（截至 2026-09 最新正式版）**
- 2026-07-28 版核心变化：**无状态协议核心**（移除 initialize 握手与 Mcp-Session-Id）、MRTR 多轮往返请求、基于 HTTP 头的路由、Tasks 降级为扩展、**sampling/roots/logging 被标记弃用**、OAuth 硬化（CIMD 取代 DCR）
- 本笔记正文按主流稳定版（2025-06-18 / 2025-11-25）讲解握手与会话模型，并逐章标注 2026-07-28 的差异——面试与生产两端都要知道。

来源：MCP 官方博客《The 2026-07-28 Specification》、modelcontextprotocol.io/specification/2025-11-25/changelog（检索于 2026-09-19）。
