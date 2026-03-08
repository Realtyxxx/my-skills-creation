#!/usr/bin/env python3
"""
NVCC Compiler IR Generation Script

Compiles CUDA source files and generates intermediate representations (PTX, SASS, cubin).
Supports multi-architecture compilation and detailed compilation analysis.
"""

import argparse
import subprocess
import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Optional


def detect_gpu_arch() -> Optional[str]:
    """Detect the current GPU architecture using nvidia-smi."""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=compute_cap', '--format=csv,noheader'],
            capture_output=True, text=True, check=True
        )
        compute_cap = result.stdout.strip().split('\n')[0]
        # Convert 8.0 -> sm_80
        major, minor = compute_cap.split('.')
        return f"sm_{major}{minor}"
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
        return None


def build_nvcc_command(
    input_file: str,
    output_type: str,
    archs: List[str],
    options: List[str],
    verbose: bool,
    keep: bool
) -> List[str]:
    """Build the nvcc command based on parameters."""
    cmd = ['nvcc']

    # Add output type specific flags
    if output_type == 'ptx':
        cmd.append('--ptx')
        # For PTX, use compute_ architecture
        for arch in archs:
            compute_arch = arch.replace('sm_', 'compute_')
            cmd.append(f'-arch={compute_arch}')
            break  # PTX only needs one architecture

    elif output_type == 'cubin':
        cmd.append('--cubin')
        # For cubin, use gencode for multiple architectures
        if len(archs) == 1:
            cmd.append(f'-arch={archs[0]}')
        else:
            for arch in archs:
                compute_arch = arch.replace('sm_', 'compute_')
                cmd.append(f'-gencode=arch={compute_arch},code={arch}')

    elif output_type == 'sass':
        # SASS requires cubin first, then cuobjdump
        cmd.append('--cubin')
        cmd.append(f'-arch={archs[0]}')  # SASS for single architecture

    elif output_type == 'fatbin':
        cmd.append('--fatbin')
        for arch in archs:
            compute_arch = arch.replace('sm_', 'compute_')
            cmd.append(f'-gencode=arch={compute_arch},code={arch}')

    # Add verbose flag for compilation statistics
    if verbose:
        cmd.append('-Xptxas=-v')

    # Keep intermediate files
    if keep:
        cmd.append('-keep')

    # Add user-specified options
    cmd.extend(options)

    # Add input file
    cmd.append(input_file)

    return cmd


def expected_output_files(
    input_file: str,
    output_type: str,
    output_file: Optional[str] = None
) -> List[str]:
    """Return the expected compiler outputs for the requested type."""
    if output_file:
        return [output_file]

    base_name = Path(input_file).stem

    if output_type == 'ptx':
        return [f"{base_name}.ptx"]
    if output_type == 'cubin':
        return [f"{base_name}.cubin"]
    if output_type == 'fatbin':
        return [f"{base_name}.fatbin"]
    if output_type == 'sass':
        return [f"{base_name}.cubin"]

    return []


def compile_cuda(
    input_file: str,
    output_type: str,
    archs: List[str],
    options: List[str],
    verbose: bool,
    keep: bool,
    output_file: Optional[str] = None
) -> Dict[str, any]:
    """Compile CUDA file and generate specified output."""

    # Build command
    cmd = build_nvcc_command(input_file, output_type,
                             archs, options, verbose, keep)

    # Add output file if specified
    if output_file:
        cmd.extend(['-o', output_file])

    print(f"Executing: {' '.join(cmd)}")
    print()

    # Execute compilation
    result = subprocess.run(cmd, capture_output=True, text=True)

    compilation_result = {
        'success': result.returncode == 0,
        'stdout': result.stdout,
        'stderr': result.stderr,
        'command': ' '.join(cmd),
        'output_files': []
    }

    # If compilation succeeded, find output files
    if result.returncode == 0:
        compilation_result['output_files'] = [
            f for f in expected_output_files(input_file, output_type, output_file)
            if os.path.exists(f)
        ]

    return compilation_result


