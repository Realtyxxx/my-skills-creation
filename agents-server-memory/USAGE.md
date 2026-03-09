# AGENTS.MEMORY 使用指南

## 🎯 如何调用

### 方式 1: Skill 调用（类似 slash 命令）

```
/agents-memory status
/agents-memory read
/agents-memory search nginx
/agents-memory save
/agents-memory tag list
```

### 方式 2: 自然语言

```
MEMORY.STATUS
MEMORY.READ
MEMORY.SEARCH nginx
MEMORY.SAVE
```

---

## 📋 完整命令列表

### 📊 /agents-memory status
查看当前项目的记忆状态

**示例：**
```
/agents-memory status
```

**输出：**
- 当前项目 slug
- 全局知识行数
- 项目知识行数
- Trace 条目数
- 归档条目数
- 热门标签

---

### 📖 /agents-memory read
读取项目记忆

**语法：**
```
/agents-memory read              # 只读 knowledge
/agents-memory read trace        # 包含 trace
/agents-memory read full         # 读取所有
```

**示例：**
```
/agents-memory read
```

---

### 🔍 /agents-memory search
搜索记忆内容

**语法：**
```
/agents-memory search <keyword>
/agents-memory search <keyword> --type=knowledge
/agents-memory search <keyword> --scope=global
```

**示例：**
```
/agents-memory search nginx
/agents-memory search "ssl error" --type=knowledge
```

---

### 💾 /agents-memory save
保存当前会话到记忆

**语法：**
```
/agents-memory save
```

**流程：**
1. 分析当前会话
2. 生成知识/trace 候选
3. 建议标签和置信度
4. 询问用户确认
5. 保存到指定位置

---

### 🏷️ /agents-memory tag
标签管理

**语法：**
```
/agents-memory tag list              # 列出所有标签
/agents-memory tag show #deployment  # 显示特定标签
/agents-memory tag stats             # 标签统计
```

**示例：**
```
/agents-memory tag list
/agents-memory tag show #nginx
```

---

## 🚀 快速开始

### 第一次使用

```bash
# 1. 查看状态
/agents-memory status

# 2. 读取现有记忆（如果有）
/agents-memory read

# 3. 做一些工作...

# 4. 保存会话
/agents-memory save

# 5. 查看标签
/agents-memory tag list
```

### 日常使用

```bash
# 查找过往解决方案
/agents-memory search "nginx ssl"

# 查看特定标签的记忆
/agents-memory tag show #deployment

# 读取项目知识
/agents-memory read
```

---

## 💡 使用技巧

1. **定期保存** - 完成重要工作后使用 `/agents-memory save`
2. **善用搜索** - 遇到问题先搜索记忆：`/agents-memory search <关键词>`
3. **标签分类** - 保存时使用合适的标签，方便后续查找
4. **查看状态** - 定期运行 `/agents-memory status` 了解记忆库状态
5. **跨项目知识** - 通用知识保存到 global，项目特定保存到 project

---

## 📂 记忆存储位置

```
~/AGENTS.MEMORY/
  _global/              # 全局知识（跨项目）
    knowledge.md
    trace.md
  _home/                # Home 目录工作
    knowledge.md
    trace.md
  projects__myapp/      # 项目特定（自动识别）
    knowledge.md
    trace.md
    trace_archive.md
```

---

## 🎨 命令别名

每个命令都支持多种调用方式：

| Skill 调用 | 自然语言 | 中文 |
|-----------|---------|------|
| `/agents-memory status` | `MEMORY.STATUS` | "查看记忆状态" |
| `/agents-memory read` | `MEMORY.READ` | "读取记忆" |
| `/agents-memory search X` | `MEMORY.SEARCH X` | "搜索记忆中的 X" |
| `/agents-memory save` | `MEMORY.SAVE` | "保存到记忆" |
| `/agents-memory tag list` | `MEMORY.TAG list` | "显示所有标签" |

选择你喜欢的方式！

---

## ⚙️ 高级用法

### 搜索选项

```bash
# 只搜索 knowledge 文件
/agents-memory search nginx --type=knowledge

# 只搜索全局记忆
/agents-memory search error --scope=global

# 搜索特定项目
/agents-memory search bug --scope=projects__myapp

# 搜索指定日期之后的记忆
/agents-memory search deploy --since=2026-03-01
```

### 读取选项

```bash
# 包含 trace
/agents-memory read trace

# 读取所有内容
/agents-memory read full

# 原始格式（不总结）
/agents-memory read --raw
```

### 标签操作

```bash
# 列出所有标签及使用次数
/agents-memory tag list

# 显示特定标签的所有条目
/agents-memory tag show #deployment

# 查看标签统计和趋势
/agents-memory tag stats
```

---

## 📖 示例场景

### 场景 1: 解决 Nginx 问题

```bash
# 1. 搜索过往 nginx 相关记忆
/agents-memory search nginx

# 2. 查看 nginx 标签的所有条目
/agents-memory tag show #nginx

# 3. 解决问题后保存
/agents-memory save
# → 选择保存为 knowledge，添加 #nginx #ssl 标签
```

### 场景 2: 新项目开始

```bash
# 1. 查看当前状态
/agents-memory status

# 2. 读取全局知识（跨项目经验）
/agents-memory read

# 3. 工作一段时间后保存
/agents-memory save
```

### 场景 3: 定期维护

```bash
# 1. 查看记忆库状态
/agents-memory status

# 2. 查看所有标签
/agents-memory tag list

# 3. 搜索特定主题
/agents-memory search deployment
```

---

**现在就试试：输入 `/agents-memory status` 查看你的记忆状态！**
