# ModelCompass：个人场景模型选择器

## 0. 文档状态

- 状态：设计方案 v2（方案已确认，待实现）
- 项目名：`ModelCompass`
- 建议仓库名：`modelcompass`
- Python 包名：`modelcompass`
- 目标形态：联网优先的本地 Web 工具；独立 GitHub 开源库；后续可作为 cc-switch 的外部集成工具
- 目标用户：同时使用多个模型、Provider、Agent 或 API 渠道，并希望按个人场景选择模型的用户
- 交接对象：新的 coding agent

## 1. 一句话定位

把公开模型评测、官方价格和规格信息，按用户定义的任务场景进行能力簇加权，计算场景任务成本，并允许用户自选 2-3 个维度生成 Pareto 前沿。第一版优先收录有公开测评数据的官方渠道模型；第三方渠道和可靠性暂不作为核心推荐维度。

核心原则：

> AA 等公共榜单用于发现候选；公开 benchmark 用于提供能力证据；用户场景权重决定最终排序；模型、版本、推理档位和渠道必须分开记录；模型版本和推理档位组成独立的 ModelVariant。

## 2. 为什么做

公共榜单通常回答“统一口径下哪个模型综合更强”，但个人实际选择还受到以下因素影响：

- 编程、科研、网页研究、中文知识库等任务的能力权重不同；
- 价格、延迟、上下文和工具能力不同；
- 同一模型在不同推理档位和 API 渠道上的表现不同；
- benchmark 之间存在重复计分、版本过期和厂商自报问题；
- cc-switch 中的模型名不一定等于上游真实模型身份。

本项目要解决的是“个人模型决策支持”，不是发布新的模型总榜。

## 3. 产品边界

### 3.1 MVP 必须做

1. 导入或联网读取结构化的公开评测数据，优先支持官方模型和官方渠道。
2. 支持 AA 快照、公开 Cost per Task、benchmark 分数、价格和模型元数据。
3. 按能力簇去重和归一化。
4. 支持用户定义多个场景及权重。
5. 计算场景质量分、场景任务成本和可解释推荐结果。
6. 允许用户从质量、场景任务成本、速度、首 token 延迟、上下文、能力簇分数中自选 2-3 个维度，动态绘制 Pareto 图。
7. 标注数据来源、更新时间、版本和置信度。
8. 提供 localhost Web UI，并支持 JSON、CSV 导出。
9. 对缺失数据、版本不匹配、过期数据和来源失败给出警告。

### 3.2 MVP 不做

- 不运行大规模 benchmark；
- 不承诺直接复现 AA 或厂商榜单；
- 不把所有模型接入 cc-switch 核心数据库；
- 不自动断言某个中转渠道背后的真实模型；
- 不把缺失分数静默补成 0 或平均值；
- 不把加权分数包装成客观真理；
- 不在第一版做账号登录、云端同步、在线社区榜单或复杂的渠道可靠性排名。

## 4. 推荐产品形态

第一版采用联网优先、本机 Web 服务架构：

```text
YAML/JSON 配置 + CSV/JSON 数据快照
              |
              v
       数据校验与标准化
              |
              v
       能力簇聚合与场景加权
              |
              v
   质量/成本/延迟/上下文计算
              |
              v
      Pareto 前沿识别与警告
              |
       +------+------+
       |             |
       v             v
    CLI 输出      localhost Web UI
```

推荐技术栈：

- Python 3.11+
- `pydantic`：数据模型和校验
- `pandas` 或标准库：数据处理
- `numpy`：数值计算
- `plotly`：交互式 Pareto 图
- `typer`：CLI
- `pytest`：测试
- `ruff`：格式和静态检查
- FastAPI + Jinja/HTMX：本机 Web 服务和页面交互

MVP 直接使用 Plotly 生成 2D/3D 交互图；数据模型和计算层不得与展示层耦合。

## 5. 核心数据对象

### 5.1 ModelIdentity

模型的规范身份，不能只用展示名称。

```yaml
canonical_id: openai/gpt-6.1-sol
provider_family: openai
model_name: gpt-6.1-sol
```

### 5.2 ModelVariant

模型版本和推理档位是第一版的独立评测对象；渠道信息只作为附加部署信息。

```yaml
variant_id: openai/gpt-6.1-sol@2026-10-01/reasoning-max
canonical_model_id: openai/gpt-6.1-sol
version: 2026-10-01
reasoning_mode: max
modality: text
context_window: 1000000
```

