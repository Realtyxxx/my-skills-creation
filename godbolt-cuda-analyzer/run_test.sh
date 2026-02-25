#!/bin/bash
# -*- coding: utf-8 -*-
# 带编码保护的 Python 脚本运行器

# 设置 UTF-8 编码（使用系统可用的 locale）
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export PYTHONIOENCODING=utf-8

# 运行 Python 脚本
if [ $# -eq 0 ]; then
    echo "用法: $0 <python脚本.py> [参数...]"
    echo ""
    echo "示例:"
    echo "  $0 examples/test1_basic_ptx.py"
    echo "  $0 examples/quick_test.py"
    exit 1
fi

python3 "$@"
