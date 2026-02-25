"""Pytest configuration for MUSA support."""
import torch
import torch_musa

# Patch torch.cuda.is_available to also check MUSA
_original_cuda_is_available = torch.cuda.is_available

def _patched_cuda_is_available():
    """Check for both CUDA and MUSA."""
    if hasattr(torch, 'musa') and torch.musa.is_available():
        return True
    return _original_cuda_is_available()

torch.cuda.is_available = _patched_cuda_is_available

# Also patch torch.cuda.device_count
_original_cuda_device_count = torch.cuda.device_count

def _patched_device_count():
    """Get device count for CUDA or MUSA."""
    if hasattr(torch, 'musa') and torch.musa.is_available():
        return torch.musa.device_count()
    return _original_cuda_device_count()

torch.cuda.device_count = _patched_device_count

# Override torch.cuda.device to return musa device
_original_cuda_device = torch.cuda.device

class _MusaDevice:
    """Wrapper that makes torch.cuda.device return musa device."""
    def __init__(self, device_or_id):
        if hasattr(torch, 'musa') and torch.musa.is_available():
            if isinstance(device_or_id, int):
                self._device = torch.musa.device(device_or_id)
            else:
                # Extract index from device string
                device_str = str(device_or_id)
                if ':' in device_str:
                    idx = int(device_str.split(':')[1])
                    self._device = torch.musa.device(idx)
                else:
                    self._device = torch.musa.device(0)
        else:
            self._device = _original_cuda_device(device_or_id)
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass
    
    def __getattr__(self, name):
        return getattr(self._device, name)

def _patched_cuda_device_func(device=None):
    """Patch torch.cuda.device to return musa device."""
    return _MusaDevice(device if device is not None else 0)

torch.cuda.device = _patched_cuda_device_func
