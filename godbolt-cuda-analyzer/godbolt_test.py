# -*- coding: utf-8 -*-
import re
import requests
import json

# SASS 模式使用的默认 cuclang 编译器（Clang 20.1.0 + CUDA 12.9.1, sm_90）
DEFAULT_SASS_COMPILER = "cuclang2010-1291"


def _convert_flags_for_cuclang(flags: str) -> str:
    """将 nvcc 风格的 flags 转换为 cuclang (Clang CUDA) 风格。"""
    result = flags
    # -arch=sm_XX → --cuda-gpu-arch=sm_XX
    result = re.sub(r'-arch=(\S+)', r'--cuda-gpu-arch=\1', result)
    # 去掉 --ptx（cuclang SASS 模式不需要）
    result = re.sub(r'--ptx\b', '', result)
    # 去掉 --cubin
    result = re.sub(r'--cubin\b', '', result)
    return result.strip()


def compile_and_analyze_asm(
    source_code: str,
    language: str = "cuda",
    compiler_id: str = "nvcc120",
    flags: str = "-O3 -arch=sm_90 --ptx",
    output_mode: str = "ptx",
) -> dict:
    """
    将代码发送给 Godbolt Compiler Explorer 并获取汇编代码。

    Args:
        source_code: CUDA 源代码
        language: 语言，默认 "cuda"
        compiler_id: 编译器 ID，PTX 模式默认 "nvcc120"，SASS 模式自动切换为 cuclang
        flags: 编译器参数，默认 "-O3 -arch=sm_90 --ptx"
        output_mode: "ptx" 返回 PTX 虚拟汇编，"sass" 返回真实 GPU 机器码（SASS）

    Returns:
        dict with keys: success, asm, stderr, raw_code, mode, compiler_used
    """
    mode = output_mode.lower()
    if mode not in ("ptx", "sass"):
        return {
            "success": False, "asm": "", "mode": mode,
            "stderr": f"不支持的 output_mode: {output_mode}，请使用 'ptx' 或 'sass'",
            "raw_code": -1, "compiler_used": "",
        }

    # SASS 模式：自动切换编译器和 flags
    if mode == "sass":
        actual_compiler = DEFAULT_SASS_COMPILER
        actual_flags = _convert_flags_for_cuclang(flags)
        binary_filter = True
    else:
        actual_compiler = compiler_id
        actual_flags = flags
        binary_filter = False

    url = f"https://godbolt.org/api/compiler/{actual_compiler}/compile"

    payload = {
        "source": source_code,
        "lang": language,
        "options": {
            "userArguments": actual_flags,
            "filters": {
                "binary": binary_filter,
                "labels": True,
                "directives": True,
                "commentOnly": True,
                "libraryCode": True,
                "intel": True,
                "demangle": True,
            },
        },
        "allowStoreCodeDebug": False,
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        try:
            result_data = response.json()
        except (json.JSONDecodeError, ValueError) as e:
            return {
                "success": False, "asm": "", "mode": mode,
                "stderr": f"API 返回非 JSON 内容 (可能被限流): {str(e)}",
                "raw_code": -1, "compiler_used": actual_compiler,
            }

        asm_lines = [line_obj.get("text", "") for line_obj in result_data.get("asm", [])]
        compiled_asm = "\n".join(asm_lines)

        stderr_lines = [err.get("text", "") for err in result_data.get("stderr", [])]
        stderr_output = "\n".join(stderr_lines)

        return {
            "success": result_data.get("code", 0) == 0,
            "asm": compiled_asm,
            "stderr": stderr_output,
            "raw_code": result_data.get("code"),
            "mode": mode,
            "compiler_used": actual_compiler,
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False, "asm": "", "mode": mode,
            "stderr": f"API 请求失败: {str(e)}",
            "raw_code": -1, "compiler_used": actual_compiler,
        }