同一个模型的不同版本和推理档位应是不同 ModelVariant。

### 5.3 Deployment（可选附加对象）

Deployment 用于记录实际渠道，但不是第一版主推荐对象。

```yaml
deployment_id: ccs-myh/gpt-6.1-sol
model_variant_id: openai/gpt-6.1-sol@2026-10-01/reasoning-max
channel: cc-switch/myh
api_format: responses
availability: observed
```

官方 API、cc-switch 和其他 Provider 作为附加 Deployment 记录，不改变 ModelVariant 的公开能力评分。

### 5.4 BenchmarkObservation（挂载到模型版本）

```yaml
model_variant_id: openai/gpt-6.1-sol@2026-10-01/reasoning-max
benchmark_id: gpqa
ability_cluster: science_reasoning
score: 0.742
score_unit: accuracy
reported_at: 2026-10-10
source_url: https://example.org/result
source_type: third_party
reproducibility: medium
confidence: medium
notes: score is reported for a model family alias
```

### 5.5 PriceObservation

```yaml
model_variant_id: openai/gpt-6.1-sol@2026-10-01/reasoning-max
input_price_usd_per_million: 1.5
output_price_usd_per_million: 6.0
cached_input_price_usd_per_million: null
observed_at: 2026-10-18
source_url: https://example.org/pricing
confidence: high
```

### 5.6 CapabilityObservation

```yaml
model_variant_id: openai/gpt-6.1-sol@2026-10-01/reasoning-max
context_window: 1000000
tool_calling: true
web_search: unknown
mcp: unknown
vision: true
structured_output: true
source_url: https://example.org/docs
observed_at: 2026-10-18
```

### 5.7 PublicTaskCostObservation

第一版直接消费 Artificial Analysis 等公开来源的 Cost per Task，不在本地重新推导 token、调用次数或默认参数。

```yaml
model_variant_id: openai/gpt-6.1-sol@2026-10-01/reasoning-max
task_definition: aa_cost_per_task_v1
cost_usd: 0.08
observed_at: 2026-10-18
source_url: https://artificialanalysis.ai/
source_snapshot_id: aa-2026-10-18
```

### 5.8 ScenarioProfile

```yaml
id: coding
name: Codex 编程与仓库任务
weights:
  software_engineering: 0.30
  agent_tools: 0.20
  reasoning: 0.15
  long_context: 0.10
  instruction_following: 0.10
  general: 0.15
constraints:
  min_confidence: 0.55
  require_tool_calling: true
```

## 6. 能力簇设计

第一版固定以下能力簇，允许后续扩展：

- `general`：综合能力和通用偏好
- `reasoning`：通用复杂推理
- `mathematics`：数学推理
- `science_reasoning`：科学、物理、化学和知识推理
- `software_engineering`：仓库级编程和软件工程
- `code_generation`：代码生成与修复
- `agent_tools`：工具调用、终端、浏览器和 Agent 任务
- `long_context`：长上下文检索与文档理解
- `instruction_following`：格式和指令遵循
- `chinese`：中文理解和表达
- `multimodal`：图片、图表和文档视觉理解

benchmark 到能力簇必须通过显式映射表维护，禁止根据名称自动猜测后静默归类。

## 7. 公开数据源策略

### 7.1 第一版数据源

优先支持具有公开页面或公开 JSON/CSV 的来源：

- AA 或类似公共模型综合榜单快照；
- HELM 公共结果；
- OpenAI Evals 或公开 benchmark 结果；
- GPQA、MMLU-Pro、AIME/MATH、IFEval；
- SWE-bench、LiveCodeBench、Terminal-Bench；
- BrowseComp 或公开网页研究评测；
- C-Eval、CMMLU 等中文评测；
- 官方价格和上下文规格。

第一版可以先通过手工维护的 CSV/JSON 导入，不要为了“全自动”提前绑定不稳定网页结构。

### 7.2 SourceAdapter 接口

```python
class SourceAdapter(Protocol):
    source_id: str

    def fetch(self, *, as_of: date) -> RawSnapshot: ...
    def parse(self, snapshot: RawSnapshot) -> list[BenchmarkObservation]: ...
    def validate(self, records: list[BenchmarkObservation]) -> list[ValidationIssue]: ...
```

每个适配器必须保留：

- 原始来源 URL；
- 抓取时间；
- 原始快照或哈希；
- 解析版本；
- 失败原因；
- 是否为官方、第三方或用户手工录入。

