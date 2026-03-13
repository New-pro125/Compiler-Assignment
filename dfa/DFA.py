from collections import defaultdict, deque

from nfa.State import State
from typing import Dict, FrozenSet, Iterable, List, Set, Tuple
from nfa.NFA import NFA
import json


class DFA:

    def __init__(self, start: State, end) -> None:
        self._start = start
        self._end = end

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
            if a in state.transitions:
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
        dfa_states: Set[FrozenSet[State]],
        dfa_transitions: Dict[Tuple[FrozenSet[State], str], FrozenSet[State]],
        nfa_accept_state: State,
        symbols: List[str],
    ) -> Tuple[List[Set[FrozenSet[State]]], Set[FrozenSet[State]]]:
        accepting_states = set()
        for state in dfa_states:
            if nfa_accept_state in state:
                accepting_states.add(state)
        non_accepting_states = dfa_states - accepting_states
        P = []
        W = []
        if accepting_states:
            P.append(accepting_states)
            W.append(accepting_states)
        if non_accepting_states:
            P.append(non_accepting_states)
            W.append(non_accepting_states)
        inverse_transitions = defaultdict(lambda: defaultdict(list))
        for (src, c), tgt in dfa_transitions.items():
            inverse_transitions[tgt][c].append(src)
        while W:
            A = W.pop()
            for c in symbols:
                X = set()
                for target in A:
                    if target in inverse_transitions:
                        X.update(inverse_transitions[target].get(c, []))
                splits = []
                for i, Y in enumerate(P):
                    Y_int = Y & X
                    Y_diff = Y - X
                    if Y_int and Y_diff:
                        splits.append((i, Y, Y_int, Y_diff))
                for i, Y, Y_int, Y_diff in splits:
                    P[i] = Y_int
                    P.append(Y_diff)
                    if Y in W:
                        W.remove(Y)
                        W.append(Y_int)
                        W.append(Y_diff)
                    else:
                        if len(Y_int) <= len(Y_diff):
                            W.append(Y_int)
                        else:
                            W.append(Y_diff)
        return P, accepting_states

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
        min_accepting_states = set()
        for old_state in accepting_groups:
            min_accepting_states.add(old_to_new_state_map[old_state])
        for group in P:
            representative = next(iter(group))
            new_s = old_to_new_state_map[representative]
            for symbol in symbols:
                target = dfa_transitions.get((representative, symbol))
                if target is not None and target in old_to_new_state_map:
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
        visited.add(self._start.name)
        while queue:
            curr = queue.popleft()
            is_accepting = (
                curr in self._end if isinstance(self._end, set) else curr == self._end
            )
            entry = {"isTerminatingState": is_accepting}
            for symbol, next_states in curr.transitions.items():
                entry[symbol] = [s.name for s in next_states]
                for s in next_states:
                    if s.name not in visited:
                        visited.add(s.name)
                        queue.append(s)
            result[curr.name] = entry
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
