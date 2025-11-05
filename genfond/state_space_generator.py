import itertools
import logging
import random
from collections.abc import Collection
from enum import Enum
from typing import Optional

from pddl.action import Action
from pddl.core import Domain, Problem
from pddl.logic import Predicate, SensingModel
from pddl.logic.base import And, Formula, Not, OneOf, is_literal, Or
from pddl.logic.effects import When
from pddl.logic.functions import (
    Assign,
    BinaryFunction,
    Decrease,
    Divide,
)
from pddl.logic.functions import EqualTo as FunctionEqualTo
from pddl.logic.functions import (
    FunctionExpression,
    GreaterEqualThan,
    GreaterThan,
    Increase,
    LesserEqualThan,
    LesserThan,
    Minus,
    NumericFunction,
    NumericValue,
    Plus,
    ScaleDown,
    ScaleUp,
    Times,
)
from pddl.logic.predicates import EqualTo

from .ground import ground, ground_domain_predicates, ground_sensing_models

log = logging.getLogger("genfond.state_space_generator")

State = frozenset[Formula]


def state_to_string(state: State) -> str:
    state_str = []
    for p in state:
        if isinstance(p, Predicate):
            state_str.append(f'{p.name}({",".join([str(p) for p in p.terms])})')
        elif isinstance(p, FunctionEqualTo):
            state_str.append(f"{p.operands[0]}={p.operands[1]}")
        else:
            raise ValueError("Unknown state type: {}".format(type(p)))
    return ",".join(sorted(state_str))


def eval_function_term(term: FunctionExpression, state: State) -> float | int:
    if isinstance(term, NumericValue):
        return term.value
    elif isinstance(term, NumericFunction):
        for f in state:
            if not isinstance(f, FunctionEqualTo):
                continue
            if f.operands[0] == term:
                return f.operands[1].value
        # TODO: check if this is correct
        # DZC: This is probably be fine. If a numeric fluent does not appear in the initial
        # state of the PDDL, its value is assumed to be 0.
        return 0
        # raise ValueError(f'Function {term} not found in state {state_to_string(state)}')
    elif isinstance(term, Plus):
        return eval_function_term(term.operands[0], state) + eval_function_term(term.operands[1], state)
    else:
        raise ValueError("Unknown term type: {}".format(type(term)))


def check_formula(state: State, formula: Formula) -> bool:
    if isinstance(formula, And):
        return all(check_formula(state, subformula) for subformula in formula.operands)
    elif isinstance(formula, Not):
        return not check_formula(state, formula.argument)
    elif isinstance(formula, Predicate):
        if "pos_EqualTo" in formula.name:
            return formula.terms[0] == formula.terms[1]
        elif "neg_EqualTo" in formula.name:
            return formula.terms[0] != formula.terms[1]
        return formula in state
    elif isinstance(formula, EqualTo):
        return formula.left == formula.right
    elif isinstance(formula, LesserThan):
        return eval_function_term(formula.operands[0], state) < eval_function_term(formula.operands[1], state)
    elif isinstance(formula, LesserEqualThan):
        return eval_function_term(formula.operands[0], state) <= eval_function_term(formula.operands[1], state)
    elif isinstance(formula, GreaterThan):
        return eval_function_term(formula.operands[0], state) > eval_function_term(formula.operands[1], state)
    elif isinstance(formula, GreaterEqualThan):
        return eval_function_term(formula.operands[0], state) >= eval_function_term(formula.operands[1], state)
    elif isinstance(formula, FunctionEqualTo):
        return eval_function_term(formula.operands[0], state) == eval_function_term(formula.operands[1], state)
    else:
        raise ValueError("Unknown formula type: {}".format(type(formula)))

def is_dnf(condition: Formula) -> bool:
    if isinstance(condition, Or):
        return all(isinstance(c, And) and all(is_literal(l) for l in c.operands) for c in condition.operands)
    elif isinstance(condition, And):
        return all(is_literal(l) for l in condition.operands)
    elif is_literal(condition):
        return True
    else:
        return False

def observed_literal_to_action_name(literal: Predicate) -> str:
    """Convert a literal to a valid action name that matches the regex [A-Za-z][-_A-Za-z0-9]*"""
    # Convert the entire literal to string, remove parentheses, and replace spaces with underscores
    action_name = str(literal).replace('(', '').replace(')', '').replace(' ', '_')
    return action_name    

