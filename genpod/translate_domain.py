import logging
from typing import List
from pddl.logic.base import And, Formula, is_literal, Atomic, Not, Or, ForallCondition, ExistsCondition
from pddl.logic import Predicate, StateVariable, ObservableVariable, MultivaluedVariable
from pddl.logic.predicates import EqualTo
from pddl.logic.sensing_model import SensingModel
from pddl.logic.effects import When, Forall
from pddl.helpers.base import ensure_set
from pddl.core import Domain, Problem
from pddl.action import Action
from pddl.parser.symbols import Symbols
from genpod.ground import ground_domain_predicates, inverse_literal, ground_state_variables
from genpod.partially_observable_problem import PartiallyObservableProblem

log = logging.getLogger(__name__)
GROUND_INSTANCE_GROUP_FACTOR = 2

class K_Translator:
    """A translator that translates a domain and problem to K-translation."""
    def __init__(self, domain: Domain, problems: List[Problem], hidden_predicates: dict[str, list[set[Formula]]] = None):
        self.original_domain = domain
        self.original_problems = problems
        self.translated_domain = None
        self.translated_problems = []

        translated_hidden_predicates = {}

        predicates = {
            self.k_pos_literal(pred) for pred in self.original_domain.predicates
        }
        predicates.update({
            self.k_neg_literal(pred) for pred in self.original_domain.predicates
        })
        actions = [self.translate_action(action) for action in self.original_domain.actions]
        sensing_models = [self.translate_sensing_model(model) for model in self.original_domain.sensing_models]
        state_variables = [self.translate_state_variable(var) for var in self.original_domain.state_variables]
        observable_variables = [self.translate_state_variable(var) for var in self.original_domain.observable_variables]
        # add sensing actions for each observable literal
        self.translated_domain = Domain(
            name=self.original_domain.name,
            requirements=self.original_domain.requirements,
            types=self.original_domain.types,
            predicates=ensure_set(predicates),
            actions=actions,
            sensing_models=sensing_models,
            constants=self.original_domain.constants,
            state_variables=[StateVariable(var.variable, var.exception, var.formula) for var in state_variables],
            observable_variables=[ObservableVariable(var.variable, var.exception, var.formula) for var in observable_variables]
        )

        for problem in self.original_problems:
            ground_predicates = ground_domain_predicates(domain, problem)
            init=self._get_problem_init(problem)
            goal=self.k_translate_formula(problem.goal)

            if hidden_predicates is not None:
                log.debug(f"Adding hidden predicates for problem {problem.name}")
                # add hidden predicates for the problem
                for i, formula_set in enumerate(hidden_predicates.get(problem.name, [])):
                    if i == 0:
                        translated_list = []
                    for fact in formula_set:
                        # Extract the predicate from the formula (handle both Predicate and Not(Predicate))
                        pred = fact.argument if isinstance(fact, Not) else fact
                        if pred not in ground_predicates:
                            raise ValueError(f"Hidden predicate {pred} is not a grounded predicate in the domain. {ground_predicates}")
                    translated_set = {self.k_translate_formula(fact) for fact in formula_set}
                    translated_list.append(translated_set)
                    #if i % GROUND_INSTANCE_GROUP_FACTOR == GROUND_INSTANCE_GROUP_FACTOR - 1 or i == len(hidden_predicates.get(problem.name, [])) - 1:
                translated_problem = Problem(
                            name=problem.name,
                            domain=self.translated_domain,
                            objects=problem.objects,
                            init=init,
                            goal=goal,
                            requirements=problem.requirements
                        )
                self.translated_problems.append(PartiallyObservableProblem(translated_problem, translated_list))
            else:
                translated_problem = Problem(
                                    name=problem.name,
                                    domain=self.translated_domain,
                                    objects=problem.objects,
                                    init=init,
                                    goal=goal,
                                    requirements=problem.requirements
                                )
                self.translated_problems.append(PartiallyObservableProblem(translated_problem, []))

    def k_translate_formula(self, formula: Formula) -> Formula:
        """Translate a formula to K-translation."""
        if isinstance(formula, Not):
            if is_literal(formula):
                return self.k_neg_literal(formula.argument)
            elif isinstance(formula.argument, And):
                return self.k_translate_formula(Or(*[Not(f) for f in formula.argument.operands]))
            elif isinstance(formula.argument, Or):
                return self.k_translate_formula(And(*[Not(f) for f in formula.argument.operands]))
            elif isinstance(formula.argument, Not):
                return self.k_translate_formula(formula.argument.argument)
            else:
                raise ValueError("Negation of non-literal, non-And/Or formula is not supported.")
        elif isinstance(formula, Atomic):
            if not isinstance(formula, EqualTo) and (formula.name.startswith("K_pos_") or formula.name.startswith("K_neg_")):
                return formula  # Already translated
            elif isinstance(formula, Predicate):
                return Predicate(
                    f"K_pos_{formula.name}",
                    *(formula.terms)
                )
            elif isinstance(formula, EqualTo):
                return self.k_pos_literal(formula)
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
            raise ValueError(f"Formula type: {type(literal)}. Other atomic formulas than Predicate and EqualTo are not supported.")

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
        if is_literal(action.precondition) or isinstance(action.precondition, And) or isinstance(action.precondition, Or):
            new_precondition = self.k_translate_formula(action.precondition)
        else:
            raise ValueError("Action precondition must be a literal, And formula, or an Or formula.")

        new_effects = []
        # for each effect C -> X=x, we add KC -> Kx and ~K~C -> ~K~x. 
        if is_literal(action.effect):
            new_effects.append(self.k_translate_formula(action.effect))
        elif isinstance(action.effect, When):
            new_effects.extend(self.translate_conditional_effect(action.effect))
        elif isinstance(action.effect, And):
            for effect in action.effect.operands:
                if is_literal(effect):
                    new_effects.append(self.k_translate_formula(effect))
                elif isinstance(effect, When):
                    new_effects.extend(self.translate_conditional_effect(effect))
                elif isinstance(effect, Forall):
                    if isinstance(effect.effect, When):
                        translated_when_effects = self.translate_conditional_effect(effect.effect)
                        translated_condition = And(translated_when_effects[0], translated_when_effects[1])
                        new_effects.append(ForallCondition(
                            variables=effect.variables,
                            cond=translated_condition
                        ))
                    else:
                        translated_condition = self.k_translate_formula(effect.effect)
                    new_effects.append(ForallCondition(
                        variables=effect.variables,
                        cond=translated_condition
                    ))
                else:
                    raise ValueError("Effect must be a literal, When, or ForallCondition formula.")
        elif isinstance(action.effect, Forall):
            effect = action.effect
            if isinstance(effect.effect, When):
                translated_when_effects = self.translate_conditional_effect(effect.effect)
                translated_condition = And(translated_when_effects[0], translated_when_effects[1])
                new_effects.append(ForallCondition(
                    variables=effect.variables,
                    cond=translated_condition
                ))
            else:
                translated_condition = self.k_translate_formula(effect.effect)
                new_effects.append(ForallCondition(
                    variables=effect.variables,
                    cond=translated_condition
                ))
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
        
        # Build cancellation condition: (¬K_not_x ∧ ¬K_not_y ∧ ... ∧ ¬K_not_z)
        if isinstance(when.condition, And):
            cancellation_condition_operands = [
                Not(self.k_translate_formula(Not(cond))) 
                for cond in when.condition.operands
            ]
            cancellation_condition = And(*cancellation_condition_operands)
        else:
            cancellation_condition = Not(self.k_translate_formula(Not(when.condition)))
        
        # Build cancellation effect: (¬K_not_a ∧ ¬K_not_b ∧ ... ∧ ¬K_not_c)
        if isinstance(when.effect, And):
            cancellation_effect_operands = [
                Not(self.k_translate_formula(Not(effect))) 
                for effect in when.effect.operands
            ]
            cancellation_effect_formula = And(*cancellation_effect_operands)
        elif is_literal(when.effect):
            cancellation_effect_formula = Not(self.k_translate_formula(Not(when.effect)))
        else:
            raise ValueError("Effect of a conditional effect must be a literal or an And formula.")
        
        cancellation_effect = When(cancellation_condition, cancellation_effect_formula)
        new_effects = [support_effect, cancellation_effect]
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
    
    def translate_state_variable(self, var: MultivaluedVariable) -> MultivaluedVariable:
        var = MultivaluedVariable(
            variable=var.variable,
            exception=self.k_translate_formula(var.exception) if var.exception else None,
            formula=self.k_translate_formula(var.formula)
        )
        return(var)

    def _get_problem_init(self, problem: Problem) -> set[Predicate]:
        """Get the initial state predicates from a problem."""
        init = ensure_set([self.k_translate_formula(fact) for fact in problem.init])
        grounded_domain_predicates = ground_domain_predicates(self.translated_domain, problem)
        state_vars = ground_state_variables(self.translated_domain, problem, grounded_domain_predicates, is_observable=False)
        #if Kx then K~x' for other X=x
        for key, var in state_vars.items():
            if len(var) == 1 and not any(l in init for l in var):
                init = init | {inverse_literal(next(iter(var)))}
            elif any(l in init for l in var):
                for l in var:
                    if l not in init:
                        init = init | {inverse_literal(l)}
        return init
