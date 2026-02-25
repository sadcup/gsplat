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
- [x] Step 5: Detect CUDA Source Folders
- [x] Step 6: Run SimplePorting
- [x] Step 7: Modify setup.py
- [x] Step 8: Build & Fix Errors
- [x] Step 9: Python Conversion
- [x] Step 10: Verification
- [ ] Step 11: Profiling & Optimization (Optional)
- [ ] Step 12: Final Commit
- [ ] Step 11: Profiling & Optimization (Optional)
- [ ] Step 12: Final Commit

## Completed Steps

### Step 4: Create musa Branch
**Date**: 2026-02-25
**Action**: Created musa branch from main/master
**Result**: SUCCESS
**Notes**: Branch is ready for migration work

### Step 5: Detect CUDA Source Folders
**Date**: 2026-02-25
**Action**: Identified CUDA source directories from planning
**Result**: SUCCESS
**Notes**:
- gsplat/cuda/csrc/: 20 .cu, 3 .cuh, 9 .cpp files
- gsplat/cuda/include/: 2 .cuh files
- Excluded: third_party/glm (will patch separately)

### Step 6: Run SimplePorting
**Date**: 2026-02-25
**Action**: Ran SimplePorting on CUDA directories
**Result**: SUCCESS
**Notes**:
- gsplat/cuda/csrc_musa/: 20 .mu, 1 .muh, 8 .cpp, 8 .h files
- gsplat/cuda/include_musa/: 2 .muh, 3 .h files
- GLM patched for MUSA compatibility

### Step 3: Project Analysis and Planning
**Date**: 2026-02-25
**Action**: Deep analysis of project structure, dependencies, and CUDA usage
**Result**: SUCCESS

## Issues Encountered
1. **GLM MUSA detection**: GLM didn't recognize MUSA compiler - fixed by patching
2. **std::array::at() in device code**: `.at()` throws exceptions in __device__ functions - replaced with array subscript
3. **Register allocation failure**: MUSA compiler ran out of registers for backward kernels - reduced optimization and added #pragma unroll 4
4. **Python torch.cuda compatibility**: torch.cuda functions don't work on MUSA - added MUSA-aware helper functions

## Manual Fixes Applied
(none yet)

### Fix #1: GLM MUSA Compatibility Patch
**File**: gsplat/cuda/csrc/third_party/glm/glm/detail/setup.hpp
**Change**:
```diff
-#if (GLM_COMPILER & GLM_COMPILER_CUDA) || (GLM_COMPILER & GLM_COMPILER_HIP)
+#if (GLM_COMPILER & GLM_COMPILER_CUDA) || (GLM_COMPILER & GLM_COMPILER_HIP) || defined(__MUSACC__)
```
**Reason**: Allow GLM to recognize MUSA compiler as CUDA-compatible

### Fix #2: GLM platform.h MUSA Detection
**File**: gsplat/cuda/csrc/third_party/glm/glm/simd/platform.h
**Change**:
```diff
+// MUSA (musacc)
+#elif defined(__MUSACC__)
+#	define GLM_COMPILER GLM_COMPILER_CUDA80
```
**Reason**: Add MUSA compiler detection to GLM

### Fix #3: std::array::at() in device code
**File**: gsplat/cuda/include_musa/Cameras.muh (lines 1068, 1071)
**Change**:
```diff
- dist.pixeldist_to_angle_poly.at(1)
+ dist.pixeldist_to_angle_poly[1]
```
**Reason**: `.at()` throws exception in device code; use array subscript instead

### Fix #4: Reduce optimization to -O2
**File**: setup.py (line 92)
**Change**:
```diff
- mcc_flags += ["-O3", "-std=c++17"]
+ mcc_flags += ["-O2", "-std=c++17"]
```
**Reason**: Reduce register pressure for MUSA compiler

### Fix #5: Add #pragma unroll 4 to backward kernels
**Files**: 
- gsplat/cuda/csrc_musa/RasterizeToPixels3DGSBwd.mu
- gsplat/cuda/csrc_musa/RasterizeToPixels2DGSBwd.mu  
- gsplat/cuda/csrc_musa/RasterizeToPixelsFromWorld3DGSBwd.mu
**Change**: Changed all `#pragma unroll` to `#pragma unroll 4`
**Reason**: Reduce register pressure in backward pass kernels

### Fix #6: Python torch.cuda to MUSA compatibility
**Files**: Multiple Python files modified for MUSA compatibility:
- gsplat/__init__.py - Added `import torch_musa`
- gsplat/cuda/_wrapper.py - Added `_sync_device()` and `_empty_cache()` helpers
- gsplat/profile.py - Added `_sync()` helper for torch.cuda.synchronize()
- gsplat/strategy/default.py - Added `_empty_cache()` helper
- gsplat/strategy/mcmc.py - Added `_empty_cache()` helper
- gsplat/distributed.py - Added `_get_device_count()` and `_set_device()` helpers
**Change**: Replaced torch.cuda calls with device-agnostic functions that check for MUSA first
**Reason**: torch.cuda doesn't work on MUSA; need to use torch.musa functions

## Build Log Summary
- **Build 1**: Initial build - Failed (GLM MUSA detection issues)
- **Build 2**: GLM patched - Failed (std::array::at() errors)
- **Build 3**: Fixed .at() - Failed (register allocation errors)
- **Build 4**: Added #pragma unroll 4 + -O2 - **SUCCESS**

## Verification Command
```bash
python3 -c "import gsplat; print('OK')"
```
