from typing import Any, Dict, List, Union


import psutil
import pynvml


def get_cuda_gpus() -> List[Dict[str, Union[int, str]]]:
    """Get stastics on all CUDA GPUs in the system.

    Returns:
        List of detected CUDA gpus on the system.  Each entry
        in the list is a dictionary with the following information: GPU ID
        (id), product name (type), current fan speed as a percentage of
        maximum (fan_speed), current temperature in Celcius (temperature),
        performance mode (mode), power usage in Watts (power_used), maximum
        possible power usage in Watts (power_available), memory usage in MiB
        (memory_used), total GPU memory in MiB (memory_available), and
        utilization as a percentage of cycles (utilization).

        ```procs``` is a list of processes currently running on the GPU.  Each
        entry is a dictionary with the following information: GPU ID (gpu),
        username of the process owner (owner), process type (type) with
        possible values 'C' for compute or 'G' for graphics, process name as
        reported by nvidia-smi (name), the command used to launch the process
        (command), and the memory used by the process in MiB (memory).
    """
    pynvml.nvmlInit()
    gpus = []
    for gpu_id in range(pynvml.nvmlDeviceGetCount()):
        gpu = {}
        gpu['id'] = gpu_id
        handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
        gpu['type'] = pynvml.nvmlDeviceGetName(handle)
        gpu['fan_speed'] = pynvml.nvmlDeviceGetFanSpeed(handle)
        gpu['temperature'] = pynvml.nvmlDeviceGetTemperature(handle, 0)
        gpu['mode'] = pynvml.nvmlDeviceGetPerformanceState(handle)
        gpu['power_used'] = pynvml.nvmlDeviceGetPowerUsage(handle)
        gpu['power_total'] = pynvml.nvmlDeviceGetPowerManagementLimit(handle)
        gpu['memory_used'] = pynvml.nvmlDeviceGetMemoryInfo(handle).used
        gpu['memory_total'] = pynvml.nvmlDeviceGetMemoryInfo(handle).total
        gpus.append(gpu)
    return gpus


def get_cuda_procs() -> List[Dict[str, Union[int, str]]]:
    pynvml.nvmlInit()
    procs = []
    for gpu_id in range(pynvml.nvmlDeviceGetCount()):
        handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
        gpu_procs = pynvml.nvmlDeviceGetComputeRunningProcesses(handle) + pynvml.nvmlDeviceGetGraphicsRunningProcesses(handle)
        for proc in gpu_procs:
            info = {}
            info['gpu'] = gpu_id
            info['type'] = 'compute' if proc in pynvml.nvmlDeviceGetComputeRunningProcesses(handle) else 'graphics'
            info['memory'] = proc.usedGpuMemory
            os_proc = psutil.Process(proc.pid)
            info['owner'] = os_proc.username()
            info['name'] = os_proc.name()
            info['command'] = ' '.join(os_proc.cmdline())
            procs.append(info)
    return procs

