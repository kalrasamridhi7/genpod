import itertools
import logging
import queue
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

from genfond.partially_observable_problem import PartiallyObservableProblem

from .ground import Grounding, ground, inverse_literal

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
    elif isinstance(formula, Or):
        return any(check_formula(state, subformula) for subformula in formula.operands)
    elif isinstance(formula, Not):
        ##if Kx or K~x is in state then we know something about x.  
        #if isinstance(formula.argument, Predicate):
        #    #log.debug(f"Checking NOT formula: {formula.argument} against state")
        #    literal_name = formula.argument.name[6:] if formula.argument.name.startswith("K_pos_") or formula.argument.name.startswith("K_neg_") else None
        #    for p in state:
        #        if isinstance(p, Predicate) and p.name[6:] == literal_name and p.terms == formula.argument.terms:
        #            #log.debug("returning False")
        #            return False  
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
        return all((isinstance(c, And) and all(is_literal(l) for l in c.operands)) or is_literal(c) for c in condition.operands)
    elif isinstance(condition, And):
        return all(is_literal(l) for l in condition.operands)
    elif is_literal(condition):
        return True
    else:
        return False

def is_cnf(condition: Formula) -> bool:
    """Check if a formula is in CNF (Conjunctive Normal Form)."""
    if isinstance(condition, And):
        return all(isinstance(c, Or) and all(is_literal(l) for l in c.operands) for c in condition.operands)
    elif isinstance(condition, Or):
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

def convert_sensing_model_to_actions(grounded_sensing_models: list[SensingModel],
                                     grounded_obs_variables: dict[Predicate, set[Predicate]]) -> list[Action]:
    sensing_actions = []
    for model in grounded_sensing_models:
        inverse_models = []
        for key, predicate_set in grounded_obs_variables.items():
            if model.literal in predicate_set or inverse_literal(model.literal) in predicate_set:
                if len(predicate_set) == 1:         #binary variable
                    inverse_models.extend([m for m in grounded_sensing_models if m.literal == inverse_literal(model.literal)])
                else:
                    inverse_models.extend([m for m in grounded_sensing_models if m.literal in predicate_set - {model.literal}])
        if not inverse_models:
            raise ValueError("No inverse model found for sensing model {}".format(model.literal))
        #action_effect = And(*[get_effects_from_dnf(inverse_model.condition, model.literal) for inverse_model in inverse_models], model.literal)
        #test: do not add observation token to sensing action effect to maintain markovian states.
        action_effect = And(*[get_effects_from_dnf(inverse_model.condition, model.literal) for inverse_model in inverse_models])
        sensing_action = Action(
            name=observed_literal_to_action_name(model.literal),
            parameters=model.parameters,
            #precondition=And(model.precondition, Not(model.literal), *[Not(m.literal) for m in inverse_models]),
            precondition=model.precondition,
            effect=action_effect
        )
        sensing_actions.append(sensing_action)
        #log.debug(f'sensing action: {sensing_action}')
    return sensing_actions

def cnf_to_dnf(formula: Formula) -> Formula:
    """
    Convert a formula in CNF (Conjunctive Normal Form) to DNF (Disjunctive Normal Form).
    CNF: (A ∨ B) ∧ (C ∨ D) 
    DNF: (A ∧ C) ∨ (A ∧ D) ∨ (B ∧ C) ∨ (B ∧ D)
    """
    if not isinstance(formula, And):
        return formula  # Already in DNF or atomic

    # Extract all conjuncts (clauses)
    conjuncts = list(formula.operands)

    # Normalize clauses: convert each to a list of literals
    clauses = []
    for conjunct in conjuncts:
        if isinstance(conjunct, Or):
            clauses.append(list(conjunct.operands))
        else:
            clauses.append([conjunct])

    # Sort clauses by size (smallest first) to potentially reduce intermediate size
    clauses.sort(key=len)

    # Iteratively apply distributive law instead of generating all combinations at once
    # This can help with early termination and memory efficiency
    result = clauses[0]

    for clause in clauses[1:]:
        new_terms = []
        for term in result:
            for literal in clause:
                # Combine existing term with new literal
                if isinstance(term, And):
                    new_terms.append(And(*term.operands, literal))
                else:
                    new_terms.append(And(term, literal))
        result = new_terms

    # Convert result to proper DNF formula
    if len(result) == 1:
        return result[0]
    else:
        return Or(*result)

