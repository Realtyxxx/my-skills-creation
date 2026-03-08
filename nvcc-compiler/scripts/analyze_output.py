#!/usr/bin/env python3
"""
NVCC Output Analysis Script

Analyzes PTX, SASS, and cubin files to extract useful information about
compilation results, including instruction counts, register usage, and more.
"""

import argparse
import subprocess
import sys
import os
import re
from pathlib import Path
from typing import Dict, List, Optional


def analyze_ptx(ptx_file: str) -> Dict[str, any]:
    """Analyze PTX file and extract key information."""
    with open(ptx_file, 'r') as f:
        content = f.read()

    info = {
        'file': ptx_file,
        'size_bytes': os.path.getsize(ptx_file),
        'functions': [],
        'total_instructions': 0,
        'instruction_types': {},
        'register_usage': {},
        'shared_memory': []
    }

    # Extract functions
    func_pattern = r'\.visible\s+\.entry\s+(\w+)\s*\('
    functions = re.findall(func_pattern, content)
    info['functions'] = functions

    # Count instructions (lines starting with whitespace followed by instruction)
    instruction_pattern = r'^\s+(\w+)'
    instructions = re.findall(instruction_pattern, content, re.MULTILINE)
    info['total_instructions'] = len(instructions)

    # Count instruction types
    for inst in instructions:
        info['instruction_types'][inst] = info['instruction_types'].get(
            inst, 0) + 1

    # Extract register declarations
    reg_pattern = r'\.reg\s+\.(\w+)\s+%(\w+)(?:<(\d+)>)?'
    registers = re.findall(reg_pattern, content)
    for reg_type, _reg_name, reg_count in registers:
        info['register_usage'][reg_type] = (
            info['register_usage'].get(reg_type, 0) + int(reg_count or 1)
        )

    # Extract shared memory declarations
    smem_pattern = r'\.shared\s+\.align\s+(\d+)\s+\.(\w+)\s+(\w+)\[(\d+)\]'
    shared_mems = re.findall(smem_pattern, content)
    for align, dtype, name, size in shared_mems:
        info['shared_memory'].append({
            'name': name,
            'type': dtype,
            'size': int(size),
            'alignment': int(align)
        })

    return info


def analyze_cubin(cubin_file: str) -> Dict[str, any]:
    """Analyze cubin file using cuobjdump."""
    info = {
        'file': cubin_file,
        'size_bytes': os.path.getsize(cubin_file),
        'sections': [],
        'symbols': [],
        'architecture': None
    }

    try:
        # Get ELF information
        result = subprocess.run(
            ['cuobjdump', '-elf', cubin_file],
            capture_output=True, text=True, check=True
        )
        elf_output = result.stdout

        # Extract architecture
        arch_match = re.search(r'arch\s*=\s*sm_(\d+)', elf_output)
        if arch_match:
            info['architecture'] = f"sm_{arch_match.group(1)}"

        # Get symbol information
        result = subprocess.run(
            ['cuobjdump', '-symbols', cubin_file],
            capture_output=True, text=True, check=True
        )
        symbols_output = result.stdout

        # Parse symbols
        symbol_pattern = r'(\w+)\s+(\w+)\s+(\w+)\s+([\w\.]+)'
        symbols = re.findall(symbol_pattern, symbols_output)
        info['symbols'] = [
            {'name': s[3], 'type': s[1], 'binding': s[0]}
            for s in symbols
        ]

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        info['error'] = str(e)

    return info


def analyze_sass(sass_file: str) -> Dict[str, any]:
    """Analyze SASS assembly file."""
    with open(sass_file, 'r') as f:
        content = f.read()

    info = {
        'file': sass_file,
        'size_bytes': os.path.getsize(sass_file),
        'functions': [],
        'total_instructions': 0,
        'instruction_types': {},
        'control_flow': {
            'branches': 0,
            'jumps': 0,
            'calls': 0,
            'returns': 0
        }
    }

    # Extract function names
    func_pattern = r'Function\s*:\s*(\w+)'
    functions = re.findall(func_pattern, content)
    info['functions'] = functions

    # Count instructions (SASS format: address instruction operands)
    # Example: /*0010*/  MOV R1, c[0x0][0x28];
    inst_pattern = r'/\*[0-9A-Fa-f]+\*/\s+(?:@\S+\s+)?([A-Za-z][A-Za-z0-9_]*)'
    instructions = re.findall(inst_pattern, content)
    info['total_instructions'] = len(instructions)

    # Count instruction types
    for inst in instructions:
        info['instruction_types'][inst] = info['instruction_types'].get(
            inst, 0) + 1

        # Count control flow instructions
        if inst.startswith('BR'):
            info['control_flow']['branches'] += 1
        elif inst.startswith('JMP'):
            info['control_flow']['jumps'] += 1
        elif inst.startswith('CALL'):
            info['control_flow']['calls'] += 1
        elif inst.startswith('RET'):
            info['control_flow']['returns'] += 1

    return info


