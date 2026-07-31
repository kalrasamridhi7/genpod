from typing import Collection
from pddl.logic import Predicate
from pddl.logic.base import Not, Formula
from pddl.logic.terms import Term, Constant
import re

def _parse_formulas(content: str) -> list:
    """
    Parse formulas from hidden content string.
    Handles both predicates and negated predicates.
    
    Args:
        content: String containing formulas like (pred arg1) or (not (pred arg1))
        
    Returns:
        List of formulas (Predicate or Not instances)
    """
    formulas = []
    i = 0
    while i < len(content):
        if content[i] == '(':
            # Find matching closing parenthesis
            depth = 1
            j = i + 1
            while j < len(content) and depth > 0:
                if content[j] == '(':
                    depth += 1
                elif content[j] == ')':
                    depth -= 1
                j += 1
            
            # Extract formula string
            formula_str = content[i+1:j-1].strip()
            
            # Check if it's a negated formula
            if formula_str.startswith('not '):
                # Extract the inner predicate
                inner_content = formula_str[4:].strip()
                if inner_content.startswith('(') and inner_content.endswith(')'):
                    inner_content = inner_content[1:-1].strip()
                
                parts = inner_content.split()
                if parts:
                    predicate_name = parts[0]
                    args = [Constant(arg) for arg in parts[1:]] if len(parts) > 1 else []
                    pred = Predicate(predicate_name, *args)
                    formulas.append(Not(pred))
            else:
                # Regular predicate
                parts = formula_str.split()
                if parts:
                    predicate_name = parts[0]
                    args = [Constant(arg) for arg in parts[1:]] if len(parts) > 1 else []
                    pred = Predicate(predicate_name, *args)
                    formulas.append(pred)
            
            i = j
        else:
            i += 1
    
    return formulas

def parse_hidden_state_predicates(files: Collection[str]) -> dict[str, list[set[Formula]]]:
    """
    Parse hidden state formulas from ground truth string.
    
    Args:
        ground_truth: files containing hidden states
        
    Returns:
        Dictionary of parsed formulas (predicates or negated predicates)
    """
    if not files:
        return {}

    predicates = {}
    for file in files:
        with open(file, 'r') as f:
            lines = f.readlines()
            problem_name = None
            for line in lines:
                line = line.strip()
                if not line or line.startswith(';'):
                    continue

                # Parse predicate format: predicate_name(arg1, arg2, ...)
                # Extract problem name from line like (problem problem-name)
                if line.startswith('(define (problem'):
                    # Extract problem name from (define (problem <problem_name>)
                    match = re.search(r'\(define\s+\(problem\s+(\S+)\)', line)
                    if match:
                        problem_name = match.group(1)
                        predicates[problem_name] = []
                    continue
                
                # Parse hidden block: (:hidden ...)
                if '(:hidden' in line:
                    formula_set = set()
                    match = re.search(r'\(:hidden\s+(.*)\)$', line)
                    if match and problem_name in predicates:
                        # Extract content between (:hidden ... ) - handle both same line and potential variations
                        hidden_content = match.group(1).strip()
                        # Parse formulas - handle both (predicate ...) and (not (predicate ...))
                        formulas = _parse_formulas(hidden_content)
                        for formula in formulas:
                            formula_set = formula_set | {formula}
                    predicates[problem_name].append(formula_set)
    return predicates


if __name__ == "__main__":
    parse_hidden_state_predicates(["domains/partially-observable-deterministic/wumpus/p5/p5_hidden.pddl"])
