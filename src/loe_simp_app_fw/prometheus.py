from typing import Dict, NamedTuple, TypeAlias, List, Tuple
from tabulate import tabulate
from logger import Logger

class _Counter(NamedTuple):
    success: int
    failure: int

Event: TypeAlias = str

class Prometheus:
    def __init__(self) -> None:
        self.event_counter: Dict[Event, NamedTuple] = {}
        pass

    def success(self, event: Event) -> None:
        if event in self.event_counter:
            counter = self.event_counter[event]
        else:
            counter = _Counter(0, 0)
    
        self.event_counter[event] = _Counter(counter[0] + 1, counter[1])
        return

    def fail(self, event: Event) -> None:
        if event in self.event_counter:
            counter = self.event_counter[event]
        else:
            counter = _Counter(0, 0)
    
        self.event_counter[event] = _Counter(counter[0], counter[1] + 1)
        return

    def summary(self) -> None:
        transformed_data: List[Tuple[Event, int, int, float]] = [
            (event, sum(counter), counter[1], counter[0]/sum(counter) * 100) for event, counter in self.event_counter.items()
            ]
        header = ["Event", "Occurrence", "Failure", "Success Rate (%)"]
        summary: str = tabulate(
            transformed_data,
            headers=header,
            intfmt=",",
            floatfmt=".2f",
            tablefmt="grid"
        )
        Logger.info("Prometheus monitoring result:")
        for line in summary.split("\n"):
            Logger.info(line)
        return
