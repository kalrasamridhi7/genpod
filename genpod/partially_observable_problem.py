from pddl.core import Problem
from pddl.logic import Predicate
from pddl.logic.base import Formula
from typing import Collection

class PartiallyObservableProblem(Problem):
    def __init__(self, problem: Problem, hidden_predicates: Collection[set[Formula]] = None):
        super().__init__(name=problem.name, domain=problem.domain, objects=problem.objects, init=problem.init, goal=problem.goal)
        self.hidden_predicates = hidden_predicates or []