def print_ptx_analysis(info: Dict[str, any]):
    """Print PTX analysis results."""
    print(f"\n{'='*60}")
    print(f"PTX Analysis: {info['file']}")
    print(f"{'='*60}\n")

    print(f"File Size: {info['size_bytes']} bytes")
    print(
        f"Functions: {', '.join(info['functions']) if info['functions'] else 'None'}")
    print(f"Total Instructions: {info['total_instructions']}")

    if info['register_usage']:
        print(f"\nRegister Usage:")
        for reg_type, reg_count in info['register_usage'].items():
            print(f"  {reg_type}: {reg_count} registers")

    if info['shared_memory']:
        print(f"\nShared Memory:")
        for smem in info['shared_memory']:
            print(
                f"  {smem['name']}: {smem['type']}[{smem['size']}] (align {smem['alignment']})")

    if info['instruction_types']:
        print(f"\nTop 10 Instruction Types:")
        sorted_insts = sorted(
            info['instruction_types'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        for inst, count in sorted_insts:
            percentage = (count / info['total_instructions']) * 100
            print(f"  {inst:15s}: {count:5d} ({percentage:5.1f}%)")


def print_cubin_analysis(info: Dict[str, any]):
    """Print cubin analysis results."""
    print(f"\n{'='*60}")
    print(f"Cubin Analysis: {info['file']}")
    print(f"{'='*60}\n")

    print(f"File Size: {info['size_bytes']} bytes")

    if info.get('architecture'):
        print(f"Architecture: {info['architecture']}")

    if info.get('symbols'):
        print(f"\nSymbols ({len(info['symbols'])}):")
        for sym in info['symbols'][:10]:  # Show first 10
            print(f"  {sym['name']:30s} ({sym['type']}, {sym['binding']})")
        if len(info['symbols']) > 10:
            print(f"  ... and {len(info['symbols']) - 10} more")

    if info.get('error'):
        print(f"\nError: {info['error']}")


def print_sass_analysis(info: Dict[str, any]):
    """Print SASS analysis results."""
    print(f"\n{'='*60}")
    print(f"SASS Analysis: {info['file']}")
    print(f"{'='*60}\n")

    print(f"File Size: {info['size_bytes']} bytes")
    print(
        f"Functions: {', '.join(info['functions']) if info['functions'] else 'None'}")
    print(f"Total Instructions: {info['total_instructions']}")

    print(f"\nControl Flow:")
    for key, value in info['control_flow'].items():
        print(f"  {key.capitalize()}: {value}")

    if info['instruction_types']:
        print(f"\nTop 10 Instruction Types:")
        sorted_insts = sorted(
            info['instruction_types'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        for inst, count in sorted_insts:
            percentage = (count / info['total_instructions']) * 100
            print(f"  {inst:15s}: {count:5d} ({percentage:5.1f}%)")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze NVCC compilation output (PTX, SASS, cubin)'
    )
    parser.add_argument(
        '--file', '-f', required=True,
        help='File to analyze'
    )
    parser.add_argument(
        '--type', '-t',
        choices=['ptx', 'cubin', 'sass', 'auto'],
        default='auto',
        help='File type (auto-detect by extension if not specified)'
    )

    args = parser.parse_args()

    # Check if file exists
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found", file=sys.stderr)
        sys.exit(1)

    # Determine file type
    file_type = args.type
    if file_type == 'auto':
        ext = Path(args.file).suffix.lower()
        if ext == '.ptx':
            file_type = 'ptx'
        elif ext == '.cubin':
            file_type = 'cubin'
        elif ext == '.sass':
            file_type = 'sass'
        else:
            print(
                f"Error: Cannot auto-detect file type from extension '{ext}'", file=sys.stderr)
            print("Please specify --type explicitly", file=sys.stderr)
            sys.exit(1)

    # Analyze based on type
    if file_type == 'ptx':
        info = analyze_ptx(args.file)
        print_ptx_analysis(info)
    elif file_type == 'cubin':
        info = analyze_cubin(args.file)
        print_cubin_analysis(info)
    elif file_type == 'sass':
        info = analyze_sass(args.file)
        print_sass_analysis(info)


if __name__ == '__main__':
    main()