def cnf_to_dnf_iterative(formula: Formula) -> Formula:
    """
    Convert CNF to DNF iteratively (more memory efficient than Cartesian product).
    """
    if not isinstance(formula, And):
        return formula
    
    conjuncts = list(formula.operands)
    
    # Normalize clauses
    clauses = []
    for conjunct in conjuncts:
        if isinstance(conjunct, Or):
            clauses.append(list(conjunct.operands))
        else:
            clauses.append([conjunct])
    
    if not clauses:
        return And()
    
    # Start with the first clause
    result_terms = [[literal] for literal in clauses[0]]
    
    # Iteratively distribute with remaining clauses
    for clause in clauses[1:]:
        new_terms = []
        for existing_term in result_terms:
            for literal in clause:
                # Combine existing term with new literal
                new_terms.append(existing_term + [literal])
        
        result_terms = new_terms
        
        # Optional: Early termination if too many terms
        if len(result_terms) > 10000:
            log.warning(f"DNF conversion creating {len(result_terms)} terms - aborting")
            #raise ValueError("CNF to DNF conversion would create too many terms")
    
    # Build final DNF formula
    dnf_terms = []
    for term in result_terms:
        if len(term) == 1:
            dnf_terms.append(term[0])
        else:
            dnf_terms.append(And(*term))
    
    if len(dnf_terms) == 1:
        return dnf_terms[0]
    else:
        return Or(*dnf_terms)

def get_effects_from_dnf(condition: Formula, literal: Formula) -> Formula:
    effect_list = []
    if not is_dnf(condition):
        if is_cnf(condition):
            condition = cnf_to_dnf_iterative(condition)
        else:
            raise ValueError("Condition is not in CNF or DNF.")
    if isinstance(condition, Or):
        for conjunct in condition.operands:
            if is_literal(conjunct):
                effect_list.append(When(Not(conjunct), inverse_literal(conjunct)))
            elif isinstance(conjunct, And):
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

def apply_action_effect(state: State, action: Action, grounding: Grounding) -> State:
    log.debug(f"Applying action effect for action {action.name}")
    return apply_effect(state, action.effect, grounding)

