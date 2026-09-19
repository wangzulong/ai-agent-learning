<div align="center">

# 🤖 AI Agent Learning

**从 0 到 1 系统学习 AI Agent 开发的个人学习工作区**

[![Topics](https://img.shields.io/badge/topics-11-6C5CE7?logo=bookstack&logoColor=white)](#-专题目录)
[![Notes](https://img.shields.io/badge/notes-112+-00B894?logo=markdown&logoColor=white)](#-专题目录)
[![Diagrams](https://img.shields.io/badge/diagrams-61-FDCB6E?logo=diagramsdotnet&logoColor=black)](#-专题目录)
[![Printable PDFs](https://img.shields.io/badge/pdf-11-E17055?logo=adobeacrobatreader&logoColor=white)](#-如何使用)
[![License: MIT](https://img.shields.io/badge/license-MIT-0984E3)](LICENSE)

*Prompt 工程 · LLM 基础 · Agent 架构 · 工具调用 · RAG · MCP · 多 Agent · 记忆工程 · 框架实战 · 项目实战 · 论文研读*

</div>

---

## ✨ 这是什么

一套**工程师视角**的 AI Agent 学习笔记，不是资料搬运，而是按经过验证的学习方法重新组织的内容体系：

- **费曼技巧**：每个概念先用「一句话人话 + 生活类比」讲透，再进技术细节
- **黄金圈顺序**：Why（为什么需要）→ What（是什么）→ How（怎么实现/怎么用）→ What-if（深水区）
- **康奈尔笔记**：每章开头【本节问题】引导阅读，结尾【本节自测】闭环检验
- **主动回忆 + 间隔重复**：题库按 L1~L4 分级（概念/理解/应用/面试），附 D1/D3/D7/D21 复习计划
- **生产视角**：每篇都有「生产篇」——成本、安全、评估、失败模式，不止于 Demo
- **出处可溯**：关键结论对齐官方文档与论文（如 mem0 笔记对齐 arXiv 2504.19413 与 docs.mem0.ai）

## 📚 专题目录

| # | 专题 | 核心内容 | 正文目录 | 状态 |
|---|------|----------|----------|------|
| 001 | [Prompt 工程](./001-prompt工程) | 提示解剖学、58 技术地图、评估迭代、注入防御 | `techniques/` | ✅ 8 篇 |
| 002 | [LLM 基础](./002-llm基础) | Token 与推理旅程、训练三部曲、API 成本、2026 模型格局 | `fundamentals/` | ✅ 8 篇 |
| 003 | [Agent 原理与架构](./003-agent原理与架构) | Agent 循环解剖、自主性频谱、编排模式、失败模式防御 | `techniques/` | ✅ 8 篇 |
| 004 | [工具调用与 Function Calling](./004-工具调用与function-calling) | 一次调用的完整旅程、工具设计工程学、三家 SDK 全代码 | `techniques/` | ✅ 8 篇 |
| 005 | [RAG 检索增强](./005-rag检索增强) | 检索管道解剖、分块策略、混合检索与 RRF、AgenticRAG | `techniques/` | ✅ 8 篇 |
| 006 | [MCP 协议](./006-mcp协议) | 三角色架构、三原语、手写 MCP 服务器、安全防御纵深 | `techniques/` | ✅ 8 篇 |
| 007 | [多 Agent 系统](./007-多agent系统) | 协作拓扑、A2A 与 MCP 互补、双 Agent 协作实战 | `techniques/` | ✅ 8 篇 |
| 008 | [记忆与上下文工程](./008-记忆与上下文工程) | Agent 记忆全景 + **mem0 深度笔记**（两阶段流水线/LOCOMO/源码细节） | `mem0/` | ✅ 9 篇 |
| 009 | [Agent 框架实战](./009-agent框架实战) | 框架共性架构、LangGraph 实战、持久化与 Human-in-the-Loop | `frameworks/` | ✅ 8 篇 |
| 010 | [项目实战](./010-项目实战) | 6 个贸易业务场景 Agent 项目设计（CTRM 落地方案） | `projects/` | ✅ 6 篇 |
| 011 | [论文与资料](./011-论文与资料) | 必读十篇精读卡、博客资源地图、12 周阅读路线图 | `papers/` | ✅ 5 篇 |

> 状态说明：✅ 完整 = 八段式齐备；🚧 更新中 = 还在补充后续章节。

## 🗺️ 学习路线图

```
                ┌─────────────────────────────────────────────┐
                │  011 论文与资料（全程伴随，按 12 周路线图推进） │
                └─────────────────────────────────────────────┘

 001 Prompt 工程          —— 先学会跟模型说话
        ↓
 002 LLM 基础             —— 再懂模型怎么工作
        ↓
 003 Agent 原理与架构     —— 然后理解 Agent 循环的本质
        ↓
 004 工具调用 · 005 RAG · 006 MCP · 007 多 Agent · 008 记忆工程
        └──────────（五大能力模块，顺序可并行）──────────┘
        ↓
 009 Agent 框架实战       —— 用框架把这些能力组装起来
        ↓
 010 项目实战             —— 落到 6 个真实业务场景
```

## 📁 统一的专题结构

每个专题都遵循同一套目录约定，找内容零成本：

```
00X-专题名/
├── README.md            # 专题导航：路线图 + 间隔复习计划
├── 00-背景篇-*.md       # 前史与全景（先建立认知地图）
├── <main>/              # 八段式正文（目录名因专题而异）
│   ├── 01-问题篇-*.md   #   Why：痛点场景 + 经济账
│   ├── 02-概念篇-*.md   #   What：费曼式概念卡片
│   ├── 03-原理篇-*.md   #   How：图解 + 伪代码
│   ├── 04-进阶篇-*.md   #   深水区：论文精读/高级技术
│   ├── 05-实战篇-*.md   #   可运行代码 + 排错表
│   ├── 06-生产篇-*.md   #   成本/安全/评估/上线清单
│   ├── 07-对比篇-*.md   #   横向评测 + 选型决策树
│   └── 08-自测篇-*.md   #   L1~L4 题库 + 面试题
├── diagrams/            # SVG 配图（GitHub 可直接预览）
└── *-打印版.pdf         # 整套笔记的 A4 打印版
```

## 🚀 如何使用

1. **按路线图顺序**进入各专题，先读专题 `README.md` 拿到全局地图
2. **读前**扫一眼每章开头的【本节问题】，**读后**合上笔记做【本节自测】
3. 按各专题自测篇里的 **D1 / D3 / D7 / D21 计划**间隔复习，错题回炉
4. 需要**离线/打印阅读**：每个专题根目录都有 A4 打印版 PDF
5. 配图在 `diagrams/` 下，GitHub 网页可直接预览

## 📊 当前规模

| 类型 | 数量 |
|---|---|
| Markdown 笔记 | **116** 篇 |
| SVG 原理图 | **65** 张 |
| 打印版 PDF | **11** 份 |
| 学习专题 | **11** 个（全部八段式齐备） |

## 🛠️ 生成与维护

- 笔记主体在 AI 助手协作下完成：结构化整理 + 官方文档/论文考据 + 人工审校迭代
- 打印版 PDF 由 [WorkBuddy](https://www.workbuddy.cn) 的 md-notes-to-pdf 工具链生成
- 仓库通过 SSH（专用子密钥别名）与 GitHub 同步

## 📄 License

本项目以 [MIT License](./LICENSE) 开源，笔记内容仅供学习交流使用。

---

<div align="center">

**Learning in public.** 持续更新中 🚧

</div>
