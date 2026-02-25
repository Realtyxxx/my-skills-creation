#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Godbolt 手动测试 - 快速参考
一行命令快速测试各种场景
"""

from godbolt_test import compile_and_analyze_asm

# ============================================================================
# 快速测试模板 - 复制粘贴到 Python REPL 中使用
# ============================================================================

def quick_test(code, flags="-O3 -arch=sm_90 --ptx"):
    """快速测试模板"""
    result = compile_and_analyze_asm(code, flags=flags)
    if result["success"]:
        asm = result["asm"]
        print(f"✓ 编译成功 | 代码行数: {len(asm.split(chr(10)))}")
        print(f"  ld.global: {asm.count('ld.global')} | st.global: {asm.count('st.global')}")
        print(f"  ld.shared: {asm.count('ld.shared')} | st.shared: {asm.count('st.shared')}")
        print(f"  mul: {asm.count('mul.f32')} | fma: {asm.count('fma')} | add: {asm.count('add.f32')}")
        print(f"  bar.sync: {asm.count('bar.sync')} | bra: {asm.count('bra')}")
        return asm
    else:
        print(f"✗ 编译失败")
        print(result["stderr"])
        return None

# ============================================================================
# 测试场景 1: 基础向量操作
# ============================================================================

print("=" * 70)
print("场景 1: 基础向量加法")
print("=" * 70)

vector_add = """
extern "C" __global__ void add(float *a, float *b, float *c, int n) {
    int i = threadIdx.x + blockIdx.x * blockDim.x;
    if (i < n) c[i] = a[i] + b[i];
}
"""

quick_test(vector_add)

# ============================================================================
# 测试场景 2: 循环展开
# ============================================================================

print("\n" + "=" * 70)
print("场景 2: 循环展开 (4 次迭代)")
print("=" * 70)

loop_unroll = """
extern "C" __global__ void sum4(float *input, float *output, int n) {
    int tid = threadIdx.x + blockIdx.x * blockDim.x;
    if (tid < n) {
        float sum = 0.0f;
        for (int i = 0; i < 4; i++) {
            sum += input[tid * 4 + i];
        }
        output[tid] = sum;
    }
}
"""

quick_test(loop_unroll)

# ============================================================================
# 测试场景 3: 共享内存
# ============================================================================

print("\n" + "=" * 70)
print("场景 3: 共享内存归约")
print("=" * 70)

shared_reduce = """
extern "C" __global__ void reduce(float *input, float *output) {
    __shared__ float sdata[256];
    int tid = threadIdx.x;

    sdata[tid] = input[tid];
    __syncthreads();

    for (int s = 128; s > 0; s >>= 1) {
        if (tid < s) {
            sdata[tid] += sdata[tid + s];
        }
        __syncthreads();
    }

    if (tid == 0) output[0] = sdata[0];
}
"""

quick_test(shared_reduce)

# ============================================================================
# 测试场景 4: 对比优化级别
# ============================================================================

print("\n" + "=" * 70)
print("场景 4: 对比 -O0 vs -O3")
print("=" * 70)

test_code = """
extern "C" __global__ void fma_test(float *a, float *b, float *c, float *d) {
    int i = threadIdx.x;
    d[i] = a[i] * b[i] + c[i];
}
"""

print("\n-O0:")
quick_test(test_code, flags="-O0 -arch=sm_90 --ptx")

print("\n-O3:")
quick_test(test_code, flags="-O3 -arch=sm_90 --ptx")

# ============================================================================
# 测试场景 5: 不同架构
# ============================================================================

print("\n" + "=" * 70)
print("场景 5: 对比 sm_80 (Ampere) vs sm_90 (Hopper)")
print("=" * 70)

arch_test = """
extern "C" __global__ void simple(float *x) {
    x[threadIdx.x] = x[threadIdx.x] * 2.0f;
}
"""

print("\nsm_80 (Ampere):")
asm_80 = quick_test(arch_test, flags="-O3 -arch=sm_80 --ptx")

print("\nsm_90 (Hopper):")
asm_90 = quick_test(arch_test, flags="-O3 -arch=sm_90 --ptx")

# ============================================================================
# 使用技巧
# ============================================================================

print("\n" + "=" * 70)
print("使用技巧")
print("=" * 70)

print("""
1. 在 Python REPL 中使用:
   >>> from godbolt_test import compile_and_analyze_asm
   >>> result = compile_and_analyze_asm(code, flags="-O3 -arch=sm_90 --ptx")
   >>> print(result["asm"])

2. 快速查看特定指令:
   >>> asm = result["asm"]
   >>> [line for line in asm.split('\\n') if 'ld.global' in line]

3. 统计指令数量:
   >>> asm.count('fma')

4. 保存结果到文件:
   >>> with open('output.ptx', 'w') as f: f.write(result["asm"])

5. 对比两个版本:
   >>> len(result_v1["asm"]) - len(result_v2["asm"])

常用编译选项:
  -O0, -O1, -O2, -O3          优化级别
  -arch=sm_80, sm_86, sm_90   目标架构
  --ptx                       生成 PTX 而不是 SASS
  -lineinfo                   包含行号信息
  -use_fast_math              快速数学库

常见指令:
  ld.global / st.global       全局内存访问
  ld.shared / st.shared       共享内存访问
  ld.param                    参数加载
  add.f32 / mul.f32           浮点运算
  fma.rn.f32                  融合乘加
  mad.lo.s32                  整数乘加
  setp                        条件判断
  bar.sync                    线程同步
  bra                         分支跳转
""")