def extract_sass(cubin_file: str) -> str:
    """Extract SASS assembly from cubin file using cuobjdump."""
    try:
        result = subprocess.run(
            ['cuobjdump', '-sass', cubin_file],
            capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error extracting SASS: {e.stderr}"
    except FileNotFoundError:
        return "Error: cuobjdump not found. Please ensure CUDA toolkit is installed."


def parse_compilation_stats(stderr: str) -> Dict[str, any]:
    """Parse compilation statistics from nvcc stderr output."""
    stats = {}

    # Extract register usage
    reg_match = re.search(r'(\d+) registers', stderr)
    if reg_match:
        stats['registers'] = int(reg_match.group(1))

    # Extract shared memory usage
    smem_match = re.search(r'(\d+) bytes smem', stderr)
    if smem_match:
        stats['shared_memory_bytes'] = int(smem_match.group(1))

    # Extract constant memory usage
    cmem_match = re.search(r'(\d+) bytes cmem', stderr)
    if cmem_match:
        stats['constant_memory_bytes'] = int(cmem_match.group(1))

    # Extract spill information
    if 'spill' in stderr.lower():
        stats['has_spills'] = True

    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Compile CUDA code and generate intermediate representations'
    )
    parser.add_argument(
        '--input', '-i', required=True,
        help='Input CUDA source file (.cu)'
    )
    parser.add_argument(
        '--output-type', '-t', required=True,
        choices=['ptx', 'cubin', 'sass', 'fatbin', 'all'],
        help='Type of output to generate'
    )
    parser.add_argument(
        '--arch', '-a', default=None,
        help='GPU architecture(s), comma-separated (e.g., sm_80,sm_86). Auto-detect if not specified.'
    )
    parser.add_argument(
        '--output', '-o', default=None,
        help='Output file name (optional)'
    )
    parser.add_argument(
        '--options', default='',
        help='Additional nvcc options (space-separated)'
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Show detailed compilation statistics'
    )
    parser.add_argument(
        '--keep', '-k', action='store_true',
        help='Keep all intermediate files'
    )

    args = parser.parse_args()

    if args.output_type == 'all' and args.output:
        parser.error(
            '--output cannot be used with --output-type all; '
            'run each output type separately or omit --output'
        )

    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)

    # Determine architectures
    if args.arch:
        archs = [a.strip() for a in args.arch.split(',')]
    else:
        detected_arch = detect_gpu_arch()
        if detected_arch:
            archs = [detected_arch]
            print(f"Auto-detected GPU architecture: {detected_arch}")
        else:
            print("Warning: Could not detect GPU architecture, using sm_80 as default")
            archs = ['sm_80']

    # Parse additional options
    options = args.options.split() if args.options else []

    # Compile
    if args.output_type == 'all':
        output_types = ['ptx', 'cubin', 'sass']
    else:
        output_types = [args.output_type]

    for output_type in output_types:
        print(f"\n{'='*60}")
        print(f"Generating {output_type.upper()}")
        print(f"{'='*60}\n")

        result = compile_cuda(
            args.input, output_type, archs, options,
            args.verbose, args.keep, args.output
        )

        if result['success']:
            print("✓ Compilation successful")
            print(f"\nGenerated files:")
            for f in result['output_files']:
                size = os.path.getsize(f)
                print(f"  - {f} ({size} bytes)")

            # Show compilation statistics if verbose
            if args.verbose and result['stderr']:
                stats = parse_compilation_stats(result['stderr'])
                if stats:
                    print(f"\nCompilation Statistics:")
                    for key, value in stats.items():
                        print(f"  {key}: {value}")

            # Extract SASS if requested
            if output_type == 'sass' and result['output_files']:
                cubin_file = result['output_files'][0]
                print(f"\nExtracting SASS from {cubin_file}...")
                sass_output = extract_sass(cubin_file)

                # Save SASS to file
                sass_file = str(Path(cubin_file).with_suffix('.sass'))
                with open(sass_file, 'w') as f:
                    f.write(sass_output)
                print(f"✓ SASS saved to {sass_file}")

                # Show first few lines
                lines = sass_output.split('\n')[:20]
                print(f"\nFirst 20 lines of SASS:")
                print('\n'.join(lines))
        else:
            print("✗ Compilation failed")
            if result['stderr']:
                print(f"\nError output:")
                print(result['stderr'])
            sys.exit(1)


if __name__ == '__main__':
    main()
