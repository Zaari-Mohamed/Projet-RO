# algorithms/first_fit.py
from models.entities import Service, VM
from typing import List, Dict

def first_fit(services: List[Service], vms: List[VM]) -> Dict[int, int]:
    assignment = {}
    for service in services:
        for vm in vms:
            if vm.can_host(service):
                vm.assign(service)
                assignment[service.id] = vm.id
                break
    return assignment