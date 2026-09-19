# 05 - 实战篇：用好推理 API（全代码）

> 【本节问题】① 三家 SDK 的最小调用怎么写？② 流式输出怎么消费？③ 参数怎么按任务类型配？④ 本地部署（Ollama/vLLM）什么场景值得？⑤ 调用失败的完整降级链路？

![API时序](../diagrams/002-06-API时序与成本结构.svg)

---

## 1. 三家最小调用（2026-09 模型名）

### OpenAI（GPT-5.6 系，Responses API）

```python
from openai import OpenAI
client = OpenAI()  # OPENAI_API_KEY

resp = client.responses.create(
    model="gpt-5.6-terra",                 # Sol=旗舰 / Terra=主力 / Luna=便宜量足
    input=[
        {"role": "user", "content": "用一句话解释 KV cache 为什么能加速推理"},
    ],
    reasoning={"effort": "low"},           # 简单任务调低思考深度，省钱省时
    text={"verbosity": "low"},             # 控制回答长度
)
print(resp.output_text)
```

### Anthropic（Claude）

```python
import anthropic
client = anthropic.Anthropic()

resp = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,                        # 输出上限，必填
    system="你是 CTRM 系统的技术助手。回答简体中文。",   # 独立参数，不要放进 messages
    messages=[
        {"role": "user", "content": "点价和升贴水是什么关系？"},
    ],
    # 注意：4.6+ 不要传 temperature/top_p（非默认值 400）
    # 注意：不要再往 messages 末尾塞 assistant 预填消息（prefill 已废弃）
)
print(resp.content[0].text)
```

### DeepSeek（OpenAI 兼容格式，国产默认选项）

```python
from openai import OpenAI
client = OpenAI(api_key="sk-…", base_url="https://api.deepseek.com")

resp = client.chat.completions.create(
    model="deepseek-v4-flash",             # Flash=通用快 / Pro=重推理（旧别名 deepseek-chat/reasoner 已于 2026-07-24 退役）
    messages=[
        {"role": "system", "content": "你是贸易单证助手。"},
        {"role": "user", "content": "把这段中文品名标准化：'电解铜 500吨'"},
    ],
)
print(resp.choices[0].message.content)
```

## 2. 流式输出（长回答的体验救星）

```python
# Anthropic 流式示例（SSE）
with client.messages.stream(
    model="claude-sonnet-5", max_tokens=1024,
    system="…", messages=[{"role": "user", "content": "写一份点价流程说明"}],
) as stream:
    for text in stream.text_stream:        # 每个 token/片段实时到达
        print(text, end="", flush=True)
```

- 原理呼应 03 篇：生成就是逐 token 的，流式只是把每个 token **边生成边推给你**（SSE）
- 指标：**TTFT（首字延迟）** 主要受 prefill（prompt 长度）影响；整体时间 ≈ TTFT + 输出 token 数 / 吞吐
- Web 应用（你的 Vue 前端）用 `fetch` + `ReadableStream` 消费 SSE 即可

## 3. 参数配置速查（按任务类型）

| 任务 | 模型档位 | 温度/思考 | 关键参数 |
|---|---|---|---|
| 分类/抽取/结构化 | Luna / Flash / Haiku 级 | temp 0 / effort low | response_format=JSON Schema |
| 日常写作/总结 | Terra / Sonnet / Flash | temp 0.7 或默认 | verbosity 按需 |
| 复杂推理/审查 | Sol / Pro / Opus 级 | effort high（默认） | 控制思考预算上限 |
| Agent 主控 | Sonnet/Terra 级 | effort medium | 并行工具调用开启 |
| 海量批处理 | 任意 | — | **batch 端口（全场半价）** |

> 原则（呼应 001 篇）：**能用参数解决的别写进提示词；提示词里只放业务语义。**

## 4. 结构化输出（跨厂商通用模式）

```python
from openai import OpenAI
client = OpenAI()

resp = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[{"role": "user", "content": "从邮件抽取点价要素：<mail>…</mail>"}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "pricing_request",
            "schema": {
                "type": "object",
                "properties": {
                    "items": {"type": "array", "items": {"$ref": "#/$defs/item"}},
                },
                "$defs": {
                    "item": {
                        "type": "object",
                        "properties": {
                            "commodity": {"type": ["string", "null"]},
                            "quantity":  {"type": ["number", "null"]},
                            "delivery_month": {"type": ["string", "null"]},
                        },
                        "required": ["commodity", "quantity", "delivery_month"],
                    }
                },
            },
        },
    },
)
```

- 约束解码：引擎层直接禁掉不合 schema 的 token → 结构正确率 ~100%（05 篇 001 专题修复循环的更强上位替代）
- Anthropic 用 structured outputs / `output_config.format`；不支持的模型退回"提示词要 JSON + 校验重试"

## 5. 本地部署：Ollama / vLLM（数据主权场景）

| 工具 | 定位 | 适用 |
|---|---|---|
| **Ollama** | 一键拉起，桌面级 | 开发体验、隐私草稿、demo。`ollama run qwen3.6:27b` |
| **vLLM** | 生产级推理服务（PagedAttention、 continuous batching） | 团队内网服务、高并发。吞吐比 naive 方案高一个量级 |

```bash
# Ollama：5 分钟上手（Qwen3.6-27B 单卡 24GB 可跑，中文场景首选本地模型）
ollama run qwen3.6:27b

# vLLM：生产部署
vllm serve Qwen/Qwen3.6-27B --max-model-len 32768 --gpu-memory-utilization 0.9
```

**什么时候值得自部署**（决策清单）：

- [ ] 数据不能出内网（合规/涉密） → 必须本地
- [ ] 调用量巨大且任务简单（分类/抽取） → 小模型本地，边际成本趋近电费
- [ ] 需要微调私有领域模型（蒸馏/LoRA） → 本地闭环
- [ ] 只是"不想付 API 费"但调用量小 → **别**，自部署的运维成本会教做人

## 6. 失败与降级链路（生产必写）

```text
调用失败 → 判断错误类型：
├─ 429 限流 → 指数退避重试（读 Retry-After 头）
├─ 5xx/超时 → 换同档位备选模型重试一次
├─ 上下文超限 → 触发历史裁剪/摘要压缩（008 专题）后重试
├─ 结构化输出校验失败 → 带错误信息重试（001 篇修复循环）
└─ 仍然失败 → 降级到规则兜底/排队人工，并打告警
```

配套：所有调用记录 `模型版本+提示词版本+token用量`（06 篇监控的地基）。

---

## 【本节自测】

1. 三家 SDK 的 system 写法差异？Anthropic 两个"不要传"的参数是什么、为什么？
2. 流式输出的原理（用 03 篇语言解释）？TTFT 由什么决定？
3. 写出五类任务的参数配置（不看表）。
4. 约束解码和"提示词要 JSON+重试"的强度差异？
5. Ollama 和 vLLM 的定位差别？自部署的四条判断清单？
6. 手写降级链路伪代码：429、超限、校验失败三条分支。
7. （动手）用 Ollama 跑通 qwen3.6:27b（或更小杯），对比同任务与 DeepSeek API 的质量/延迟。
