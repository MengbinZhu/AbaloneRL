import copy
from typing import Dict

import numpy as np

from abalone import AbaloneModel
from abalone.StoneColor import StoneColor
from agent.PruningPolicy import PruningPolicy


def prob_array(x: Dict[int, float]) -> Dict[int, float]:
    return {act: prob / sum(x.values()) for act, prob in x.items()}


class Node:

    def __init__(self, parent,
                 child: dict = None,
                 prv_prob: float = 0):
        self.parent = parent
        self.child = dict() if child is None else child
        self.prv_prob = prv_prob

        self.visit_count = 0

        self._q_value = 0
        self._u_value = 0

    def expand(self, action_prob: Dict[int, float]) -> None:
        for action, prob in action_prob:
            if action not in self.child:
                self.child[action] = Node(self, prv_prob=prob)

    def select(self, cutoff: float):
        max_score, max_node = 0, None
        for node in self.child.items():
            if node[1].get_score(cutoff) > max_score:
                max_score, max_node = node[1].get_score(cutoff), node
        return max_node

    def update(self, cost: float) -> None:
        self.visit_count += 1
        self._q_value = (cost - self._q_value) / self.visit_count

    def update_backward(self, cost: float) -> None:
        if self.parent is not None:
            self.parent.update_recursive(-cost)
        self.update(cost)

    def get_score(self, cutoff: float) -> float:
        self._u_value = (cutoff * self.prv_prob * np.sqrt(self.parent.visit_count) / (1 + self.visit_count))
        return self._q_value + self._u_value


class AbaloneMCTS:

    def __init__(self,
                 abalone_agent: AbaloneModel.AbaloneAgent,
                 pruning_policy: PruningPolicy,
                 cutoff: int = 5,
                 max_depth: int = 10000):
        self.agent = copy.deepcopy(abalone_agent)
        self.agent.set_game_vector(np.array([0]))
        self.pruning_policy = pruning_policy

        self._cutoff = cutoff
        self._max_depth = max_depth

        self._root_node = Node(None)

    def get_action_prob(self, game_vector: np.ndarray) -> Dict[int, float]:
        root_node = Node(None)

        nodes = list()
        action_count = AbaloneModel.get_action_size(game_vector.size)
        for action in range(action_count):
            nodes.append(self.process_game(game_vector.copy()))

        return prob_array(nodes)

    def process_game(self, game_vector: np.ndarray):
        node = self._root_node

        while True:
            if len(node.child) == 0:
                break
            action, node = node.select(self._cutoff)
            self.agent.set_game_vector(game_vector)
            self.agent.push_stone(*self.agent.decode_action(action))

        action_prob, cost = self.pruning_policy.prediction(game_vector)
        prv_color = self.agent.get_current_color()
        winner = self.agent.next_turn()
        if winner is not None:
            node.expand(action_prob)
        else:
            cost = 1 if winner == prv_color else -1

        node.update_backward(cost)

    def forward_move(self):
        pass
