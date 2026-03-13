from __future__ import annotations
from collections import deque
import json

from .State import State


class NFA:
    """Encapsulates NFA start/end states and conversion to JSON."""

    def __init__(self, start: State, end: State):
        self.start = start
        self.end = end

    def nfa_symbols(self) -> list[str]:
        visited = set()
        queue = deque([self.start])
        symbols = set()

        while queue:
            curr = queue.popleft()
            if curr.id in visited:
                continue

            visited.add(curr.id)
            symbols.update(curr.transitions.keys())
            for next_states in curr.transitions.values():
                for s in next_states:
                    if s.id not in visited:
                        queue.append(s)
        if "ε" in symbols:
            symbols.remove("ε")  # Not needed for subset construction

        return list(symbols)

    def to_dict(self) -> dict:
        result = {"startingState": self.start.name}
        visited, queue = set(), deque([self.start])
        while queue:
            curr = queue.popleft()
            if curr.name in visited:
                continue
            visited.add(curr.name)
            entry = {"isTerminatingState": curr == self.end}
            for symbol, next_states in curr.transitions.items():
                entry[symbol] = [s.name for s in next_states]
                for s in next_states:
                    if s.name not in visited:
                        queue.append(s)
            result[curr.name] = entry
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
