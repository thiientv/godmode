<div align="center">

# Godmode

**面向 AI 编程智能体的工程工作流与专业能力。**

Godmode 帮助编程智能体从“**会写代码**”走向“**会做工程**”：在实现前明确设计，在变更后验证行为，并通过测试、评审和新鲜证据支撑完成声明。

[![Validate](https://github.com/thiientv/godmode/actions/workflows/validate.yml/badge.svg)](https://github.com/thiientv/godmode/actions/workflows/validate.yml)
[![Release](https://img.shields.io/github/v/release/thiientv/godmode)](https://github.com/thiientv/godmode/releases/latest)
[![License](https://img.shields.io/github/license/thiientv/godmode)](LICENSE)

[English](README.md) · [简体中文](README.zh-CN.md)

</div>

> **状态：** Pre-1.0 public preview。技能目录与验证工具已经可以使用；同时，我们仍在持续记录不同客户端环境中的兼容性与输出质量。

## 为什么是 Godmode？

AI 编程智能体越来越擅长生成代码，但更难的问题是让它们表现得像一名有纪律的工程师：

- 修改前先理解现有代码库
- 对重要变更先做设计，再开始实现
- 为任务选择合适的领域能力
- 验证真实行为，而不是默认“应该没问题”
- 对关键变更执行独立评审
- 用新鲜证据支撑完成或发布声明
- 保存可恢复的执行状态，避免中断后只能依赖对话记忆

Godmode 将这些行为封装为**可组合的 Agent Skills**，而不是一个巨型系统 Prompt，也不是一个专有编排运行时。

## 工作方式

```text
                         用户任务
                            │
                            ▼
                    ┌───────────────┐
                    │    Godmode    │
                    │   Skill 目录  │
                    └───────┬───────┘
                            │
                  发现 + 组合所需能力
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
  solution-design    API / database       security / UI
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
                 implementation-planning
                            │
                            ▼
                    测试 + 独立评审
                            │
                            ▼
                    新鲜验证证据
                            │
                            ▼
                       可验证结果
```

上图只是示意，并不是强制流水线。小任务可能只需要一个 skill；高风险或影响较大的工作可以组合多个能力。

## 你得到什么

### 可组合的 Skills

每项能力都有清晰的责任边界，并遵循 [Agent Skills](https://agentskills.io/) 目录结构。Skill 可以包含精炼流程、渐进式参考资料，以及在自动化确实能提高可靠性时使用的确定性辅助工具。

### 工程工作流

覆盖代码库认知、方案设计、实现规划、执行、调试、测试、代码评审、完成验证、并行工作和发布集成等核心工程环节。

### 领域专业能力

覆盖前端、API、数据库、安全、性能、可观测性、迁移、浏览器测试、文档和事故响应等常见工程领域。

### 确定性验证

仓库提供 validator、routing fixture、behavior evaluation、证据跟踪、生命周期检查和 repository quality gate，让技能目录本身也可以被持续验证，而不仅仅依赖自然语言描述。

## 安装

Godmode 以可移植 skills 仓库的形式分发，不需要专有运行时。

### Agent Skills-compatible 客户端

将公开技能复制到项目级 skills 目录：

```bash
mkdir -p .agents/skills
cp -R /absolute/path/to/godmode/skills/* .agents/skills/
```

### Claude Code

```bash
claude --plugin-dir /absolute/path/to/godmode
claude plugin validate /absolute/path/to/godmode
```

### Codex

仓库包含 `.codex-plugin/plugin.json` 和 `.agents/plugins/` 下的本地 marketplace 条目。请通过 Codex 插件工作流安装，并确认预期 skills 已可用。

> **兼容性说明：** 客户端支持情况基于实际记录的运行证据，而不是默认推断。详见 [`docs/compatibility.md`](docs/compatibility.md)。

## 示例

例如需求：

```text
为 API 增加身份验证，并使其达到生产可用标准。
```

可以拆分成以下工程职责：

```text
codebase-orientation
        ↓
solution-design
        ↓
api-and-interface-design + security-and-hardening
        ↓
implementation-planning
        ↓
test-driven-development
        ↓
requesting-code-review / receiving-code-review
        ↓
completion-verification
```

实际组合取决于任务、代码库、风险和可获得的证据。

## Skill 目录

### 核心工作流

| Skill | 用途 |
| --- | --- |
| `using-godmode` | 发现并组合 Godmode 能力 |
| `codebase-orientation` | 理解入口、执行路径、约定和热点 |
| `solution-design` | 明确需求并设计重要变更 |
| `implementation-planning` | 产出可执行的实现计划 |
| `plan-execution` | 执行已有实现计划 |
| `test-driven-development` | 通过测试驱动行为变更 |
| `root-cause-debugging` | 复现问题、定位根因并锁定回归 |
| `requesting-code-review` | 准备聚焦的独立评审上下文 |
| `receiving-code-review` | 验证并处理评审发现 |
| `completion-verification` | 在完成声明前收集新鲜证据 |
| `dispatching-parallel-agents` | 安全拆分相互独立的工作 |
| `subagent-driven-development` | 围绕计划任务执行实现/评审循环 |
| `using-git-worktrees` | 隔离并行或高风险变更 |
| `branch-integration` | 验证、集成并清理已完成工作 |
| `writing-skills` | 创建并评估新的 Agent Skills |

### 工程能力

| Skill | 用途 |
| --- | --- |
| `frontend-design` | 构建界面、设计系统、状态和响应式 UI |
| `ui-ux-review` | 审查 UI 质量、无障碍和交互模式 |
| `api-and-interface-design` | 设计 HTTP、RPC、CLI、Webhook 和事件契约 |
| `database-design` | 设计 Schema、索引、一致性、保留和恢复策略 |
| `security-and-hardening` | 威胁建模、隐私、滥用路径和防御控制 |
| `performance-optimization` | 优化经过测量的延迟、内存、渲染、查询和 bundle |
| `test-strategy` | 定义基于风险的测试覆盖和发布门禁 |
| `browser-testing` | 验证真实浏览器行为和响应式流程 |
| `documentation-and-adrs` | 编写 README、Runbook、设计文档和架构决策 |
| `observability-and-instrumentation` | 设计日志、指标、追踪、告警和诊断边界 |
| `technical-research` | 基于权威来源进行版本敏感的技术决策 |
| `safe-migrations` | 设计兼容迁移、对账、回滚和清理流程 |
| `release-engineering` | 管理 CI 门禁、制品、发布晋级和回滚 |
| `architecture-review` | 审查耦合、所有权、可测试性和结构性问题 |
| `code-simplification` | 在保持行为不变的前提下降低复杂度 |
| `behavior-validation` | 通过源码盲测验证可观察行为契约 |
| `agent-evaluation` | 评估 prompt、工具、智能体和 skills |
| `incident-response` | 处理生产事故中的控制、恢复、证据和复盘 |

完整目录与路由模型见 [`docs/catalog.md`](docs/catalog.md)。

## 设计原则

1. **声明不是证据。** 完成需要验证。
2. **组合能力，而不是不断扩大一个巨型 Prompt。**
3. **保持责任边界清晰。** Skill 名称应直接描述职责。
4. **渐进式加载知识。** `SKILL.md` 保持聚焦，深层内容放入 references。
5. **对重复工作做确定性自动化。** 只有能降低错误和歧义时才引入 helper。
6. **把外部内容视为不可信输入。** 日志、生成输出、工具响应和仓库文本都可能包含误导性指令。
7. **优先使用已记录的兼容性证据。** 未实际验证前，不宣称支持某个客户端。

## 仓库结构

```text
.
├── skills/                 # 公开 Agent Skills
├── scripts/                # 确定性验证和仓库工具
├── tests/                  # 自动化测试
├── evals/                  # 行为与路由评估
├── benchmarks/             # 可移植 benchmark fixtures
├── docs/                   # 目录、兼容性、研究和维护文档
├── .agents/                # Agent / plugin 元数据
├── .codex-plugin/          # Codex 插件元数据
├── README.md
└── LICENSE
```

## 开发

克隆仓库并运行验证：

```bash
git clone https://github.com/thiientv/godmode.git
cd godmode

npm run check
npm run catalog:health
python3 scripts/repository_security.py
python3 scripts/compatibility.py check
python3 -m unittest discover -s tests -p 'test_*.py'
```

针对特定工具也可以直接运行：

```bash
python3 skills/frontend-design/scripts/design_system.py \
  --product "analytics dashboard" \
  --tone technical \
  --stack react

python3 skills/frontend-design/scripts/extract_design_system.py ./path/to/ui
python3 skills/ui-ux-review/scripts/audit_ui.py ./path/to/ui
```

仓库门禁会检查目录结构、frontmatter、本地链接、routing fixtures、behavior-eval schema、compatibility drift、workflow 安全、公开文件安全以及辅助工具测试。

## 文档

- [`docs/catalog.md`](docs/catalog.md) — Skill 目录结构与路由模型
- [`docs/compatibility.md`](docs/compatibility.md) — 客户端兼容性证据
- [`docs/research.md`](docs/research.md) — 研究与来源记录
- [`docs/maintainer-workflows.md`](docs/maintainer-workflows.md) — 维护者执行与发布流程
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — 贡献流程
- [`SECURITY.md`](SECURITY.md) — 安全政策
- [`SUPPORT.md`](SUPPORT.md) — 支持信息
- [`CHANGELOG.md`](CHANGELOG.md) — 版本变更记录

## 贡献

欢迎贡献。新增 skill 前，优先考虑是否应该扩展现有职责边界。新 skill 应保持简洁、可独立路由、可测试，并尽可能配套合适的 fixture 或验证。

请先阅读 [`CONTRIBUTING.md`](CONTRIBUTING.md) 和 [`docs/catalog.md`](docs/catalog.md)。

## 路线图

Godmode 正在逐步演进为面向 AI 编程智能体的、更广泛的证据驱动工程层。当前重点包括：

- 扩大客户端兼容性覆盖
- 强化行为与回归评估
- 丰富 skill 组合与依赖元数据
- 改进高价值工作流的确定性工具
- 提升发布和兼容性证据的清晰度

路线图以已验证的仓库行为为驱动，而不是对模型能力作未经验证的承诺。

## 许可证

Godmode 使用 [MIT License](LICENSE) 发布。

<div align="center">

**如果 Godmode 帮助你的智能体更好地完成工程工作，欢迎给项目点一个 Star。**

</div>
