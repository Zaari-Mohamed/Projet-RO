# utils/helpers.py
import streamlit as st
import json
import random
from models.entities import VM, Service
from typing import List, Dict

def load_data(vms_file: str = "data/vms.json", services_file: str = "data/services.json"):
    with open(vms_file) as f:
        vms_data = json.load(f)
    with open(services_file) as f:
        services_data = json.load(f)

    vms = [VM(**data) for data in vms_data]
    services = [Service(**data) for data in services_data]
    return services, vms

def generate_random_data(num_services=20, num_vms=6, seed=42):
    random.seed(seed)
    services = [
        Service(i,
                round(random.uniform(1, 5), 2),
                round(random.uniform(2, 12), 2),
                round(random.uniform(5, 40), 2))
        for i in range(num_services)
    ]
    vms = [
        VM(i,
           round(random.uniform(12, 28), 2),
           round(random.uniform(24, 64), 2))
        for i in range(num_vms)
    ]
    return services, vms

def compute_metrics(vms: List[VM], services: List[Service]) -> Dict:
    total_services = len(services)
    assigned = sum(len(vm.services) for vm in vms)
    makespan = max((vm.completion_time for vm in vms), default=0)
    cpu_util = sum((vm.cpu_capacity - vm.cpu_free) / vm.cpu_capacity for vm in vms) / len(vms) * 100
    ram_util = sum((vm.ram_capacity - vm.ram_free) / vm.ram_capacity for vm in vms) / len(vms) * 100
    return {
        "makespan": round(makespan, 2),
        "assigned": assigned,
        "rejected": total_services - assigned,
        "cpu_util_%": round(cpu_util, 2),
        "ram_util_%": round(ram_util, 2)
    }
