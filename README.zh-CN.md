# Godmode

[English](README.md) | [简体中文](README.zh-CN.md)

面向 AI 编程智能体的可组合工程工作流与专业能力集合。

Godmode 为编程智能体提供明确的工作流：在修改代码前完成设计、规划并执行多步骤任务、测试驱动开发、定位根因、独立评审、验证可观察行为、安全发布、响应生产事故，以及运用聚焦的工程专业能力。

本仓库采用标准 Agent Skills 目录结构：每项公开能力都位于包含 `SKILL.md` 的独立目录中，并提供简洁的路由元数据，以及按需加载的参考资料或确定性辅助工具。Godmode 刻意不引入专有编排运行时。

## 安装

### 兼容 Agent Skills 的客户端

将公开技能目录复制到项目级 skills 目录：

```bash
mkdir -p .agents/skills
cp -R /absolute/path/to/godmode/skills/* .agents/skills/
```

支持 skills installer 的客户端可以直接安装本仓库。`examples/` 仅用于本地研究，已被 Git 忽略，运行时不需要它。

### Claude Code

```bash
claude --plugin-dir /absolute/path/to/godmode
claude plugin validate /absolute/path/to/godmode
```

轻量级 SessionStart hook 会注入共享操作规则；具体能力仍由客户端原生的 skill discovery 机制选择。

### Codex

仓库包含用于直接加载的 `.codex-plugin/plugin.json`，以及 `.agents/plugins/` 下的本地 marketplace 条目。Marketplace 只发布 `skills/`，因此 `examples/` 中被忽略的研究仓库不会进入安装包。请通过 Codex 插件浏览器或本地 marketplace 工作流安装，并确认预期技能已成功显示。

## 技能目录

### 核心工作流技能

| Skill | 使用场景 |
| --- | --- |
| `using-godmode` | 选择并组合目录中的技能 |
| `solution-design` | 需求模糊或影响重大的设计决策 |
| `implementation-planning` | 在多步骤实现前编写可执行的详细计划 |
| `plan-execution` | 按任务执行已有计划 |
| `test-driven-development` | 通过红—绿—重构完成行为变更和回归测试 |
| `root-cause-debugging` | 复现问题、定位根因并锁定回归 |
| `requesting-code-review` | 准备聚焦的独立代码评审材料 |
| `receiving-code-review` | 验证并处理评审发现 |
| `completion-verification` | 在宣称完成或发布前获取最新证据 |
| `dispatching-parallel-agents` | 将独立任务拆分给写入范围互不重叠的智能体 |
| `subagent-driven-development` | 针对计划任务执行实现者—评审者循环 |
| `using-git-worktrees` | 为并行或高风险工作提供安全隔离 |
| `branch-integration` | 完成最终差异、证据、集成和清理决策 |
| `writing-skills` | 创建并评估新的 Agent Skills |

### 工程能力

| Skill | 使用场景 |
| --- | --- |
| `frontend-design` | 新建或重构界面、设计系统、状态和响应式 UI |
| `ui-ux-review` | 审查现有 UI、视觉质量、无障碍和反模式 |
| `api-and-interface-design` | HTTP、RPC、CLI、Webhook 和事件契约 |
| `database-design` | Schema、索引、迁移、一致性、保留和恢复 |
| `security-and-hardening` | 威胁建模、滥用路径、隐私和防御控制 |
| `performance-optimization` | 基于测量优化延迟、内存、渲染、查询和 bundle |
| `test-strategy` | 基于风险的覆盖、环境、发布门禁和测试责任 |
| `browser-testing` | 真实浏览器流程、响应式行为、无障碍和视觉证据 |
| `documentation-and-adrs` | README、Runbook、设计文档和架构决策 |
| `observability-and-instrumentation` | 日志、指标、追踪、告警和诊断边界 |
| `codebase-orientation` | 入口、执行路径、所有权、约定、热点和未知项 |
| `technical-research` | 依据权威来源作出版本敏感的技术决策 |
| `safe-migrations` | 兼容的分阶段迁移、对账、回滚和清理 |
| `release-engineering` | CI 门禁、制品、金丝雀、晋级阈值和回滚 |
| `architecture-review` | 结构摩擦、模块所有权、耦合和可测试性 |
| `code-simplification` | 在保持行为不变的前提下降低复杂度 |
| `behavior-validation` | 根据可观察契约执行源码盲测的黑盒验证 |
| `agent-evaluation` | 为 prompt、工具、智能体和 skill 构建基线与候选评估 |
| `incident-response` | 生产事故中的控制、恢复、证据、沟通和复盘 |

