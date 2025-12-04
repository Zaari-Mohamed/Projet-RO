# algorithms/max_min.py
# Identique à min_min mais on prend le temps MAXIMUM
from models.entities import Service, VM
from typing import List, Dict

def max_min(services: List[Service], vms: List[VM]) -> Dict[int, int]:
    assignment = {}
    remaining = services[:]
    while remaining:
        best_service = None
        best_vm = None
        best_time = -float('inf')

        for service in remaining:
            for vm in vms:
                if vm.can_host(service):
                    if service.exec_time > best_time:
                        best_time = service.exec_time
                        best_service = service
                        best_vm = vm

        if best_vm and best_service:
            best_vm.assign(best_service)
            assignment[best_service.id] = best_vm.id
            remaining.remove(best_service)
    return assignment