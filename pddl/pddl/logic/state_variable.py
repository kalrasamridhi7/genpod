from typing import Optional, Sequence
from pddl.logic.base import Formula
from pddl.logic.terms import Term, Variable
from pddl.helpers.base import _typed_parameters, ensure_sequence


class MultivaluedVariable:
    """
    Base class for state variables and observable variables.
    """
    def __init__(
        self,
        variable: Formula,
        exception: Optional[Formula] = None,
        formula: Formula = None,
    ) -> None:
        """
        Initialize the base variable.

        :param variable: the variable predicate skeleton
        :param exception: the exception condition (optional)
        :param formula: the formula condition
        """
        self._variable = variable
        self._exception = exception
        self._formula = formula

    @property
    def variable(self) -> Formula:
        """Get the variable."""
        return self._variable

    @property
    def exception(self) -> Optional[Formula]:
        """Get the exception."""
        return self._exception

    @property
    def formula(self) -> Formula:
        """Get the formula."""
        return self._formula

    @property
    def parameters(self) -> Sequence[Variable]:
        """Get the parameters from the variable."""
        if hasattr(self._variable, 'terms'):
            return self._variable.terms
        return []

    @property
    def terms(self) -> Sequence[Term]:
        """Get the terms."""
        return self.parameters

    def __hash__(self) -> int:
        """Get the hash."""
        return hash((
            type(self), 
            self.variable, 
            self.exception,
            self.formula
        ))

    def __eq__(self, other):
        """Override equal operator."""
        return (
            type(self) == type(other)
            and self.variable == other.variable
            and self.exception == other.exception
            and self.formula == other.formula
        )

    def __repr__(self) -> str:
        """Get the string representation."""
        return (f"{type(self).__name__}(variable={self.variable}, "
                f"exception={self.exception}, formula={self.formula})")


class StateVariable(MultivaluedVariable):
    """
    Represents a state variable: a predicate with its possible values and conditions.
    """
    
    def __str__(self):
        """Get the string representation."""
        operator_str = "(:state-variable "
        operator_str += f"{self.variable} "
        if self.exception is not None:
            operator_str += f"{str(self.exception)} "
        operator_str += f"{str(self.formula)}"
        operator_str += ")"
        return operator_str


class ObservableVariable(MultivaluedVariable):
    """
    Represents an observable variable: a predicate that can be observed with its conditions.
    """
    
    def __str__(self):
        """Get the string representation."""
        operator_str = "(:obs-variable "
        operator_str += f"{self.variable} "
        if self.exception is not None:
            operator_str += f"{str(self.exception)} "
        operator_str += f"{str(self.formula)}"
        operator_str += ")"
        return operator_str