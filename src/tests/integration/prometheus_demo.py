from ...loe_simp_app_fw import prometheus, Logger
from random import random

def main() -> None:
    Logger.bootstrap("./log")
    Logger.info("Start main")
    for i in range(10000):
        if random() < 0.5:
            prometheus.success("A")
        else:
            prometheus.failure("A")

main()