def apply_action_effect_with_observations(state: State, action: Action, grounding: Grounding, sensing_actions: list[Action], true_observations: set[Predicate]=None) -> tuple[set[State], set[Predicate]] | set[State]:
    if action:
        s_a = apply_action_effect(state, action, grounding)
        if true_observations is not None:
           update_true_obs = get_updated_true_observation(true_observations, state, action, grounding)
    new_states = set()
    applicable_sensing_actions = []
    for sensing_action in sensing_actions:
        model = next((m for m in grounding.grounded_sensing_models if observed_literal_to_action_name(m.literal) == sensing_action.name), None)
        inverse_models = []
        for key, predicate_set in grounding.grounded_observable_variables.items():
            if model.literal in predicate_set or inverse_literal(model.literal) in predicate_set:
                if len(predicate_set) == 1:         #binary variable
                    inverse_models.extend([m for m in grounding.grounded_sensing_models if m.literal == inverse_literal(model.literal)])
                else:
                    inverse_models.extend([m for m in grounding.grounded_sensing_models if m.literal in predicate_set - {model.literal}])
        if not inverse_models:
            raise ValueError("No inverse model found for sensing model {}".format(model.literal))
        inverse_actions = [a for a in sensing_actions if a.name in [observed_literal_to_action_name(m.literal) for m in inverse_models]]
        #if check_formula(s_a, sensing_action.precondition) and not any(check_formula(s_a, im.condition) for im in inverse_models):
        if check_formula(s_a, sensing_action.precondition):
            if true_observations is not None and update_true_obs != true_observations:
                applicable_sensing_actions.append(sensing_action)
            #we don't want to sense inconsistently with the parent state. For example, don't sense glitter in a cell if K_neg_gold.
            #Solution: repeated application of a sensing action should give us no new information!
            elif not any(apply_action_effect(s_a, inverse_action, grounding) == s_a for inverse_action in inverse_actions):
                applicable_sensing_actions.append(sensing_action)
    #log.debug(f"applicable_sensing_actions: {[a.name for a in applicable_sensing_actions]}")
    if not applicable_sensing_actions:
        return ({s_a}, update_true_obs) if true_observations is not None else {s_a}
    if true_observations is not None:
        #apply observations according to ground truth
        log.debug(f"Applying true observations: {update_true_obs}")
        observation_combinations = set()
        combo = set()
        conj_formula = And(*update_true_obs)
        s_a_aug = apply_effect(s_a, conj_formula, grounding)
        s_a_o = s_a
        for sensing_action in applicable_sensing_actions:
            sensing_model = next((m for m in grounding.grounded_sensing_models if observed_literal_to_action_name(m.literal) == sensing_action.name), None)
            if sensing_model and check_formula(s_a_aug, sensing_model.condition):
                combo.add(sensing_action.name)
        observation_combinations.add(frozenset(combo))
        #log.debug(f"Number of observation combinations: {len(observation_combinations)}")
        for combo in observation_combinations:
            s_a_o = s_a
            for action_name in combo:
                sensing_action = next((x for x in applicable_sensing_actions if x.name == action_name), None)
                if sensing_action:
                    s_a_o = apply_action_effect(s_a_o, sensing_action, grounding)
            log.debug(f"Applying observation combination: {combo}")
            new_states.add(s_a_o)
        #log.debug(f"Number of new states with observations: {len(new_states)}")
        return new_states, update_true_obs
    #applying observations as combinations of possible sensing in a state.
    grouped_sensing_actions = {}
    for sa in applicable_sensing_actions:
        for key, var in grounding.grounded_observable_variables.items():
            if len(var) == 1:         #binary variable
                var = var | {inverse_literal(next(iter(var)))}
            if sa.name in [observed_literal_to_action_name(p) for p in var]:
                grouped_sensing_actions.setdefault(key, []).append(sa.name)
    observation_combinations = itertools.product(*[group for group in grouped_sensing_actions.values() if group])
    for combo in observation_combinations:
        s_a_o = s_a
        for action_name in combo:
            sensing_action = next((x for x in applicable_sensing_actions if x.name == action_name), None)
            if sensing_action:
                s_a_o = apply_action_effect(s_a_o, sensing_action, grounding)
        '''ground_predicate_wumpus = [p for p in s_a_o if isinstance(p, Predicate) and "pos_wumpus" in p.name]
        ground_predicate_gold = [p for p in s_a_o if isinstance(p, Predicate) and "pos_gold" in p.name]
        if ground_predicate_wumpus and ground_predicate_gold:
            if ground_predicate_wumpus[0].terms == ground_predicate_gold[0].terms:
                continue  # invalid state: wumpus and gold in the same location'''
        log.debug(f"Applying observation combination: {combo}")
        new_states.add(s_a_o)
    return new_states  # true_observations is None in this path

