from __future__ import annotations
from typing import List
from .State import State
from regex.RegexTokenizer import RegexTokenizer
from .NFA import NFA


class NFABuilder:
    """Builds NFA from regex using Thompson's construction."""

    def __init__(self):
        self.state_counter = 0

    def create_state(self) -> State:
        state = State(self.state_counter)
        self.state_counter += 1
        return state

    def from_regex(self, regex: str) -> NFA:
        postfix = RegexTokenizer.to_postfix(regex)
        stack: List[NFA] = []
        for token in postfix:
            if token in "_|":
                nfa2, nfa1 = stack.pop(), stack.pop()
                stack.append(
                    self.concat(nfa1, nfa2)
                    if token == "_"
                    else self.alternate(nfa1, nfa2)
                )
            elif token in "*+?":
                nfa = stack.pop()
                if token == "*":
                    stack.append(self.zero_or_more(nfa))
                elif token == "+":
                    stack.append(self.one_or_more(nfa))
                elif token == "?":
                    stack.append(self.zero_or_one(nfa))
            else:
                stack.append(self.literal(token))
        return stack[0]

    # --- Thompson Operators ---
    def literal(self, char: str) -> NFA:
        start = self.create_state()
        end = self.create_state()
        start.add_transition(char, end)
        return NFA(start, end)

    def concat(self, nfa1: NFA, nfa2: NFA) -> NFA:
        nfa1.end.add_transition("ε", nfa2.start)
        return NFA(nfa1.start, nfa2.end)

    def alternate(self, nfa1: NFA, nfa2: NFA) -> NFA:
        start, end = self.create_state(), self.create_state()
        start.add_transition("ε", nfa1.start)
        start.add_transition("ε", nfa2.start)
        nfa1.end.add_transition("ε", end)
        nfa2.end.add_transition("ε", end)
        return NFA(start, end)

    def zero_or_more(self, nfa: NFA) -> NFA:
        start, end = self.create_state(), self.create_state()
        start.add_transition("ε", nfa.start)
        start.add_transition("ε", end)
        nfa.end.add_transition("ε", nfa.start)
        nfa.end.add_transition("ε", end)
        return NFA(start, end)

    def one_or_more(self, nfa: NFA) -> NFA:
        start, end = self.create_state(), self.create_state()
        start.add_transition("ε", nfa.start)
        nfa.end.add_transition("ε", nfa.start)
        nfa.end.add_transition("ε", end)
        return NFA(start, end)

    def zero_or_one(self, nfa: NFA) -> NFA:
        start, end = self.create_state(), self.create_state()
        start.add_transition("ε", nfa.start)
        start.add_transition("ε", end)
        nfa.end.add_transition("ε", end)
        return NFA(start, end)