def convert_sensing_model_to_actions(grounded_sensing_models: list[SensingModel]) -> list[Action]:
    sensing_actions = []
    for model in grounded_sensing_models:
        inverse_model = next((m for m in grounded_sensing_models if m.literal == inverse_literal(model.literal)), None)
        if not inverse_model:
            raise ValueError("No inverse model found for sensing model {}".format(model.literal))
        if not isinstance(model.condition, Or) and is_dnf(model.condition):
            action_effect = (And(model.condition, model.literal))
        else:
            action_effect = And(get_effects_from_dnf(inverse_model.condition, model.literal), model.literal)
        sensing_action = Action(
            name=observed_literal_to_action_name(model.literal),
            parameters=model.parameters,
            precondition=And(model.precondition, Not(model.literal), Not(inverse_model.literal)),
            effect=action_effect
        )
        #print(sensing_action)
        sensing_actions.append(sensing_action)
    return sensing_actions

def get_effects_from_dnf(condition: Formula, literal: Formula) -> Formula:
    effect_list = []
    if not is_dnf(condition):
        #condition = convert_to_dnf(condition)
        raise ValueError("Sensing model condition is not in DNF.")
    if isinstance(condition, Or):
        for conjunct in condition.operands:
            for literal in conjunct.operands:
                rest_conjuncts = set(conjunct.operands) - {literal}
                effect_list.append(When(
                    And(*rest_conjuncts, Not(literal)),
                    inverse_literal(literal)
                ))
    elif isinstance(condition, And):
        for literal in condition.operands:
            rest_conjuncts = set(condition.operands) - {literal}
            effect_list.append(When(
                And(*rest_conjuncts, Not(literal)),
                inverse_literal(literal)
            ))
    elif is_literal(condition):
        effect_list.append(When(
            Not(condition),
            inverse_literal(condition)
        ))
    return And(*effect_list)

def apply_action_effect(state: State, action: Action, domain: Domain, problem: Problem) -> State:
    #print(f"Applying action effect for action {action.name} with effect {action.effect}")
    return apply_effect(state, action.effect, domain, problem)

def inverse_literal(literal: Predicate) -> Predicate:
    if literal.name.startswith("K_pos_"):
        return Predicate(f"K_neg_{literal.name[6:]}", *(literal.terms))
    elif literal.name.startswith("K_neg_"):
        return Predicate(f"K_pos_{literal.name[6:]}", *(literal.terms))
    else:
        raise ValueError("Literal must be a K_pos_ or K_neg_ literal.")

def complement_literal(literal: Predicate, domain: Domain, problem: Problem, state: State) -> set[Predicate]:
    ground_predicates = ground_domain_predicates(domain, problem)
    if any(literal.name == model.literal.name for model in domain.sensing_models):
        return {literal}
    if literal.name.startswith("K_pos_"):
        complement_name = f"K_neg_{literal.name[6:]}"
        return {p for p in ground_predicates if p.name == complement_name and p.terms != literal.terms}
    elif literal.name.startswith("K_neg_"):
        x_in_state = {p for p in state if p.name == literal.name}
        x_in_domain = {p for p in ground_predicates if p.name == literal.name}
        if len(x_in_domain) - len(x_in_state | {literal}) == 1:
            o_x = next(iter(x_in_domain - x_in_state))
            return {inverse_literal(o_x), literal}
        else:
            return {literal}

def apply_effect(state: State, effect: Formula, domain: Domain, problem: Problem) -> State:
    assert all(isinstance(f, (Predicate, FunctionEqualTo)) for f in state)
    if isinstance(effect, And):
        for sub_effect in effect.operands:
            state = apply_effect(state, sub_effect, domain, problem)
        return state
    elif isinstance(effect, Predicate):
        new_state = state
        print(f"Applying effect {effect}")
        effect_complements = complement_literal(effect, domain, problem, state)
        all_effects = {effect} | effect_complements
        for effect in all_effects:
            if inverse_literal(effect) in state:
                new_state = set(f for f in state if f != inverse_literal(effect))
        return frozenset(new_state | all_effects)
    elif isinstance(effect, Not):
        print(f"Applying effect {effect}")
        return frozenset(f for f in state if f != effect.argument)
    elif isinstance(effect, When):
        if check_formula(state, effect.condition):
            print(f"Applying effect {effect.effect} due to When condition {effect.condition}")
            return apply_effect(state, effect.effect, domain, problem)
        else:
            return state
    elif isinstance(effect, BinaryFunction):
        if isinstance(effect.operands[0], NumericFunction):
            fct = effect.operands[0]
            change = eval_function_term(effect.operands[1], state)
        else:
            # DZC: What is this else case?
            fct = effect.operands[1]
            change = effect.operands[0]
        assert isinstance(fct, NumericFunction)
        # DZC: remove this assert by evaluating change = eval_function_term(...)
        # assert isinstance(change, NumericValue)
        current_evals = [f for f in state if isinstance(f, FunctionEqualTo) and f.operands[0] == fct]
        if not current_evals:
            current_eval = FunctionEqualTo(fct, NumericValue(0))
        else:
            assert len(current_evals) == 1
            current_eval = current_evals[0]
        current_value = current_eval.operands[1].value
        if isinstance(effect, Assign):
            new_value = change
        elif isinstance(effect, Increase):
            new_value = current_value + change
        elif isinstance(effect, Decrease):
            new_value = current_value - change
        elif isinstance(effect, (Plus, Minus, Times, Divide, ScaleUp, ScaleDown)):
            raise NotImplementedError()
        else:
            raise ValueError("Unknown effect type: {}".format(type(effect)))
        # log.debug(f'Change {fct} from {current_value} to {new_value}')
        return frozenset([f for f in state if f != current_eval] + [FunctionEqualTo(fct, NumericValue(new_value))])
    else:
        raise ValueError("Unknown effect type: {}".format(type(effect)))

