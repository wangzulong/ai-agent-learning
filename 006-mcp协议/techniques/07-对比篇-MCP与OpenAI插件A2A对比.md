# 07-对比篇：MCP 与 Function Calling、A2A、OpenAPI

> 【本节问题】① MCP 与 OpenAI function calling 到底谁替代谁？② MCP 与 A2A 是竞争还是互补？③ 有了 OpenAPI/Swagger 为什么还要 MCP？④ CTRM 项目里应该怎么选？

## 1. 一张总表定坐标

| 维度 | MCP | OpenAI Function Calling（004） | OpenAPI/Swagger | A2A（007 详述） |
|---|---|---|---|---|
| 解决什么 | 工具/数据的**跨应用标准化分发** | 模型**表达**要调哪个函数 | REST API 的**接口描述** | **Agent 之间**互操作 |
| 层级 | 应用↔工具 协议 | 模型内部机制 | API 文档规范 | Agent↔Agent 协议 |
| 谁实现 | Host 内置 Client + 独立 Server | 各模型厂商内置 | 工具生成 SDK | Agent 平台实现 |
| 跨应用复用 | 是（写一次任意客户端用） | 否（单应用私有） | 部分（仍要写胶水） | 是（Agent 级） |
| 是否感知 LLM | 是（为模型消费设计） | 是 | 否（为人/代码设计） | 是 |
| 传输 | stdio / Streamable HTTP | 依附各 API | HTTP | HTTP(S) + Agent Card |

## 2. MCP vs Function Calling：发动机 vs 国标油口

【一句话人话】function calling 是"模型怎么表达要调工具"的**私有机制**（每家模型厂一套格式）；MCP 是"工具怎么被发布、发现、传输"的**开放标准**。两者是**上下游**，不是竞争。

```text
用户问题 → [MCP Client] tools/list → 工具Schema ─翻译→ 模型厂 function 定义 → 模型决策
模型: "调 query_inventory(SH,CU-2026)" → [MCP Client] tools/call → MCP Server → 结果回填 → 模型作答
```

证据链：任一 MCP Host（Claude/Cursor）内部，MCP tool 最终被**翻译成本家模型的 function calling 格式**；OpenAI Agents SDK 支持 MCP 作为工具来源。所以 004 与 006 的关系是：**004 的 tools 定义是单模型私有协议，MCP 是跨应用分发标准**。

面试金句："function calling 决定模型会不会用工具，MCP 决定全世界的工具能不能插进来。"

## 3. MCP vs A2A：工具互操作 vs Agent 互操作

| 判据 | MCP | A2A |
|---|---|---|
| 对端身份 | 工具/数据（无自主目标） | Agent（有角色、有目标、可协商） |
| 交互粒度 | 单个原语调用（tool/resource/prompt） | 任务（task）级、多轮、长时 |
| 状态/异步 | 无状态为主（新版），工具无自主性 | 任务生命周期、进度通知是核心 |
| 类比 | USB-C：插上就供电/读盘 | 名片交换：先看 Agent Card 再谈合作 |
| 典型问题 | "帮我查 SH 仓库存" | "让集团风控 Agent 与贸易 Agent 协商对冲方案" |

结论：**互补**。一个复杂 Agent 常同时是 MCP Client（接工具）与 A2A 上的节点（与其他 Agent 协作）。A2A 详述见 007 主题。

## 4. MCP vs OpenAPI/LLMs.txt：给机器读的描述 ≠ 给模型用的通道

- OpenAPI 描述**接口长什么样**，但不解决：鉴权委托（OAuth resource server 模式）、传输（stdio/HTTP）、能力协商、模型侧审批 UX、变更通知——这些 MCP 全包了；
- 有了 OpenAPI 仍需手写"调用胶水+鉴权+错误处理"；MCP SDK 直接把这些做成协议层；
- LLMs.txt（给模型读的站点索引）只是"发现"材料，无调用语义；
- 反向视角：企业已有大量 OpenAPI 时，可用网关把 REST 包装成 MCP Server（业界已有成熟转换层），CTRM 老接口即可低成本入列。

## 5. CTRM 选型决策树

```text
要接的对象是另一个"有自主目标的 Agent"？ ──是──→ A2A（或同时用两者）
        │否
要跨多个 AI 应用复用同一工具/数据？ ──是──→ 包 MCP Server（05 章）
        │否（只在单一应用内、单一模型上）
只是某个模型的一次性调用？ ──是──→ 直接 function calling（004）
        │
需要给模型描述已有 REST API？ → OpenAPI 转换为 MCP Server 更划算
```

优先级建议：先 function calling 跑通单应用原型 → 工具价值确认后包 MCP Server 分发 → 涉及跨 Agent 协作再上 A2A。**不要为了用协议而用协议。**

## 【本节自测】

1. **MCP 与 function calling 的关系？** 要点：上下游互补——MCP 分发工具并翻译为各模型的 function 定义，非替代。
2. **为什么说 function calling 是私有协议？** 要点：格式由各模型厂定义且互不兼容，换模型需重写工具层。
3. **MCP 与 A2A 的本质区别？** 要点：MCP 面向工具/数据（无自主目标），A2A 面向 Agent 间任务级协作。
4. **OpenAPI 差在哪？** 要点：只描述接口不解决鉴权/传输/审批/变更通知等 Agent 化需求。
5. **CTRM 什么时候该包 MCP Server？** 要点：工具要被多个 AI 客户端复用、口径需统一、需要集中审计时。
6. **已有大量 REST 接口的企业怎么低成本接入 MCP？** 要点：网关/转换层把 OpenAPI 包装成 MCP Server。
7. **"Agent 同时用 MCP 和 A2A"合理吗？** 要点：合理——MCP 接工具，A2A 与其他 Agent 协作，各管一段。

下一章：`08-自测篇-题库与面试题.md`——合卷检验。