这些名称刻意采用直白、面向任务的词汇。它们描述能力边界，不依赖其他仓库的公开命名或难懂的短别名。

## 常见组合

```text
新功能：
  solution-design → implementation-planning → plan-execution + test-driven-development
  → requesting-code-review → completion-verification

包含持久化的新 API：
  solution-design + api-and-interface-design + database-design
  → implementation-planning → TDD → security-and-hardening

高质量网页：
  solution-design + frontend-design → plan-execution + browser-testing
  → ui-ux-review → completion-verification

不稳定的浏览器回归：
  root-cause-debugging + browser-testing
  → test-driven-development → completion-verification

陌生的跨模块变更：
  codebase-orientation → solution-design + technical-research
  → implementation-planning → plan-execution

有状态的生产迁移：
  safe-migrations + test-strategy + observability-and-instrumentation
  → release-engineering → behavior-validation

正在影响生产环境的事故：
  incident-response → root-cause-debugging
  → test-driven-development → completion-verification
```

原生客户端 discovery 根据描述决定激活哪些技能。只有当任务确实跨越多个能力边界时才应组合多个技能；目录不会预加载所有参考文件。

## 设计原则

- 智能体的声明不等于证据。
- 直白的职责名称优于短别名和借用词汇。
- 当工作流状态具有不同的激活和交接规则时，应将其拆分。
- 保持 `SKILL.md` 简洁，按需渐进加载深入规则。
- 对重复且容易出错的工作使用确定性辅助工具。
- 审查实际渲染后的 UI，而不只是源码。
- 将日志、外部文本、生成内容和工具响应视为不可信数据。
- 未经实际验证，不宣称兼容某个客户端。

## 开发

```bash
npm run check
python3 skills/frontend-design/scripts/design_system.py \
  --product "analytics dashboard" --tone technical --stack react
python3 skills/frontend-design/scripts/extract_design_system.py ./path/to/ui
python3 skills/ui-ux-review/scripts/audit_ui.py ./path/to/ui
python3 scripts/behavior_eval.py validate evals/behavior/core-workflows.json
```

仓库门禁会验证 frontmatter、本地链接、正文长度、manifest 结构、33 份路由评估、behavior-eval case schema 和辅助工具测试。作者与贡献说明请参阅 [`CONTRIBUTING.md`](CONTRIBUTING.md)、[`docs/catalog.md`](docs/catalog.md) 和 [`docs/research.md`](docs/research.md)。支持、安全和发布说明请参阅 [`SUPPORT.md`](SUPPORT.md)、[`SECURITY.md`](SECURITY.md) 和 [`CHANGELOG.md`](CHANGELOG.md)。客户端验证证据及其限制记录在 [`docs/compatibility.md`](docs/compatibility.md) 中。

维护者专用的交接、来源记录、生命周期、behavior eval、激活和发布流程位于 [`docs/maintainer-workflows.md`](docs/maintainer-workflows.md)。这些流程不会作为公开 skill 发布，以避免产生路由冲突。

`package.json` 保持 `private: true`，防止意外发布到 npm。公开分发通过代码仓库、客户端 marketplace 和带校验和的 GitHub Release 归档完成。

## 状态

Godmode 目前是 pre-1.0 public preview。技能目录、确定性辅助工具、路由 fixtures 和 behavior-eval harness 已可使用，但针对不同客户端的激活效果和输出质量，仍需要在受支持的运行环境中记录 forward run。仓库门禁通过并不表示所有模型或客户端的行为完全一致。

## 许可证

MIT。`examples/` 下的仓库保留各自许可证，且不属于 Godmode 分发包。