def get_observable_variables(domain: Domain) -> list[str]:
    observable_variables = []
    for model in domain.sensing_models:
        variable = model.literal.name[6:]  # Remove 'K_pos_' prefix
        if variable not in observable_variables:
            observable_variables.append(variable)
    return observable_variables

class Alive(Enum):
    ALIVE = 0
    DEAD = 1
    UNKNOWN = 2
    PRUNED = 3
    NUM_PRUNED = 4


class StateSpaceNode:

    def __init__(self, state: State, id: int):
        self.state = state
        self.id = id
        self.children: dict[Action, set[StateSpaceNode]] = dict()
        self.alive = Alive.UNKNOWN
        self.goal = False
        self.parents: set[StateSpaceNode] = set()

    def __str__(self) -> str:
        return state_to_string(self.state)

    def __repr__(self) -> str:
        return repr(self.state)

    def add_child(self, action: Action, node: "StateSpaceNode") -> None:
        self.children.setdefault(action, set()).add(node)


def get_num_vals(state: State) -> set[int]:
    return {f.operands[1].value for f in state if isinstance(f, FunctionEqualTo)}


class StateSpaceGraph:

    def __init__(
        self,
        domain: Domain,
        problem: Problem,
        prune: bool = True,
        selected_states: Optional[set[State]] = None,
        max_num_val: Optional[int] = None,
    ):
        self.domain = domain
        self.problem = problem

        grounded_actions = ground(domain, problem)
        grounded_sensing_models = ground_sensing_models(domain, problem)
        sensing_actions = convert_sensing_model_to_actions(grounded_sensing_models)
        observable_variables = get_observable_variables(domain)

        self.next_id = 0
        queue = []
        self.nodes: dict[State, StateSpaceNode] = dict()
        if selected_states:
            for state in selected_states:
                node = StateSpaceNode(state, self.next_id)
                self.next_id += 1
                self.nodes[state] = node
                queue.append(node)
        else:
            root_state = problem.init
            #apply sensing effects to root state
            for fact in problem.init:
                for sensing_action in sensing_actions:
                    if observed_literal_to_action_name(fact) == sensing_action.name:
                        root_state = apply_action_effect(root_state, sensing_action, domain, problem)
            self.root = StateSpaceNode(root_state, 0)
            self.next_id = 1
            self.nodes = {root_state: self.root}
            queue = [self.root]
            print(f"Initial root state: {state_to_string(root_state)}")
        while queue:
        #for _ in range(10):  # DZC: temporary hack to only do one iteration for testing
            print(f"Queue size: {len(queue)}")
            node = queue.pop(0)
            state = node.state
            #print(f"Expanding node {node.id} with state {state_to_string(state)}")
            if check_formula(state, problem.goal):
                node.alive = Alive.ALIVE
                node.goal = True
            if all([p in state or inverse_literal(p) in state for p in ground_domain_predicates(domain, problem)]):
                print("All predicates known in state")
            for j, action in enumerate(grounded_actions):
                if not check_formula(state, action.precondition):
                    continue
                s_a = apply_action_effect(state, action, domain, problem)
                print(f"Applied action {action.name} {action.parameters}")
                applicable_sensing_actions = [sensing_action for sensing_action in sensing_actions if check_formula(s_a, sensing_action.precondition)]
                observable_variables_in_state = [var for var in observable_variables if any([var in action.name for action in applicable_sensing_actions])]
                observation_combinations = list(itertools.product([1, 0], repeat=len(observable_variables_in_state)))
                for combo in observation_combinations:
                    s_a_o = s_a
                    for i, val in enumerate(combo):
                        sensing_action = None
                        var = observable_variables_in_state[i]
                        if val == 1:
                            action_name_start = f'K_pos_{var}'
                        else:
                            action_name_start = f'K_neg_{var}'
                        sensing_action = next((sa for sa in applicable_sensing_actions if sa.name.startswith(action_name_start)), None)
                        if not sensing_action:
                            continue
                        print(f"sensing action {sensing_action.name} on state")
                        s_a_o = apply_action_effect(s_a_o, sensing_action, domain, problem)
                    new_node = self.add_node(s_a_o, state, action)
                    if new_node:
                        #print("created new node")
                        if max_num_val and any(v > max_num_val for v in get_num_vals(s_a_o)):
                            new_node.alive = Alive.NUM_PRUNED
                        elif selected_states and s_a_o not in selected_states:
                                new_node.alive = Alive.PRUNED
                        else:
                            print(f"Adding new node with state {state_to_string(s_a_o)} to queue")
                            queue.append(new_node)
                
            print(f"len(queue): {len(queue)}")
            #break
        compute_alive(self.nodes.values())
        if prune:
            self.prune_nodes()
        assert all(node.alive != Alive.UNKNOWN for node in self.nodes.values())
        # assert self.root.alive == Alive.ALIVE, 'Problem {} is unsolvable'.format(problem.name)

    def add_node(self, state: State, parent_state: State, action: Action) -> Optional[StateSpaceNode]:
        parent = self.nodes[parent_state]
        try:
            node = self.nodes[state]
            #print("this state already exists")
            new = False
        except KeyError:
            node = StateSpaceNode(state, self.next_id)
            self.next_id += 1
            self.nodes[state] = node
            new = True

        parent.add_child(action, node)
        node.parents.add(parent)
        if new:
            return node
        else:
            return None

    def prune_nodes(self) -> None:
        pruned_dead = []
        pruned_selected: list[State] = []
        for state, node in self.nodes.items():
            if node.alive == Alive.DEAD and all([parent.alive == Alive.DEAD for parent in node.parents]):
                pruned_dead.append(state)
        before = len(self.nodes)
        for state in pruned_dead + pruned_selected:
            del self.nodes[state]
        for node in self.nodes.values():
            for action, children in node.children.items():
                node.children[action] = {child for child in children if child.state in self.nodes}
        #log.info(f"Pruned {len(pruned_dead)} dead " f"out of {before} states in {self.problem.name}")
        print(f"Pruned {len(pruned_dead)} dead " f"out of {before} states in {self.problem.name}")


