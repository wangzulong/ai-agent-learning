# 05 - 实战篇：三家 SDK 全代码（点价工具集）

> 【本节问题】① OpenAI Responses API 的工具定义长什么样？② Anthropic 的 tool_use/tool_result block 怎么接线？③ Gemini 的 function calling 有什么不同？④ 同一个点价场景三家代码差在哪？⑤ Java 开发者从哪里切入？

![一次工具调用的完整旅程](../diagrams/004-02-一次工具调用的完整旅程.svg)

> 贯穿场景（回扣 01 篇）：agent 面对客户邮件，可调用 `query_inventory`（查库存）、`query_futures_price`（查期货价）、`submit_pricing_proposal`（建点价建议单·写·高危）。三家代码同构，只有"包装"不同（07 篇对比表）。

---

## 1. OpenAI（Responses API，2026-09 主推）

```python
from openai import OpenAI
import json
client = OpenAI()

TOOLS = [
  {"type": "function", "name": "query_inventory",
   "description": "按品种查询当前可用库存。返回 available_tons 与 warehouses。不要用它查期货价。",
   "parameters": {"type": "object", "properties": {
       "variety": {"type": "string", "enum": ["M", "RM", "Y"]}},
     "required": ["variety"]}},
  {"type": "function", "name": "submit_pricing_proposal",
   "description": "生成点价建议单并挂起待交易员确认。高危写操作。",
   "parameters": {"type": "object", "properties": {
       "variety": {"type": "string"}, "tons": {"type": "integer"},
       "basis": {"type": "number"}, "contract_month": {"type": "string"}},
     "required": ["variety", "tons", "contract_month"]}},
]

def run(mail: str):
    input_items = [{"role": "user",
                    "content": f"处理这封邮件：<mail>{mail}</mail>"}]
    while True:                                   # 工具循环（003 篇手写循环的 SDK 版）
        resp = client.responses.create(
            model="gpt-5",                        # 2026-09 主力
            instructions="你是点价要素处理助手。仅按工具结果作答，缺失填 null。",
            input=input_items, tools=TOOLS)
        calls = [i for i in resp.output if i.type == "function_call"]
        if not calls:
            return resp.output_text               # 没有工具调用 = 最终回答
        input_items += resp.output                # 模型输出（含 tool_calls）原样回填
        for c in calls:                           # 并行工具调用：逐个执行
            result = dispatch(c.name, json.loads(c.arguments))
            input_items.append({"type": "function_call_output",
                                "call_id": c.call_id,
                                "output": json.dumps(result, ensure_ascii=False)})
```

**要点**：Responses API 的工具定义是**扁平的**（`name/parameters` 直接放在顶层，不再嵌套 `"function": {}`）；`call_id` 是并行调用的配对键，丢了就接不上。

## 2. Anthropic（tool_use / tool_result block）

```python
import anthropic, json
client = anthropic.Anthropic()

TOOLS = [
  {"name": "query_inventory",
   "description": "按品种查询当前可用库存。不要用它查期货价。",
   "input_schema": {"type": "object", "properties": {
       "variety": {"type": "string", "enum": ["M", "RM", "Y"]}},
     "required": ["variety"]}},
]

def run(mail: str):
    messages = [{"role": "user",
                 "content": f"<contract>{mail}</contract>\n请处理点价申请。"}]
    while True:
        resp = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=2000,
            system="你是点价助手。仅输出 JSON，无闲话。",   # 独立 system 参数（001 篇）
            tools=TOOLS, messages=messages)
        tool_uses = [b for b in resp.content if b.type == "tool_use"]
        if not tool_uses:
            return resp.content                      # text block = 最终回答
        results = []
        for b in tool_uses:
            result = dispatch(b.name, b.input)
            results.append({"type": "tool_result", "tool_use_id": b.id,
                            "content": json.dumps(result, ensure_ascii=False)})
        messages.append({"role": "assistant", "content": resp.content})
        messages.append({"role": "user",   "content": results})  # tool_result 放 user 轮
```

**要点**：`tools` 用 `input_schema`（不是 `parameters`）；`stop_reason == "tool_use"` 也可以做终止判断；**tool_result 必须装在紧跟的 user 消息里**——这是三家差异最大的一处。

## 3. Gemini（functionDeclarations）

```python
from google import genai
from google.genai import types
client = genai.Client()

TOOLS = types.Tool(function_declarations=[{
    "name": "query_inventory",
    "description": "按品种查询当前可用库存。",
    "parameters": {"type": "object", "properties": {
        "variety": {"type": "string", "enum": ["M", "RM", "Y"]}},
      "required": ["variety"]}},
])

def run(mail: str):
    cfg = types.GenerateContentConfig(
        system_instruction="你是点价助手。",
        tools=[TOOLS], temperature=0)
    chat = client.chats.create(model="gemini-3.1-pro", config=cfg)
    resp = chat.send_message(f"<mail>{mail}</mail>")
    while fn := resp.function_calls:                 # 有调用就执行回填
        parts = []
        for c in fn:
            result = dispatch(c.name, dict(c.args))
            parts.append(types.Part.from_function_response(
                name=c.name, response={"result": result}))
        resp = chat.send_message(parts)              # 同会话直接回填
    return resp.text
```

**要点**：Gemini 的 `function_declarations` 里 `parameters` 的 `type` 用**大写字符串或内置枚举**；官方明确要求 **query last**（问题放最后，001/07 篇提过）；`chats` 会话对象自动维护历史，回填走 `Part.from_function_response`。

## 4. 三家同构对照（一眼看穿包装差异）

| 环节 | OpenAI | Anthropic | Gemini |
|---|---|---|---|
| 工具定义键 | `parameters`（扁平） | `input_schema` | `function_declarations` |
| 模型的调用意图 | `function_call` item | `tool_use` block | `functionCall` part |
| 结果回填 | `function_call_output` + `call_id` | `tool_result`（user 轮） | `from_function_response` |
| 强制调用 | `tool_choice` | `tool_choice` | `tool_config` |

## 5. Java 开发者切入路径

- **Spring AI 1.x**：`@Tool` 注解直接把 Spring Bean 方法变成工具，ChatClient 自动接线——CTRM 里现有的 `InventoryService.query()` 加个注解就是工具（09 篇详表）
- **LangChain4j 1.x**：`@Tool` 同款思路，社区活跃，MCP 原生支持（006 篇联动）
- 心智转换只有一条：**Java 里写"函数"，框架负责"把函数变成模型看得懂的 schema + 接线循环"**——这正是 03 篇那张旅程图里"客户端执行"环节的工程化。

---

## 【本节自测】

1. Responses API 与 Chat Completions 的工具定义差别？（要点：扁平 name/parameters 顶层 vs 嵌套 "function":{}；新代码用 Responses）
2. Anthropic 的 tool_result 为什么要放 user 轮？（要点：协议约定，模型在下一轮 assistant 生成前需要 user 角色承载工具结果；三家最大差异点）
3. `call_id` / `tool_use_id` 丢了会发生什么？（要点：结果与调用配不上对，并行调用场景必炸；回填前务必逐个配对）
4. 三家"强制工具调用"的参数名分别是什么？（要点：tool_choice / tool_choice / tool_config）
5. Java 团队最小成本接入路径？（要点：Spring AI/LangChain4j 的 @Tool 注解包住现有 Service 方法；框架代管 schema 与循环）
