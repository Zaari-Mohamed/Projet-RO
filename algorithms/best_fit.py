# algorithms/best_fit.py
from models.entities import Service, VM
from typing import List, Dict

def best_fit(services: List[Service], vms: List[VM]) -> Dict[int, int]:
    assignment = {}
    for service in services:
        best_vm = None
        best_remaining = float('inf')
        for vm in vms:
            if vm.can_host(service):
                remaining = vm.cpu_free + vm.ram_free
                if remaining < best_remaining:
                    best_remaining = remaining
                    best_vm = vm
        if best_vm:
            best_vm.assign(service)
            assignment[service.id] = best_vm.id
    return assignment