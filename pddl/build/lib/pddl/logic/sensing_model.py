from typing import Optional, Sequence
from pddl.logic.base import Formula
from pddl.logic.terms import Term, Variable
from pddl.helpers.base import _typed_parameters, ensure_sequence

class SensingModel:
    """
    Represents a sensing model: a mapping from an observable predicate value
    to a condition (formula) under which it holds.
    """
    def __init__(
        self,
        parameters: Sequence[Variable],
        literal: Formula,
        condition: Formula,
        precondition: Optional[Formula] = None,
    ) -> None:
        self._literal = literal
        self._condition = condition
        self._parameters: Sequence[Variable] = ensure_sequence(parameters)
        self._precondition = precondition

    @property
    def literal(self) -> Formula:
        """Get the literal."""
        return self._literal

    @property
    def condition(self) -> Formula:
        """Get the condition."""
        return self._condition

    @property
    def parameters(self) -> Sequence[Variable]:
        """Get the parameters."""
        return self._parameters

    @property
    def terms(self) -> Sequence[Term]:
        """Get the terms."""
        return self.parameters

    @property
    def precondition(self) -> Optional[Formula]:
        """Get the precondition."""
        return self._precondition

    def __hash__(self) -> int:
        """Get the hash."""
        return hash((
            SensingModel, 
            self.literal, 
            self.condition, 
            frozenset(self.parameters),
            self.precondition
        ))

    def __str__(self):
        """Get the string."""
        operator_str = "(:sensing \n"
        operator_str += f"    :parameters ({_typed_parameters(self.parameters)})\n"
        operator_str += f"    :model-for {self.literal}\n"
        if self.precondition is not None:
            operator_str += f"    :precondition {str(self.precondition)}\n"
        operator_str += f"    :such-that {str(self.condition)}\n"
        operator_str += ")"
        return operator_str

    def __repr__(self) -> str:
        """Get the string representation."""
        return (f"{type(self).__name__}(parameters={', '.join(map(str, self.parameters))}, "
            f"literal={self.literal} precondition={self.precondition}, condition={self.condition})")

    def __eq__(self, other):
        """Override equal operator."""
        return (
            isinstance(other, SensingModel)
            and self.literal == other.literal
            and self.condition == other.condition
            and self.parameters == other.parameters
            and self.precondition == other.precondition
        )
