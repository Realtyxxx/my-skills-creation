# AGENTS.MEMORY Skill for Claude Code

增强版的 AI Agent 持久化记忆系统，已成功安装到 Claude Code。

## 安装位置

```
~/.claude/skills/memory__agents-memory/
├── SKILL.md              # 主技能文档
└── instructions/         # 命令实现指南
    ├── read.md          # MEMORY.READ 实现
    ├── search.md        # MEMORY.SEARCH 实现
    ├── save.md          # MEMORY.SUMMARIZE_AND_ASK_SAVE 实现
    ├── status.md        # MEMORY.STATUS 实现
    └── tag.md           # MEMORY.TAG 实现
```

## 快速开始

### 1. 查看当前项目的记忆状态
```
MEMORY.STATUS
```

### 2. 读取项目知识库
```
MEMORY.READ              # 只读 knowledge
MEMORY.READ trace        # 包含 trace
MEMORY.READ full         # 读取所有
```

### 3. 搜索过往记忆
```
MEMORY.SEARCH "nginx ssl"
MEMORY.SEARCH #deployment --type=knowledge
MEMORY.SEARCH "error" --since=2026-03-01
```

### 4. 保存当前会话
```
MEMORY.SUMMARIZE_AND_ASK_SAVE
```

### 5. 浏览标签
```
MEMORY.TAG list
MEMORY.TAG show #deployment
MEMORY.TAG stats
```

## 核心特性

### ✅ 已实现的增强功能

1. **智能搜索系统** (MEMORY.SEARCH)
   - 关键词、正则、标签搜索
   - 按项目、类型、时间过滤
   - 相关性排序

2. **标签系统** (MEMORY.TAG)
   - #hashtag 格式
   - 自动索引
   - 统计和趋势分析

3. **改进的时间管理**
   - 0-14天：自动加载
   - 15-30天：关键词匹配加载
   - 31-90天：自动归档
   - >90天：建议移到 attic

4. **智能分片管理**
   - 自动跟随续接文件
   - 可合并去重 (MEMORY.CONSOLIDATE)
   - 自动备份

5. **增强的自动触发**
   - 项目范围匹配
   - 最近活动匹配
   - 语义匹配（标签）
   - 延续信号（"继续"、"之前"）

6. **统计和维护**
   - MEMORY.STATS：全局统计
   - MEMORY.CLEANUP：交互式清理
   - MEMORY.ARCHIVE：自动归档
   - MEMORY.GRAPH：关系可视化

7. **备份系统**
   - 每次写入自动备份
   - 保留最近10个版本
   - 支持回滚

8. **置信度分级保存**
   - HIGH/MEDIUM/LOW 三级
   - 自适应建议频率

## 记忆存储位置

```
~/AGENTS.MEMORY/
  _global/              # 全局知识
  _home/                # Home 目录工作
  projects__myapp/      # 项目特定（自动派生）
  attic/                # 冷归档
  .index/               # 索引文件
```

## 使用场景

### 场景 1: 开始新项目
```bash
# 系统会自动检测并加载已有的项目知识
# 如果是新项目，正常工作，结束时保存
MEMORY.SUMMARIZE_AND_ASK_SAVE
```

### 场景 2: 查找过往解决方案
```bash
MEMORY.SEARCH "nginx ssl error"
MEMORY.SEARCH #deployment --type=knowledge
```

### 场景 3: 维护记忆库
```bash
MEMORY.STATUS                    # 检查状态
MEMORY.CONSOLIDATE --dry-run     # 预览合并
MEMORY.ARCHIVE                   # 归档旧 trace
MEMORY.CLEANUP                   # 交互式清理
```

### 场景 4: 探索关系
```bash
MEMORY.GRAPH                     # 查看连接
MEMORY.TAG list                  # 浏览标签
MEMORY.STATS                     # 整体统计
```

## 命令参考

### 核心命令
- `MEMORY.READ [options]` - 读取记忆
- `MEMORY.SEARCH <keyword> [options]` - 搜索记忆
- `MEMORY.TAG <subcommand>` - 标签管理
- `MEMORY.SUMMARIZE_AND_ASK_SAVE` - 保存会话
- `MEMORY.STATUS` - 查看状态

### 维护命令
- `MEMORY.CONSOLIDATE` - 合并分片文件
- `MEMORY.ARCHIVE` - 归档旧 trace
- `MEMORY.STATS` - 全局统计
- `MEMORY.CLEANUP` - 交互式清理
- `MEMORY.GRAPH` - 关系可视化

## 最佳实践

1. **一致使用标签** - 让搜索更强大
2. **保存知识，不只是 trace** - 提取可复用模式
3. **定期归档** - 保持 trace.md 聚焦最近工作
4. **分片时合并** - 统一文件更易读
5. **交叉引用相关条目** - 构建知识图谱
6. **验证后再保存到 knowledge** - 只存确认的事实
7. **全局存储跨项目模式** - 共享学习成果
8. **定期查看 MEMORY.STATUS** - 保持卫生

## 与原版的区别

### 向后兼容
- 现有文件无需修改
- 标签是可选的（可逐步添加）
- 新命令是增量的（旧命令仍然工作）
- 自动触发逻辑增强但不破坏

### 新增功能
- 搜索命令（原版没有）
- 标签系统（原版没有）
- 改进的时间管理（14天 vs 7天）
- 自动归档（原版手动）
- 统计和可视化（原版没有）
- 备份系统（原版没有）
- 置信度分级（原版简单是/否）

## 技术细节

### Slug 派生规则
```bash
/home/user/projects/myapp → projects__myapp
/home/user/              → _home
```

### 文件大小限制
- 每个文件 < 200 行
- 超过时创建 knowledge_2.md
- 总计 > 500 行时建议合并

### Trace 保留策略
- 0-14天：trace.md（自动加载）
- 15-30天：trace.md（关键词匹配加载）
- 31-90天：trace_archive.md（可搜索）
- >90天：建议移到 attic

### 备份策略
- 每次写入前自动备份
- 格式：knowledge.md.2026-03-03T14-30-00.bak
- 保留最近 10 个备份
- 90 天后自动清理

## 故障排除

### 问题：搜索没有结果
```bash
# 检查是否有记忆
MEMORY.STATUS

# 尝试更广泛的关键词
MEMORY.SEARCH "error" --all

# 查看可用标签
MEMORY.TAG list
```

### 问题：文件太大
```bash
# 检查状态
MEMORY.STATUS

# 合并分片文件
MEMORY.CONSOLIDATE --dry-run
MEMORY.CONSOLIDATE

# 归档旧 trace
MEMORY.ARCHIVE
```

### 问题：找不到项目记忆
```bash
# 检查当前 slug
MEMORY.STATUS

# 列出所有项目
ls ~/AGENTS.MEMORY/

# 读取特定项目
MEMORY.READ projects__myapp
```

## 下一步

1. 运行 `MEMORY.STATUS` 查看当前状态
2. 如果有现有记忆，运行 `MEMORY.READ` 查看
3. 开始工作，结束时运行 `MEMORY.SUMMARIZE_AND_ASK_SAVE`
4. 使用 `MEMORY.SEARCH` 查找过往解决方案
5. 定期运行 `MEMORY.CLEANUP` 保持整洁

## 反馈和改进

这是增强版的 AGENTS.MEMORY skill，基于原版设计并添加了多项改进。如果有任何问题或建议，欢迎反馈！