### 7.3 数据失败规则

- 请求失败不能写成“没有数据”；
- 解析失败不能静默跳过；
- 数据过期要标记 `stale`；
- 页面结构变化要标记 `source_changed`；
- 同一模型多个版本无法匹配时，标记 `version_mismatch`；
- 评测未覆盖某模型时，保持缺失，不补 0。

## 8. 分数处理

### 8.1 归一化

所有分数进入内部的 \(0, 1\) 区间，但必须保留原始分数。

可选方法：

1. 百分比直接除以 100；
2. 在同一 benchmark 的候选模型集合内做 min-max；
3. 使用公开榜单的相对百分位；
4. 对有明确上下界的分数使用固定尺度。

默认优先使用“有明确语义的固定尺度”，其次才使用当前候选集合 min-max。不能让新增一个模型改变所有历史模型的绝对分数，除非用户明确选择相对排名模式。

### 8.2 能力簇聚合

同一能力簇内先聚合，再跨能力簇加权。第一版主评测对象是 ModelVariant，不是 deployment：

$$
B_{i,k} =
\frac{\sum_{j \in k} a_j r_{i,j} q_{i,j}}
{\sum_{j \in k} a_j r_{i,j}}
$$

其中：

- \(i\)：ModelVariant；
- \(k\)：能力簇；
- \(j\)：benchmark；
- \(a_j\)：benchmark 基础权重；
- \(r_{i,j}\)：版本、来源和覆盖置信度修正；
- \(q_{i,j}\)：归一化分数。

如果一个能力簇没有有效数据，输出缺失和置信度下降，不得自动补平均值。

### 8.3 场景质量

$$
Q_i^{(s)} = \sum_k w_k^{(s)} B_{i,k}
$$

有效权重只在有数据的能力簇上重新归一化，并同时输出：

- 原始覆盖率；
- 重归一化后的有效权重；
- 数据置信度；
- 缺失能力簇。

用户必须知道一个 0.82 分是“高覆盖高置信度”，还是“只覆盖两个 benchmark 后的重归一化结果”。

## 9. 置信度模型

置信度不是模型能力分数，不得混成同一个分数。单独计算：

$$
C_i^{(s)} =
C_{source} \times C_{freshness} \times C_{version} \times C_{coverage}
$$

建议初始等级：

- `high`：官方/公开方法、版本匹配、近期、第三方复核；
- `medium`：公开来源但版本或推理档位部分不明；
- `low`：厂商自报、模型别名不明、数据过期或覆盖不足。

界面同时展示 `quality` 与 `confidence`，不把低置信度高分排在高置信度结果之前而不提示。

## 10. 成本、延迟和可靠性

### 10.1 成本

第一版直接读取 Artificial Analysis 等公开来源的 Cost per Task 观测值，统一记为 `public_task_cost`。MVP 不要求用户填写输入 token、输出 token 或调用次数；该值是统一任务口径下的公开估计，不代表个人实际账单。

每条成本记录必须保存任务定义、成本单位、模型版本、推理档位、来源 URL、观测日期和来源快照版本。成本未知不补零，显示为数据不足。

### 10.2 延迟

优先使用公开报告或官方渠道统计；无数据时为 `unknown`，不补默认速度。

### 10.3 可靠性

可靠性暂不作为第一版核心推荐维度或 Pareto 轴。未来若加入独立的实测数据，再单独扩展可靠性数据结构。

### 10.4 官方模型优先

候选模型准入规则参考 Artificial Analysis：身份、版本和推理档位可确认；优先官方模型和官方渠道；有公开测评证据；有官方价格或明确标记价格未知。模型版本和推理档位视为独立模型版本。第三方 Provider 和 cc-switch 中转渠道可作为附加数据，但不进入默认主推荐。
## 11. Pareto 前沿

Pareto 图不固定维度。用户可以从可用指标中自选 2-3 个维度，每次修改轴后重新计算前沿。第一版可选：场景质量、公开 Cost per Task、输出速度、首 token 延迟、上下文窗口和能力簇分数。可靠性暂不作为核心维度。工具调用、视觉和结构化输出作为筛选条件，不作为连续轴。

模型 A 支配模型 B 的条件根据用户选择的轴动态生成。例如质量、成本、上下文三个轴为：

$$
Q_A \ge Q_B,\quad K_A \le K_B,\quad X_A \ge X_B
$$

