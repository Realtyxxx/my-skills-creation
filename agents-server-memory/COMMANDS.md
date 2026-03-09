# AGENTS.MEMORY 快速命令参考

## 🎯 手动触发命令

在 Claude Code 对话中直接输入以下命令：

### 📖 读取记忆
```
MEMORY.READ
```
或者说：
- "read memory"
- "show me the memory"
- "读取记忆"

### 🔍 搜索记忆
```
MEMORY.SEARCH nginx ssl
```
或者说：
- "search memory for nginx"
- "搜索记忆中的 nginx"
- "find nginx in memory"

### 📊 查看状态
```
MEMORY.STATUS
```
或者说：
- "check memory status"
- "查看记忆状态"
- "show memory info"

### 💾 保存记忆
```
MEMORY.SAVE
```
或者说：
- "save this to memory"
- "remember this"
- "保存到记忆"
- "记住这个"

### 🏷️ 标签管理
```
MEMORY.TAG list
```
或者说：
- "show memory tags"
- "list all tags"
- "显示所有标签"

```
MEMORY.TAG show #deployment
```
或者说：
- "show entries with #deployment tag"
- "显示带有 #deployment 标签的记忆"

## 📝 使用示例

### 示例 1: 查看当前项目记忆
```
你: MEMORY.STATUS
AI: 执行状态检查，显示当前项目的记忆概况
```

### 示例 2: 搜索过往解决方案
```
你: MEMORY.SEARCH "nginx ssl error"
AI: 搜索所有包含这些关键词的记忆条目
```

### 示例 3: 保存当前会话
```
你: MEMORY.SAVE
AI: 分析当前会话，生成知识/trace候选，询问是否保存
```

### 示例 4: 读取项目知识
```
你: MEMORY.READ
AI: 读取并展示当前项目的知识库内容
```

## 🎨 命令变体

每个命令都支持多种说法，选择你喜欢的：

| 命令 | 英文说法 | 中文说法 |
|------|---------|---------|
| READ | "read memory", "show memory" | "读取记忆", "显示记忆" |
| SEARCH | "search memory for X" | "搜索记忆中的 X" |
| STATUS | "check memory status" | "查看记忆状态" |
| SAVE | "save to memory", "remember this" | "保存到记忆", "记住这个" |
| TAG | "show tags", "list tags" | "显示标签", "列出标签" |

## 💡 提示

1. **命令不区分大小写** - `MEMORY.READ` 和 `memory.read` 都可以
2. **支持自然语言** - 不需要精确匹配，说"查看记忆"也能触发
3. **可以组合使用** - 先 STATUS 查看状态，再 READ 读取内容
4. **搜索支持关键词** - `MEMORY.SEARCH nginx` 会搜索所有包含 nginx 的条目
5. **保存需要确认** - SAVE 命令会先展示候选内容，等你确认后才保存

## 🚀 快速开始

第一次使用？试试这个流程：

```
1. MEMORY.STATUS          # 查看当前状态
2. MEMORY.READ            # 读取现有记忆（如果有）
3. [做一些工作...]
4. MEMORY.SAVE            # 保存这次会话
5. MEMORY.TAG list        # 查看所有标签
```

## 📂 记忆存储位置

```
~/AGENTS.MEMORY/
  _global/              # 全局知识（跨项目）
  _home/                # Home 目录工作
  projects__myapp/      # 项目特定（自动识别）
```

## ⚙️ 高级用法

### 带选项的搜索
```
MEMORY.SEARCH nginx --type=knowledge
MEMORY.SEARCH error --scope=global
MEMORY.SEARCH "ssl" --since=2026-03-01
```

### 读取特定内容
```
MEMORY.READ trace        # 包含 trace
MEMORY.READ full         # 读取所有
MEMORY.READ --raw        # 原始格式
```

### 标签操作
```
MEMORY.TAG list                    # 列出所有标签
MEMORY.TAG show #deployment        # 显示特定标签的条目
MEMORY.TAG stats                   # 标签统计
```

---

**记住：直接在对话中输入这些命令，AI 会立即执行！**
