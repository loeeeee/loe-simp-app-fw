from ...loe_simp_app_fw import Prometheus, Logger
from random import random

def main() -> None:
    Logger.bootstrap("./log")
    Logger.info("Start main")
    monitor_one = Prometheus.get("Alpha")
    monitor_two = Prometheus.get("Beta")
    for i in range(10000):
        if random() < 0.5:
            monitor_one.success("0")
        else:
            monitor_one.failure("0")

        if random() < 0.7:
            monitor_two.success("9")
            monitor_two.failure("12")
        else:
            monitor_two.failure("9")
            monitor_two.success("12")
main()