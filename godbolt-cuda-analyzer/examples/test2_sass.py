# -*- coding: utf-8 -*-
"""SASS 模式测试 - 使用 cuclang + binary=True 获取真实 GPU 机器码"""
import sys, os
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SKILL_DIR)

from godbolt_test import compile_and_analyze_asm

CUDA_CODE = r'''
__global__ void vectorAdd(float *a, float *b, float *c, int n) {
    int i = threadIdx.x + blockIdx.x * blockDim.x;
    if (i < n) c[i] = a[i] + b[i];
}
'''

def test_sass():
    print("=" * 50)
    print("SASS 模式测试 (cuclang + binary=True)")
    print("=" * 50)

    result = compile_and_analyze_asm(CUDA_CODE, output_mode="sass")

    print(f"编译器: {result.get('compiler_used', 'N/A')}")
    print(f"模式:   {result.get('mode', 'N/A')}")
    print(f"成功:   {result['success']}")

    if result["success"]:
        asm = result["asm"]
        lines = asm.split("\n")
        print(f"SASS 行数: {len(lines)}")
        print()

        # SASS 关键指令统计
        sass_ops = {
            "LDG": "Global Load",
            "STG": "Global Store",
            "LDS": "Shared Load",
            "STS": "Shared Store",
            "FADD": "FP32 Add",
            "FFMA": "FP32 FMA",
            "IMAD": "Int Multiply-Add",
            "ISETP": "Int Set Predicate",
            "S2R": "Special Reg Read",
            "EXIT": "Thread Exit",
            "BRA": "Branch",
        }
        print("SASS 指令统计:")
        for op, desc in sass_ops.items():
            count = sum(1 for l in lines if op in l)
            if count > 0:
                print(f"  {op:8s} ({desc}): {count}")

        print()
        print("前 30 行 SASS:")
        print("-" * 50)
        for line in lines[:30]:
            print(line)
    else:
        print(f"错误: {result['stderr']}")

def test_ptx_unchanged():
    """确认 PTX 模式不受影响"""
    print()
    print("=" * 50)
    print("PTX 模式兼容性测试")
    print("=" * 50)

    result = compile_and_analyze_asm(CUDA_CODE, output_mode="ptx")
    print(f"编译器: {result.get('compiler_used', 'N/A')}")
    print(f"模式:   {result.get('mode', 'N/A')}")
    print(f"成功:   {result['success']}")

    if result["success"]:
        asm = result["asm"]
        has_ptx = any(kw in asm for kw in ["ld.global", "st.global", "ld.param"])
        print(f"包含 PTX 指令: {has_ptx}")
        print(f"PTX 行数: {len(asm.split(chr(10)))}")

if __name__ == "__main__":
    test_sass()
    test_ptx_unchanged()