def complement_literal(literal: Predicate, grounding: Grounding, state: State) -> set[Predicate]:
    ground_predicates = grounding.grounded_predicates
    state_vars = grounding.grounded_state_variables | grounding.grounded_observable_variables
    #if Kx then K~x' for other X=x
    if literal.name.startswith("K_pos_"):
        for key, var in state_vars.items():
            if literal in var:
              complements = var - {literal}
              return {inverse_literal(c) for c in complements}
        return set()
    #if K~x' for all X=x' except X=x, then Kx
    elif literal.name.startswith("K_neg_") and state:
        for key, var in state_vars.items():
            # if K_pos_x in var and var is not binary
            if inverse_literal(literal) in var and literal not in var:
                complements = var - {inverse_literal(literal)}
                not_x_in_state = {c for c in complements if inverse_literal(c) in state}
                if len(complements) - len(not_x_in_state) == 1:
                    return complements - not_x_in_state
        return set()

def apply_effect(state: State, effect: Formula, grounding: Grounding) -> State:
    assert all(isinstance(f, (Predicate, FunctionEqualTo)) for f in state)
    if isinstance(effect, And):
        new_state = state
        for sub_effect in effect.operands:
            if isinstance(sub_effect, When):
                if check_formula(state, sub_effect.condition):
                    log.debug(f"Applying effect {sub_effect.effect} due to When condition {sub_effect.condition}")
                    new_state = apply_effect(new_state, sub_effect.effect, grounding)
                else:
                    continue
            else:
                new_state = apply_effect(new_state, sub_effect, grounding)
        return new_state
    elif isinstance(effect, Predicate):
        new_state = state
        if effect.name == 'K_pos_EqualTo' and effect.terms[0] == effect.terms[1]:
            return new_state
        if effect in state:
            return state
        log.debug(f"Applying effect {effect}")
        effect_complements = complement_literal(effect, grounding, state)
        all_effects = {effect} | effect_complements
        for effect in all_effects:
            if inverse_literal(effect) in state:
                new_state = set(f for f in new_state if f != inverse_literal(effect))
        return frozenset(new_state | all_effects)
    elif isinstance(effect, Not):
        log.debug(f"Applying effect {effect}")
        return frozenset(f for f in state if f != effect.argument)
    elif isinstance(effect, When):
        if check_formula(state, effect.condition):
            log.debug(f"Applying effect {effect.effect} due to When condition {effect.condition}")
            return apply_effect(state, effect.effect, grounding)
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

def get_updated_true_observation(true_observation: set[Predicate], state, action, grounding):
    #log.debug(f"update true observation for action {action.name} with current true observation {true_observation}")
    new_true_observation = true_observation.copy()
    s = apply_effect(state, And(*true_observation), grounding)
    #log.debug(f"State after applying true observation effects: {state_to_string(s)}")
    s_a = apply_action_effect(s, action, grounding)
    if (s - s_a) & true_observation:
        #collect K_pos literals
        for obs in true_observation:
            for l in (s_a - s):
                if obs.name == l.name:
                    new_true_observation.remove(obs)
                    new_true_observation.add(l)
    log.debug(f"Updated true observation from {true_observation} to {new_true_observation} after applying action {action.name}")
    return new_true_observation


class Alive(Enum):
    ALIVE = 0
    DEAD = 1
    UNKNOWN = 2
    PRUNED = 3
    NUM_PRUNED = 4
    BAD_OBS = 5


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

    def __lt__(self, other):
         return self.id < other.id


def get_num_vals(state: State) -> set[int]:
    return {f.operands[1].value for f in state if isinstance(f, FunctionEqualTo)}


