from collections import defaultdict
from typing import Any, Callable, DefaultDict


EventHandler = Callable[[dict[str, Any]], None]


class EventBus:
    """Simple in-process pub/sub bus for decoupling system components."""

    def __init__(self) -> None:
        self._subscribers: DefaultDict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        self._subscribers[event_name].append(handler)

    def publish(self, event_name: str, payload: dict[str, Any]) -> None:
        for handler in self._subscribers[event_name]:
            handler(payload)
