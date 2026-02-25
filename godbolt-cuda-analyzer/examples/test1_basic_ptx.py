#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 1：基础工具调用与连通性验证 - PTX 版本"""

from godbolt_test import compile_and_analyze_asm

# 测试用的简单 CUDA 核函数 (向量加法)
cuda_source = """
extern "C" __global__ void vectorAdd(const float *A, const float *B, float *C, int numElements) {
    int i = blockDim.x * blockIdx.x + threadIdx.x;
    if (i < numElements) {
        C[i] = A[i] + B[i];
    }
}
"""

print("=" * 80)
print("测试 1：基础工具调用与连通性验证 (PTX)")
print("=" * 80)

# 调用工具测试 - 使用 --ptx 生成 PTX 而不是 SASS
result = compile_and_analyze_asm(
    source_code=cuda_source,
    language="cuda",
    compiler_id="nvcc120",
    flags="-O3 -arch=sm_90 --ptx"
)

print(f"\n编译状态: {'✓ 成功' if result['success'] else '✗ 失败'}")
print(f"返回代码: {result['raw_code']}")

if result["success"]:
    print("\n====== 生成的 PTX 代码 ======\n")
    print(result["asm"])

    # 分析核心指令
    asm_code = result["asm"]
    print("\n====== 核心指令分析 ======")

    instructions_found = []

    if "ld.global" in asm_code.lower():
        instructions_found.append("✓ 发现全局内存加载指令 (ld.global)")

    if "st.global" in asm_code.lower():
        instructions_found.append("✓ 发现全局内存存储指令 (st.global)")

    if "add.f32" in asm_code.lower() or "fma" in asm_code.lower():
        instructions_found.append("✓ 发现浮点加法指令 (add.f32/fma)")

    if "mad" in asm_code.lower() or "mul" in asm_code.lower():
        instructions_found.append("✓ 发现乘法/乘加指令 (mad/mul)")

    if "setp" in asm_code.lower():
        instructions_found.append("✓ 发现条件判断指令 (setp)")

    if "@" in asm_code:
        instructions_found.append("✓ 发现谓词寄存器使用 (@p)")

    for inst in instructions_found:
        print(inst)

    if not instructions_found:
        print("⚠ 未识别到预期的 PTX 指令模式")

else:
    print("\n====== 编译失败！错误信息 ======\n")
    print(result["stderr"])
