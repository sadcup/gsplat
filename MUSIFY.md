# MUSIFY.md - MUSA Migration State

## Project Information
- **Project**: gsplat
- **Original Repo**: https://github.com/nerfstudio-project/gsplat
- **Branch**: musa
- **Started**: 2026-02-25
- **Status**: IN_PROGRESS

## Project Structure Analysis

### Folder Hierarchy
```
gsplat/
├── setup.py                    # Build system
├── gsplat/                     # Main package
│   ├── __init__.py            # Package entry point
│   ├── cuda/
│   │   ├── csrc/              # CUDA sources (20 .cu, 3 .cuh, 9 .cpp)
│   │   │   ├── *.cu           # CUDA kernel files
│   │   │   ├── *.cpp          # C++ wrapper files
│   │   │   ├── *.cuh          # CUDA header files
│   │   │   └── third_party/   # GLM math library
│   │   └── include/           # CUDA headers (2 .cuh)
│   ├── rendering.py
│   ├── ...
├── examples/                   # Example scripts
└── tests/                      # Test suite
```

### Third-Party Libraries Found
| Library | Location | Contains CUDA | Action |
|---------|----------|---------------|--------|
| GLM | gsplat/cuda/csrc/third_party/glm | No | Patch for MUSA compatibility |

### CUDA Source Directories
| Directory | .cu Files | .cuh Files | .cpp Files | Notes |
|-----------|-----------|------------|------------|-------|
| gsplat/cuda/csrc/ | 20 | 3 | 9 | Main CUDA kernels |
| gsplat/cuda/include/ | 0 | 2 | 0 | CUDA header files |

### CUDA-Dependent Python Packages
No external CUDA-dependent packages in requirements. All CUDA code is built locally.

### PyTorch Python Files
#### Library Code (add `import torch_musa` only)
- gsplat/__init__.py (main package entry)
- gsplat/cuda/_wrapper.py (CUDA wrapper functions)
- gsplat/cuda/_backend.py (backend loading)
- gsplat/cuda/_torch_impl.py (torch implementations)
- gsplat/cuda/_torch_impl_2dgs.py
- gsplat/rendering.py
- gsplat/distributed.py
- gsplat/strategy/*.py (strategy implementations)
- And other files in gsplat/

#### Application Code (may need cuda->musa conversion)
- examples/*.py (example scripts)
- tests/*.py (test scripts)
- profiling/*.py (profiling scripts)

### Build System Summary
- **Build tool**: setuptools with torch.utils.cpp_extension
- **Extension type**: CUDAExtension
- **Key compile flags**: --use_fast_math, -std=c++17, -O3
- **Source collection method**: glob patterns

## Migration Plan (Bottom-to-Top)

### Phase 1: C++ / CUDA Source Porting
1. **Patch GLM library** for MUSA compatibility (add __MUSACC__ detection)
2. **Run SimplePorting** on gsplat/cuda/csrc/ and gsplat/cuda/include/
3. **Custom mappings**: None required beyond SimplePorting defaults

### Phase 2: Build System Modification
4. **Modify setup.py** to support MUSA build path:
   - Add `FORCE_MUSA` environment variable check
   - Replace CUDAExtension with MUSAExtension
   - Update source file paths to use `_musa` directories
   - Remove unsupported flags: `--use_fast_math`

### Phase 3: Build and Fix
5. **Build with MUSA**: `FORCE_MUSA=1 pip install -e . --no-build-isolation`
6. **Fix compilation errors iteratively**

### Phase 4: Python Conversion
7. **Library code**: Add `import torch_musa` to gsplat/__init__.py
8. **Application code**: Convert cuda references in examples/tests as needed

### Phase 5: Verification
9. **Import test**: `python3 -c "import gsplat; print('OK')"`
10. **Functional test**: Run test suite

## Migration Progress

### Current Step
- [x] Step 1: Docker Environment Setup
- [x] Step 2: MUSAExtensionSummary.md Version Check
- [x] Step 3: Project Analysis and Planning
- [x] Step 4: Create musa Branch
- [ ] Step 5: Detect CUDA Source Folders
- [ ] Step 6: Run SimplePorting
- [ ] Step 7: Modify setup.py
- [ ] Step 8: Build & Fix Errors
- [ ] Step 9: Python Conversion
- [ ] Step 10: Verification
- [ ] Step 11: Profiling & Optimization (Optional)
- [ ] Step 12: Final Commit

## Completed Steps

### Step 4: Create musa Branch
**Date**: 2026-02-25
**Action**: Created musa branch from main/master
**Result**: SUCCESS
**Notes**: Branch is ready for migration work

### Step 3: Project Analysis and Planning
**Date**: 2026-02-25
**Action**: Deep analysis of project structure, dependencies, and CUDA usage
**Result**: SUCCESS

## Issues Encountered
(none yet)

## Manual Fixes Applied
(none yet)

## Build Log Summary
(no builds yet)

## Files Changed Summary
(to be updated)

## Verification Command
```bash
python3 -c "import gsplat; print('OK')"
```
