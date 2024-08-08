from typing import ClassVar, Dict, NamedTuple, TypeAlias, List, Tuple
from tabulate import tabulate

from .logger import Logger

class _Counter(NamedTuple):
    success: int
    failure: int

Event: TypeAlias = str


class PrometheusWorker:
    def __init__(self, name: str, *args, **kwargs) -> None:
        self.name: str = name
        self.event_counter: Dict[Event, NamedTuple] = {}
        pass

    def success(self, event: Event, *args, msg: str = "", **kwargs) -> None:
        if event in self.event_counter:
            counter = self.event_counter[event]
        else:
            counter = _Counter(0, 0)
    
        self.event_counter[event] = _Counter(counter[0] + 1, counter[1])

        if msg:
            Logger.debug(msg)
        return

    def failure(self, event: Event, *args, msg: str = "", **kwargs) -> None:
        if event in self.event_counter:
            counter = self.event_counter[event]
        else:
            counter = _Counter(0, 0)
    
        self.event_counter[event] = _Counter(counter[0], counter[1] + 1)

        if msg:
            Logger.error(msg)
        return

    def _summary(self) -> None:
        transformed_data: List[Tuple[Event, int, int, float]] = [
            (event, sum(counter), counter[1], counter[0]/sum(counter) * 100) for event, counter in self.event_counter.items()
            ]
        header = ["Event", "Occurrence", "Failure", "Success Rate (%)"]
        summary: str = tabulate(
            transformed_data,
            headers=header,
            # intfmt=",",
            floatfmt=".2f",
            tablefmt="grid",
        )
        Logger.info(f"PrometheusWorker {self.name} monitoring result:")
        for line in summary.split("\n"):
            Logger.info(line)
        return


class Prometheus:
    workers: ClassVar[List[PrometheusWorker]] = []

    @classmethod
    def get(cls, name: str) -> PrometheusWorker:
        worker = PrometheusWorker(name)
        cls.workers.append(worker)
        return worker

    @classmethod
    def summary(cls) -> None:
        for worker in cls.workers:
            worker._summary()

