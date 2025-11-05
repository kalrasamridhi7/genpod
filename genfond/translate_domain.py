import logging
from typing import List
from pddl.logic.base import And, Formula, is_literal, Atomic, Not, Or, ForallCondition, ExistsCondition
from pddl.logic import Predicate
from pddl.logic.predicates import EqualTo
from pddl.logic.sensing_model import SensingModel
from pddl.logic.effects import When, CondEffect
from pddl.helpers.base import ensure_set
from pddl.core import Domain, Problem
from pddl.action import Action
from pddl.parser.symbols import Symbols
from genfond.ground import ground_domain_predicates

log = logging.getLogger(__name__)

class K_Translator:
    """A translator that translates a domain and problem to K-translation."""
    def __init__(self, domain: Domain, problems: List[Problem]):
        self.original_domain = domain
        self.original_problems = problems
        self.translated_domain = None
        self.translated_problems = []

        predicates = {
            self.k_pos_literal(pred) for pred in self.original_domain.predicates
        }
        predicates.update({
            self.k_neg_literal(pred) for pred in self.original_domain.predicates
        })
        actions = [self.translate_action(action) for action in self.original_domain.actions]
        sensing_models = [self.translate_sensing_model(model) for model in self.original_domain.sensing_models]
        # add sensing actions for each observable literal
        self.translated_domain = Domain(
            name=self.original_domain.name,
            requirements=self.original_domain.requirements,
            types=self.original_domain.types,
            predicates=ensure_set(predicates),
            actions=actions,
            sensing_models=sensing_models,
            constants=self.original_domain.constants
        )

        for problem in self.original_problems:
            ground_predicates = ground_domain_predicates(domain, problem)
            problem = enforce_closed_world_assumption(problem, ground_predicates)
            translated_problem = Problem(
                name=problem.name,
                domain=self.translated_domain,
                objects=problem.objects,
                init=ensure_set(
                    [self.k_translate_formula(fact) for fact in problem.init]
                ),
                goal=self.k_translate_formula(problem.goal),
                requirements=problem.requirements
            )
            self.translated_problems.append(translated_problem)

    def k_translate_formula(self, formula: Formula) -> Formula:
        """Translate a formula to K-translation."""
        if isinstance(formula, Not):
            if is_literal(formula):
                return self.k_neg_literal(formula.argument)
            elif isinstance(formula.argument, And):
                return self.k_translate_formula(Or([(Not(f)) for f in formula.operands]))
            elif isinstance(formula.argument, Or):
                return self.k_translate_formula(And([(Not(f)) for f in formula.operands]))
            elif isinstance(formula.argument, Not):
                return self.k_translate_formula(formula.argument.argument)
            else:
                raise ValueError("Negation of non-literal, non-And/Or formula is not supported.")
        elif isinstance(formula, Atomic):
            if formula.name.startswith("K_pos_") or formula.name.startswith("K_neg_"):
                return formula  # Already translated
            else:
                return Predicate(
                    f"K_pos_{formula.name}",
                    *(formula.terms)
                )
        elif isinstance(formula, And):
            return And(*[self.k_translate_formula(f) for f in formula.operands])
        elif isinstance(formula, Or):
            return Or(*[self.k_translate_formula(f) for f in formula.operands])
        elif isinstance(formula, ForallCondition) or isinstance(formula, ExistsCondition):
            return type(formula)(
                variables=formula.variables,
                cond=self.k_translate_formula(formula.condition)
            )
        else:
            raise ValueError(f"Unsupported formula type: {type(formula)}")


    def k_neg_literal(self, literal: Atomic) -> Atomic:
        if isinstance(literal, Predicate):
            return Predicate(
                f"K_neg_{literal.name}",
                *(literal.terms)
            )
        elif isinstance(literal, EqualTo):
            return Predicate(
                f"K_neg_EqualTo",
                literal.left,
                literal.right
            )
        else: 
            print(type(literal))
            raise ValueError("Other atomic formulas than Predicate and EqualTo are not supported.")

    def k_pos_literal(self, literal: Atomic) -> Atomic:
        if isinstance(literal, Predicate):
            return Predicate(
                f"K_pos_{literal.name}",
                *(literal.terms)
            )
        elif isinstance(literal, EqualTo):
            return Predicate(
                f"K_pos_EqualTo",
                literal.left,
                literal.right
            )
        else: 
            raise ValueError("Other atomic formulas than Predicate and EqualTo are not supported.")

    def translate_action(self, action: Action) -> Action:
        if is_literal(action.precondition) or isinstance(action.precondition, And) or action.precondition is None:
            new_precondition = self.k_translate_formula(action.precondition)
        else:
            raise ValueError("Action precondition must be a literal or an And formula.")

        new_effects = []
        # for each effect C -> X=x, we add KC -> Kx and ~K~C -> ~K~x. 
        if is_literal(action.effect):
            new_effects.append(self.k_translate_formula(action.effect))
        elif isinstance(action.effect, When):
            new_effects.append(self.translate_conditional_effect(action.effect))
        elif isinstance(action.effect, And):
            for effect in action.effect.operands:
                if is_literal(effect):
                    new_effects.append(self.k_translate_formula(effect))
                elif isinstance(effect, When):
                    new_effects.extend(self.translate_conditional_effect(effect))
                else:
                    raise ValueError("Effect must be a literal or a When formula.")
        else: raise ValueError("Action effect must be a literal, When, or And formula.")
        return Action(
            name=action.name,
            parameters=action.parameters,
            precondition=new_precondition,
            effect=And(*new_effects)
        )

    def translate_conditional_effect(self, when: When) -> List[When]:
        new_effects = []
        support_effect = When(
                        self.k_translate_formula(when.condition),
                        self.k_translate_formula(when.effect)
                    )
        cancellation_effect = When(
                        Not(self.k_translate_formula(Not(when.condition))),
                        Not(self.k_translate_formula(Not(when.effect)))
                    )
        new_effects.extend([support_effect, cancellation_effect])
        return new_effects
    
    def translate_sensing_model(self, model) -> SensingModel:
        new_precondition = self.k_translate_formula(model.precondition)
        new_literal = self.k_translate_formula(model.literal)
        new_condition = self.k_translate_formula(model.condition)
        return SensingModel(
            parameters = model.parameters,
            precondition = new_precondition,
            literal=new_literal,
            condition=new_condition
        )

def enforce_closed_world_assumption(problem: Problem, grounded_predicates: set[Predicate]) -> Problem:
    """Enforce the closed world assumption on a problem by adding negated literals for all unmentioned grounded predicates."""
    current_facts = problem.init
    current_predicate_names = {fact.name for fact in current_facts if isinstance(fact, Predicate)}
    all_facts = grounded_predicates
    negated_facts = set()
    for fact in all_facts:
        if isinstance(fact, Predicate) and fact not in current_facts:
            if fact.name in current_predicate_names:
                negated_facts.add(Not(fact))
    new_init = current_facts.union(negated_facts)
    return Problem(
        name=problem.name,
        domain_name=problem.domain_name,
        objects=problem.objects,
        init=new_init,
        goal=problem.goal,
        requirements=problem.requirements
    )
