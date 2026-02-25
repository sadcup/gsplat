#!/usr/bin/env python3
"""
SimplePorting script for gsplat CUDA-to-MUSA migration.
Run inside musify_container:
    python3 /mnt/Codebases/gsplat/simple_porting_gsplat.py
"""

import os
import sys
import shutil

from torch_musa.utils.simple_porting import SimplePorting

PROJECT_DIR = "/mnt/Codebases/gsplat"

MAPPING_RULES = {
    # =========================================================
    # torch_musa header includes (CRITICAL - not in defaults)
    # Use quoted includes, NOT angle brackets
    # =========================================================
    "#include <c10/cuda/CUDAStream.h>": '#include "torch_musa/csrc/core/MUSAStream.h"',
    "#include <c10/cuda/CUDAGuard.h>": '#include "torch_musa/csrc/core/MUSAGuard.h"',
    "#include <c10/cuda/CUDACachingAllocator.h>": '#include "torch_musa/csrc/core/MUSACachingAllocator.h"',
    "#include <c10/cuda/CUDAFunctions.h>": '#include "torch_musa/csrc/core/MUSAFunctions.h"',
    "#include <c10/cuda/CUDAException.h>": '#include "torch_musa/csrc/core/MUSAException.h"',
    "#include <ATen/cuda/CUDAContext.h>": '#include "torch_musa/csrc/aten/musa/MUSAContext.h"',
    "#include <ATen/cuda/CUDAEvent.h>": '#include "torch_musa/csrc/core/MUSAEvent.h"',
    '#include <ATen/cuda/Atomic.cuh>': '#include "torch_musa/csrc/aten/musa/MUSAAtomic.muh"\nusing at::musa::gpuAtomicAdd;',
    "#include <ATen/cuda/CUDABlas.h>": '#include "torch_musa/csrc/aten/musa/MUSABlas.h"',

    # =========================================================
    # Namespace fixes (NOT in defaults)
    # =========================================================
    "at::cuda::": "at::musa::",
    "c10::cuda::": "c10::musa::",
    "::c10::cuda::": "::c10::musa::",

    # =========================================================
    # Compiler detection macros
    # =========================================================
    "__NVCC__": "__MUSACC__",

    # =========================================================
    # Device type checks (NOT in defaults)
    # =========================================================
    ".is_cuda()": ".is_privateuseone()",
    ", CUDA,": ", PrivateUse1,",
    
    # =========================================================
    # Local .cuh header includes
    # =========================================================
    '"Projection2DGS.cuh"': '"Projection2DGS.muh"',
    '"Cameras.cuh"': '"Cameras.muh"',
    '"Utils.cuh"': '"Utils.muh"',
}

def clean_existing_musa_dirs():
    """Remove existing _musa directories if they exist."""
    dirs_to_clean = [
        os.path.join(PROJECT_DIR, "gsplat/cuda/csrc_musa"),
        os.path.join(PROJECT_DIR, "gsplat/cuda/include_musa"),
    ]
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            print(f"Removing: {dir_path}")
            shutil.rmtree(dir_path)

def port_directories():
    """Port CUDA directories using SimplePorting."""
    
    # Port csrc directory - ignore third_party to avoid binary files
    print("Porting gsplat/cuda/csrc/ -> gsplat/cuda/csrc_musa/")
    SimplePorting(
        cuda_dir_path=os.path.join(PROJECT_DIR, "gsplat/cuda/csrc"),
        ignore_dir_paths=[
            os.path.join(PROJECT_DIR, "gsplat/cuda/csrc/third_party"),
        ],
        mapping_rule=MAPPING_RULES,
        drop_default_mapping=False,
    ).run()
    
    # Manually copy third_party/glm from original location
    src_glm = os.path.join(PROJECT_DIR, "gsplat/cuda/csrc/third_party/glm")
    dst_glm = os.path.join(PROJECT_DIR, "gsplat/cuda/csrc_musa/third_party/glm")
    if os.path.exists(src_glm) and not os.path.exists(dst_glm):
        print(f"Copying GLM: {src_glm} -> {dst_glm}")
        shutil.copytree(src_glm, dst_glm)
    
    # Port include directory
    print("Porting gsplat/cuda/include/ -> gsplat/cuda/include_musa/")
    SimplePorting(
        cuda_dir_path=os.path.join(PROJECT_DIR, "gsplat/cuda/include"),
        ignore_dir_paths=[],
        mapping_rule=MAPPING_RULES,
        drop_default_mapping=False,
    ).run()

def main():
    print("=== SimplePorting Script for gsplat ===")
    clean_existing_musa_dirs()
    port_directories()
    print("Done!")

if __name__ == "__main__":
    main()
