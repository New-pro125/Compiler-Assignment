from __future__ import annotations
from typing import Dict, List
from collections import defaultdict


class State:
    """Represents a state in an NFA with transitions."""

    def __init__(self, id: int):
        self.id: int = id
        self.name: str = f"S{id}"
        self.transitions: Dict[str, List[State]] = defaultdict(list)

    def add_transition(self, symbol: str, next_state: State):
        self.transitions[symbol].append(next_state)
