from __future__ import annotations
import networkx as nx
from networkx.drawing.nx_agraph import to_agraph
from PIL import Image
from typing import Union

from dfa.DFA import DFA
from .NFA import NFA


class NFAVisualizer:
    """Generates NFA graph images."""

    @staticmethod
    def save_image(nfa: Union[NFA, DFA], filepath: str):
        data = nfa.to_dict()
        G = nx.MultiDiGraph()
        for state, trans in data.items():
            if state == "startingState":
                continue
            shape = "doublecircle" if trans["isTerminatingState"] else "circle"
            G.add_node(state, shape=shape)
            for symbol, next_states in trans.items():
                if symbol == "isTerminatingState":
                    continue
                for nxt in next_states:
                    G.add_edge(state, nxt, label=symbol)
        A = to_agraph(G)
        A.add_node("st", shape="none", label="")
        A.add_edge("st", data["startingState"])
        A.graph_attr.update(rankdir="LR")
        A.layout(prog="dot")
        A.draw(filepath)
        return Image.open(filepath)