class StateSpaceGraph:

    def __init__(
        self,
        domain: Domain,
        problem: PartiallyObservableProblem,
        prune: bool = True,
        selected_states: Optional[set[State]] = None,
        max_num_val: Optional[int] = None,
    ):
        self.domain = domain
        self.problem = problem
        grounding = Grounding(domain, problem)
        grounded_actions = grounding.grounded_actions
        grounded_sensing_models = grounding.grounded_sensing_models
        sensing_actions = convert_sensing_model_to_actions(grounded_sensing_models,
                                                           grounding.grounded_observable_variables)
        for action in grounded_actions:
            if action.name == 'move-right':
                log.debug(action)
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
                        root_state = apply_action_effect(root_state, sensing_action, grounding)
            self.root = StateSpaceNode(root_state, 0)
            self.next_id = 1
            self.nodes = {root_state: self.root}
            queue = [self.root]
            #log.debug(f"Initial root state: {state_to_string(root_state)}")
            true_observations = grounding.problem.hidden_predicates.copy() if grounding.problem.hidden_predicates else []
            cur_obs_index = 0
        seen = []
        true_obs_for_state = {}
        while queue or true_observations:
            #log.debug(f"current seen: {seen}")
            log.debug(f"true_observations size: {len(true_observations)}")
            log.debug(f"Queue size: {len(queue)}")
            #log.debug(f"Current queue: {[node.id for node in queue]}")

            if (not queue) and true_observations:
                true_observations.pop(0)
                true_obs_for_state = {}
                if not true_observations:
                    continue
                seen = []
                node = self.root
            else:
                node = queue.pop(0)
                if node.id in seen:
                    continue
            seen.append(node.id)
            state = node.state
            log.debug(f"Expanding node {node.id} with state {state_to_string(state)}")
            if check_formula(state, problem.goal):
                node.alive = Alive.ALIVE
                node.goal = True
                continue
            for j, action in enumerate(grounded_actions):
                if not check_formula(state, action.precondition):
                    continue
                log.debug(f"Action {action.name} is applicable")
                if true_observations:
                    true_obs_for_state[node.id] = true_observations[cur_obs_index] if node.id not in true_obs_for_state else true_obs_for_state[node.id]
                    log.debug(f"Applying action {action.name} to node {node.id} with true observations {true_obs_for_state[node.id]}")
                    new_states, updated_obs = apply_action_effect_with_observations(state, action, grounding, sensing_actions, true_obs_for_state[node.id])
                else:
                    new_states = apply_action_effect_with_observations(state, action, grounding, sensing_actions)
                for s_a_o in new_states:
                    new_node = self.add_node(s_a_o, state, action)
                    if new_node:
                        #log.debug(f"Created new node with state {state_to_string(s_a_o)}")
                        true_obs_for_state[new_node.id] = updated_obs if true_observations else None
                        if max_num_val and any(v > max_num_val for v in get_num_vals(s_a_o)):
                            new_node.alive = Alive.NUM_PRUNED
                        elif selected_states and s_a_o not in selected_states:
                                new_node.alive = Alive.PRUNED
                        else:
                            queue.append(new_node)
                    else:
                        if true_observations:
                            queue.append(self.nodes[s_a_o])

        compute_alive(self.nodes.values())
        if prune:
            self.prune_nodes()
        assert all(node.alive != Alive.UNKNOWN for node in self.nodes.values())
        assert self.root.alive == Alive.ALIVE, 'Problem {} is unsolvable'.format(problem.name)
        log.info(f"Generated state space with {len(self.nodes)} nodes")

    def add_node(self, state: State, parent_state: State, action: Action) -> Optional[StateSpaceNode]:
        parent = self.nodes[parent_state]
        log.debug(f"Adding child node to parent {parent.id} after action {action.name}")
        try:
            node = self.nodes[state]
            log.debug(f"this state already exists with id {node.id}")
            new = False
        except KeyError:
            node = StateSpaceNode(state, self.next_id)
            self.next_id += 1
            self.nodes[state] = node
            new = True
            log.debug(f"Created new node with id= {node.id} add= {state_to_string(state - parent_state)} and delete= {state_to_string(parent_state - state)}")

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
            if node.alive == Alive.BAD_OBS or (node.alive == Alive.DEAD and all([parent.alive == Alive.DEAD for parent in node.parents])):
                pruned_dead.append(state)
                if node.alive == Alive.BAD_OBS:
                    pruned_dead.extend([child.state for children in node.children.values() for child in children if child.state in self.nodes])
                    log.debug(f"pruning children of bad observation node {node.id}: {[child.id for children in node.children.values() for child in children]}")
                log.debug(f"Pruning dead node {node.id} with parents {[parent.id for parent in node.parents]}")
        before = len(self.nodes)
        for state in pruned_dead + pruned_selected:
            if state in self.nodes:
                del self.nodes[state]
        for node in self.nodes.values():
            for action, children in node.children.items():
                node.children[action] = {child for child in children if child.state in self.nodes}
        log.info(f"Pruned {len(pruned_dead)} dead " f"out of {before} states in {self.problem.name}")