并且至少一个不等式严格成立。未知值保留为未知，不补零、不视为最优；可以显示在“数据不足”层，但不能进入该轴的严格 Pareto 前沿。页面始终显示当前 Pareto 使用的维度和方向。

## 12. 默认个人场景

提供模板，不把模板写死成用户身份：

1. `coding`：Codex 编程与仓库任务
2. `research`：科研、数学和文献推理
3. `briefing`：每日简报、网页研究和自动化
4. `knowledge_base`：中文知识库和长文档
5. `quick_qa`：快速日常问答

用户可复制模板后修改权重。默认权重必须在配置文件中可见、可解释、可版本化。

## 13. 联网刷新与 Web UI

工具采用联网优先、快照可追溯的架构。启动时刷新数据，并按计划定时刷新；页面交互和 Pareto 计算实时完成，价格、规格和公开榜单由独立适配器更新。每次刷新保存来源、抓取时间、解析器版本、内容 hash 和状态。网络失败时继续使用最近一次成功快照，并标记 stale；解析失败标记 source_changed 或 parse_failed，不得静默清空已有数据。

推荐技术栈：Python、FastAPI、SQLite 或 DuckDB、Pydantic、NumPy/Pandas、Plotly。第一版使用本机 localhost Web 服务，建议 FastAPI + Jinja/HTMX + Plotly。Web UI 首屏包括场景选择、2-3 个 Pareto 轴选择、方向提示、官方模型筛选、Pareto 散点图、模型比较表和来源详情。

## 14. CLI 设计

```text
modelcompass init
modelcompass source list
modelcompass source update
modelcompass data validate
modelcompass scenario list
modelcompass scenario validate --file profile.yaml
modelcompass score --profile profile.yaml --as-of 2026-10-18
modelcompass pareto --profile profile.yaml --scenario coding
modelcompass report --profile profile.yaml --format web
modelcompass export --format json
```

本机服务命令：

```text
modelcompass serve --host 127.0.0.1 --port 8000
```

输出中必须包含数据快照日期和来源清单。

## 15. Web 面板

第一版页面包括：

- 当前 profile 和计算时间；
- 场景切换；
- Pareto 散点图；
- 点选模型后的来源和证据详情；
- 质量、成本、延迟、上下文和覆盖率表格；
- 数据覆盖率和置信度；
- 缺失/过期/版本不匹配警告；
- 推荐模型、低成本模型、备用模型；
- 导出 JSON/CSV；
- “这是公开先验，不是个人实测”的明确说明。

## 16. 仓库目录建议

```text
modelcompass/
├─ pyproject.toml
├─ README.md
├─ LICENSE
├─ CONTRIBUTING.md
├─ SECURITY.md
├─ docs/
│  ├─ design.md
│  ├─ data-contract.md
│  ├─ scoring.md
│  ├─ source-policy.md
│  └─ cc-switch-integration.md
├─ src/modelcompass/
│  ├─ cli.py
│  ├─ config.py
│  ├─ schemas.py
│  ├─ normalize.py
│  ├─ clusters.py
│  ├─ scoring.py
│  ├─ confidence.py
│  ├─ pareto.py
│  ├─ report.py
│  ├─ sources/
│  │  ├─ base.py
│  │  ├─ aa_snapshot.py
│  │  ├─ benchmark_csv.py
│  │  ├─ pricing.py
│  │  └─ official_specs.py
│  └─ integrations/
│     └─ cc_switch.py
├─ data/
│  ├─ schemas/
│  ├─ snapshots/
│  ├─ mappings/
│  └─ profiles/
├─ templates/
│  └─ report.html
├─ tests/
│  ├─ test_schema_validation.py
│  ├─ test_normalization.py
│  ├─ test_cluster_aggregation.py
│  ├─ test_missing_data.py
│  ├─ test_confidence.py
│  └─ test_pareto.py
└─ scripts/
   └─ validate_data.py
```

## 17. 数据许可和伦理边界

必须在 README 和每个数据源适配器中说明：

- 数据来源和许可；
- 是否允许再分发；
- 是否只是链接和摘要；
- 抓取频率和缓存策略；
- 不绕过登录、验证码、robots 或访问控制；
- 不把厂商宣传当作独立验证；
- 不把模型推荐写成绝对结论。

对于不能再分发的榜单，仓库只保留：

- source URL；
- 抓取时间；
- 解析器版本；
- 用户本地快照格式；
- 必要的摘要统计。

## 18. cc-switch 集成策略

