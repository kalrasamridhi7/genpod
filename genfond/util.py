from typing import Collection
from pddl.logic import Predicate
from pddl.logic.terms import Term, Constant
import re

def parse_hidden_state_predicates(files: Collection[str]) -> dict[str, list[Predicate]]:
    """
    Parse hidden state predicates from ground truth string.
    
    Args:
        ground_truth: files containing hidden states
        
    Returns:
        Dictionary of parsed predicates
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
                    predicate_set = set()
                    match = re.search(r'\(:hidden\s+(.*)\)$', line)
                    if match and problem_name in predicates:
                        # Extract content between (:hidden ... ) - handle both same line and potential variations
                        hidden_content = match.group(1).strip()
                        # Split by predicates (each starting with '(')
                        pred_matches = re.findall(r'\(([^)]+)\)', hidden_content)
                        for pred_str in pred_matches:
                            parts = pred_str.split()
                            if parts:
                                predicate_name = parts[0]
                                args = parts[1:] if len(parts) > 1 else []
                                args = [Constant(arg) for arg in args]
                                pred = Predicate(predicate_name, *args)
                                predicate_set = predicate_set | {pred}
                    predicates[problem_name].append(predicate_set)

    return predicates


if __name__ == "__main__":
    parse_hidden_state_predicates(["domains/partially-observable-deterministic/wumpus/p5/p5_hidden.pddl"])