def generate_state_space(domain: Domain, problem: Problem, selected_states: Optional[set[State]] = None):
    return StateSpaceGraph(domain, problem, selected_states=selected_states)


def can_reach(node: StateSpaceNode, goal_nodes: Collection[StateSpaceNode]) -> bool:
    seen = set()
    stack = [node]
    while stack:
        current_node = stack.pop()
        if current_node in goal_nodes:
            return True
        if current_node.alive in [Alive.DEAD, Alive.BAD_OBS]:
            continue
        if current_node.alive == Alive.ALIVE:
            return True
        if current_node in seen:
            continue
        seen.add(current_node)
        for children in current_node.children.values():
            if all(child.alive != Alive.DEAD for child in children):
                bad_obs_children = {child for child in children if child.alive == Alive.BAD_OBS}
                good_children = children - bad_obs_children
                stack.extend(good_children)
    return False


def find_nodes_leading_to_dead(nodes: Collection[StateSpaceNode]) -> bool:
    queue = [node for node in nodes if node.alive == Alive.UNKNOWN]
    changed = False
    while queue:
        node = queue.pop()
        if all(any(child.alive == Alive.DEAD for child in children) for children in node.children.values()):
            node.alive = Alive.DEAD if node.alive != Alive.BAD_OBS else Alive.BAD_OBS
            log.debug(f"Node {node.id} is now DEAD because all its children lead to DEAD nodes.")
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
            log.debug(f"Node {node.id} is now DEAD because it cannot reach any goal node.")
            changed = True
            for parent in node.parents:
                if parent.alive == Alive.UNKNOWN:
                    queue.append(parent)
    return changed

def remove_unsolvable_instances(nodes: Collection[StateSpaceNode]) -> bool:
    queue = [node for node in nodes if node.alive == Alive.DEAD]
    changed = False
    while queue:
        node = queue.pop()
        other_children = [children for parent in node.parents for children in parent.children.values()]
        for children in other_children:
            if node in children and any(sibling.alive != Alive.DEAD for sibling in children if sibling.id != node.id) and all(child.alive == Alive.DEAD for children in node.children.values() for child in children):
                node.alive = Alive.BAD_OBS
                log.debug(f"Node {node.id} with parents {[parent.id for parent in node.parents]} is now BAD_OBS because of alive siblings")
                changed = True
                parent_queue = [parent for parent in node.parents if parent.alive == Alive.DEAD]
                while parent_queue:
                    parent_node = parent_queue.pop()
                    if any(child.alive in (Alive.ALIVE, Alive.UNKNOWN) for children in parent_node.children.values() for child in children):
                        parent_node.alive = Alive.UNKNOWN
                        parent_queue.extend([parent for parent in parent_node.parents if parent.alive == Alive.DEAD])
    return changed

def compute_alive(nodes: Collection[StateSpaceNode]) -> None:
    changed = True
    root_node = next((node for node in nodes if node.id == 0), None)
    while changed:
        changed = find_nodes_leading_to_dead(nodes)
        changed = find_node_not_reaching_goal(nodes) or changed
        #if root node is not alive, there could be an unsolvable instance in the state space
        if root_node and root_node.alive == Alive.DEAD:
            changed = remove_unsolvable_instances(nodes) or changed
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
