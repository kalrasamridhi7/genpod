from pddl.core import Problem
from pddl.logic import Predicate
from typing import Collection

class PartiallyObservableProblem(Problem):
    def __init__(self, problem: Problem, hidden_predicates: Collection[set[Predicate]] = None):
        super().__init__(name=problem.name, domain=problem.domain, objects=problem.objects, init=problem.init, goal=problem.goal)
        self.hidden_predicates = hidden_predicates or []