def generate_state_space(domain: Domain, problem: Problem, selected_states: Optional[set[State]] = None):
    return StateSpaceGraph(domain, problem, selected_states=selected_states)


def can_reach(node: StateSpaceNode, goal_nodes: Collection[StateSpaceNode]) -> bool:
    seen = set()
    stack = [node]
    while stack:
        current_node = stack.pop()
        if current_node in goal_nodes:
            return True
        if current_node.alive == Alive.DEAD:
            continue
        if current_node.alive == Alive.ALIVE:
            return True
        if current_node in seen:
            continue
        seen.add(current_node)
        for children in current_node.children.values():
            if all(child.alive != Alive.DEAD for child in children):
                stack.extend(children)
    return False


def find_nodes_leading_to_dead(nodes: Collection[StateSpaceNode]) -> bool:
    queue = [node for node in nodes if node.alive == Alive.UNKNOWN]
    changed = False
    while queue:
        node = queue.pop()
        if all(any(child.alive == Alive.DEAD for child in children) for children in node.children.values()):
            node.alive = Alive.DEAD
            changed = True
            for parent in node.parents:
                if parent.alive == Alive.UNKNOWN:
                    queue.append(parent)
    return changed


def find_node_not_reaching_goal(nodes: Collection[StateSpaceNode]) -> bool:
    queue = [node for node in nodes if node.alive == Alive.UNKNOWN]
    goal_nodes = [node for node in nodes if node.alive in [Alive.ALIVE, Alive.PRUNED]]
    changed = False
    while queue:
        node = queue.pop()
        if not can_reach(node, goal_nodes):
            node.alive = Alive.DEAD
            changed = True
            for parent in node.parents:
                if parent.alive == Alive.UNKNOWN:
                    queue.append(parent)
    return changed


def compute_alive(nodes: Collection[StateSpaceNode]) -> None:
    changed = True
    while changed:
        changed = find_nodes_leading_to_dead(nodes)
        changed = find_node_not_reaching_goal(nodes) or changed
    for node in nodes:
        if node.alive == Alive.UNKNOWN:
            node.alive = Alive.ALIVE


def random_walk(domain: Domain, problem: Problem, initial_states: set[State], max_steps: int = 100):
    states = list(initial_states)
    grounded_actions = ground(domain, problem)
    while True:
        state = random.choice(states)
        for _ in range(max_steps):
            if check_formula(state, problem.goal):
                return states
            applicable_actions = [action for action in grounded_actions if check_formula(state, action.precondition)]
            if not applicable_actions:
                break
            action = random.choice(applicable_actions)
            succ = random.choice(list(apply_action_effect(state, action)))
            states.append(succ)
            state = succ
