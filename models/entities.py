# models/entities.py
from typing import List

class Service:
    def __init__(self, id: int, cpu: float, ram: float, exec_time: float):
        self.id = id
        self.cpu = cpu          # unités demandées
        self.ram = ram
        self.exec_time = exec_time  # temps d'exécution sur VM de référence

    def __repr__(self):
        return f"S{self.id}(cpu={self.cpu}, ram={self.ram}, t={self.exec_time})"


class VM:
    def __init__(self, id: int, cpu_capacity: float, ram_capacity: float):
        self.id = id
        self.cpu_capacity = cpu_capacity
        self.ram_capacity = ram_capacity
        self.cpu_free = cpu_capacity
        self.ram_free = ram_capacity
        self.services: List[Service] = []
        self.completion_time = 0.0   # makespan de cette VM

    def can_host(self, service: Service) -> bool:
        return (self.cpu_free >= service.cpu and 
                self.ram_free >= service.ram)

    def assign(self, service: Service):
        if not self.can_host(service):
            raise ValueError(f"VM{self.id} ne peut pas héberger {service}")
        self.services.append(service)
        self.cpu_free -= service.cpu
        self.ram_free -= service.ram
        # On suppose exécution séquentielle sur la VM
        self.completion_time += service.exec_time

    def reset(self):
        self.cpu_free = self.cpu_capacity
        self.ram_free = self.ram_capacity
        self.services.clear()
        self.completion_time = 0.0

    def __repr__(self):
        return f"VM{self.id}(free_cpu={self.cpu_free:.1f}, free_ram={self.ram_free:.1f})"