### 第一阶段：不改 cc-switch

外部工具读取用户导出的模型/Provider JSON，或用户手动导入 cc-switch 模型目录。

### 第二阶段：轻量集成

向 cc-switch 提交小 PR，目标只包括：

- 导出当前模型和 Provider 信息的标准 JSON；
- 增加“打开 ModelCompass”入口；
- 显示当前模型在 ModelCompass 中的链接；
- 不把 benchmark 数据和权重算法放进 cc-switch 核心。

### 第三阶段：可选插件

如果 cc-switch 插件机制成熟，再做 `modelcompass-advisor` 插件。插件只调用本地 ModelCompass 服务或读取静态 JSON。

不要第一版直接修改 cc-switch 的核心模型数据库、Provider schema 或切换路径。

## 19. 里程碑

### M0：评分协议和样例数据

- 确定项目名和许可证；
- 写 JSON Schema/Pydantic schema；
- 写 5 个场景模板；
- 放入 3-5 个模型的人工构造样例；
- 跑通场景质量、公开 Cost per Task 和用户自选 2D/3D Pareto。

验收：本机 Web 服务可以展示有来源字段的模型比较和 Pareto 图。

### M1：联网 Web MVP

- AA snapshot 导入；
- benchmark CSV/JSON 导入；
- 8-10 个能力簇；
- 缺失数据和置信度；
- Web UI、JSON/CSV 输出；
- pytest 和 CLI 文档。

验收：新增模型或 benchmark 不会静默破坏已有数据；所有分数可追溯到来源。

### M2：启动与定时刷新

- SourceAdapter；
- 官方价格和规格；
- 数据快照和 hash；
- 失败卡和 stale 标记；
- 支持启动刷新和定时刷新；`stale`、`source_changed`、`parse_failed` 等状态可见；新数据校验通过后再替换主快照。

### M3：可选 cc-switch 集成

- 读取/导入 cc-switch Provider 作为附加 Deployment；
- 规范化别名；
- 显示模型+渠道组合；
- 输出一份小而独立的集成说明或 PR。

## 20. 开发纪律

- 先写数据契约，再写爬虫和图表；
- 先支持人工快照，再自动抓取；
- 每个外部来源必须可单独禁用；
- 网络失败不应清空或阻塞最近一次成功快照的 Web 报告；
- 不在展示层偷偷修改分数；
- 任何重归一化都要显示有效覆盖率；
- 任何推荐都要能回溯到 benchmark、权重和来源；
- 评测对象优先是有公开证据的模型版本和推理档位；
- 不把渠道可用性误称为模型能力；
- 不把单次厂商结果当成确定性事实。

## 21. 给实现 Agent 的直接任务说明

请在一个新的 GitHub 仓库 `modelcompass` 中实现本设计的 M0/M1，不要先做 cc-switch PR。

实现顺序：

1. 创建 Python 项目、README 和 localhost 服务入口；
2. 定义模型版本、推理档位、benchmark、price、capability、scenario、公开 Cost per Task、source snapshot 数据结构；
3. 创建样例数据和 5 个个人场景模板；
4. 实现数据校验、固定尺度归一化、能力簇聚合、覆盖率和置信度；
5. 实现场景质量和公开 Cost per Task 导入；
6. 实现用户自选 2D/3D Pareto 支配判断；
7. 实现 `serve`、`score`、`pareto`、`data validate` 和来源刷新命令；
8. 实现启动刷新、定时刷新和 localhost Web UI；
9. 编写针对缺失数据、重复 benchmark、未知成本/延迟、版本不匹配和 Pareto 支配关系的测试；
10. 最后再评估公开数据适配器和 cc-switch 集成。

禁止事项：

- 不把所有公开分数直接平均；
- 不把缺失值补成 0；
- 不把模型版本、推理档位和渠道混成一个对象；
- 不在没有来源和日期时接受 benchmark 或 Cost per Task 数据；
- 不在第一阶段提交 cc-switch 大型改动；
- 不把推荐写成模型真实性或绝对优越性的证明；
- 第一版不加入用户实测数据。

第一阶段交付物：

- 可运行的 `modelcompass` 本机 Web 仓库；
- `README.md`；
- `docs/design.md`；
- 示例 profile；
- 示例数据快照；
- 可交互的 2D/3D Pareto Web 页面；
- 启动刷新和定时刷新；
- 测试通过记录；
- 后续公开数据适配器和 cc-switch 集成的 issue 列表。
