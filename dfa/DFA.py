from collections import defaultdict, deque

from nfa.State import State
from typing import Dict, FrozenSet, Iterable, List, Set, Tuple
from nfa.NFA import NFA
import json


class DFA:

    def __init__(self, start: State, end) -> None:
        self._start = start
        self._end = end  # Either a single State (NFA) or a set of States (minimized DFA)

    @staticmethod
    def epsilon_closure(states: Iterable[State]) -> FrozenSet[State]:
        closure = set(states)
        stack = list(states)
        while stack:
            curr = stack.pop()
            for eps_state in curr.transitions.get("ε", []):
                if eps_state not in closure:
                    closure.add(eps_state)
                    stack.append(eps_state)
        return frozenset(closure)

    @staticmethod
    def move(states: Iterable[State], a: str) -> FrozenSet[State]:
        reachable_states = set()
        for state in states:
            if state.transitions.get(a) is not None:
                reachable_states.update(state.transitions[a])
        return frozenset(reachable_states)

    @staticmethod
    def subset_construction(
        nfa: NFA,
    ) -> Tuple[
        Set[FrozenSet[State]],
        Dict[Tuple[FrozenSet[State], str], FrozenSet[State]],
        FrozenSet[State],
        List[str],
        State,
    ]:
        symbols = nfa.nfa_symbols()
        dfa_start_state = DFA.epsilon_closure([nfa.start])
        dfa_transitions: Dict[Tuple[FrozenSet[State], str], FrozenSet[State]] = {}
        queue = deque([dfa_start_state])
        visited = {dfa_start_state}
        while queue:
            curr = queue.popleft()
            for symbol in symbols:
                target_nfa_states = DFA.move(curr, symbol)
                if not target_nfa_states:
                    continue
                next_state = DFA.epsilon_closure(target_nfa_states)
                if not next_state:
                    continue
                dfa_transitions[(curr, symbol)] = next_state

                if next_state not in visited:
                    visited.add(next_state)
                    queue.append(next_state)
        return visited, dfa_transitions, dfa_start_state, symbols, nfa.end

    @staticmethod
    def hopcroft(
        dfa_states: set[FrozenSet[State]],
        dfa_transitions: Dict[Tuple[FrozenSet[State], str], FrozenSet[State]],
        nfa_accept_state: State,
        symbols: list[str],
    ) -> Tuple[List[Set[FrozenSet[State]]], Set[FrozenSet[State]]]:
        accepting_groups = set()
        non_accepting_groups = set()
        for state in dfa_states:
            if nfa_accept_state in state:
                accepting_groups.add(state)
            else:
                non_accepting_groups.add(state)
        P = []
        if accepting_groups:
            P.append(accepting_groups)
        if non_accepting_groups:
            P.append(non_accepting_groups)
        while True:
            state_to_group_idx = {}
            for i, group in enumerate(P):
                for state in group:
                    state_to_group_idx[state] = i
            P_new = []
            for group in P:
                subgroups = defaultdict(set)
                for state in group:
                    signature = []
                    for symbol in symbols:
                        target = dfa_transitions.get((state, symbol))
                        if target is not None:
                            signature.append(state_to_group_idx[target])
                        else:
                            signature.append(-1)
                    subgroups[tuple(signature)].add(state)
                P_new.extend(subgroups.values())
            if len(P) == len(P_new):
                break
            P = P_new
        return P, accepting_groups

    @staticmethod
    def build_dfa_from_groupings(
        P: List[Set[FrozenSet[State]]],
        accepting_groups: Set[FrozenSet[State]],
        dfa_transitions: Dict[Tuple[FrozenSet[State], str], FrozenSet[State]],
        start_dfa_state: FrozenSet[State],
        symbols: List[str],
    ) -> "DFA":
        old_to_new_state_map = {}
        for i, group in enumerate(P):
            new_state = State(id=i)
            for old_state in group:
                old_to_new_state_map[old_state] = new_state
        min_start_state = old_to_new_state_map[start_dfa_state]
        min_accepting_states: Set[State] = set()
        for old_state in accepting_groups:
            min_accepting_states.add(old_to_new_state_map[old_state])
        for group in P:
            representative = next(iter(group))
            new_s = old_to_new_state_map[representative]
            for symbol in symbols:
                target = dfa_transitions.get((representative, symbol))
                if target is not None:
                    new_t = old_to_new_state_map[target]
                    new_s.add_transition(symbol, new_t)
        return DFA(min_start_state, min_accepting_states)

    @staticmethod
    def build_minimized_dfa(nfa: NFA) -> "DFA":
        dfa_states, dfa_transitions, start_dfa_state, symbols, nfa_accept_state = (
            DFA.subset_construction(nfa)
        )
        P, accepting_groups = DFA.hopcroft(
            dfa_states, dfa_transitions, nfa_accept_state, symbols
        )
        return DFA.build_dfa_from_groupings(
            P, accepting_groups, dfa_transitions, start_dfa_state, symbols
        )

    def to_dict(self) -> dict:
        result = {"startingState": self._start.name}
        visited, queue = set(), deque([self._start])
        while queue:
            curr = queue.popleft()
            if curr.name in visited:
                continue
            visited.add(curr.name)
            is_accepting = (
                curr in self._end
                if isinstance(self._end, set)
                else curr == self._end
            )
            entry = {"isTerminatingState": is_accepting}
            for symbol, next_states in curr.transitions.items():
                entry[symbol] = [s.name for s in next_states]
                for s in next_states:
                    if s.name not in visited:
                        queue.append(s)
            result[curr.name] = entry
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
