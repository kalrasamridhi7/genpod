#!/usr/bin/env python3
"""
Script to generate a hidden instance file for binary search domain.
Takes a PDDL problem file and produces a hidden file with a randomly selected secret state.
"""

import re
import random
import argparse
from pathlib import Path


def parse_problem_file(problem_path):
    """
    Parse a PDDL problem file to extract problem name and state objects.
    
    Args:
        problem_path: Path to the PDDL problem file
        
    Returns:
        tuple: (problem_name, list of state objects)
    """
    with open(problem_path, 'r') as f:
        content = f.read()
    
    # Extract problem name
    problem_name_match = re.search(r'\(define\s+\(problem\s+(\S+)\)', content)
    if not problem_name_match:
        raise ValueError("Could not find problem name in file")
    problem_name = problem_name_match.group(1)
    
    # Extract objects of type state
    # Pattern: (:objects ... pX pY pZ ... - state ...)
    objects_match = re.search(r'\(:objects\s+(.*?)\)', content, re.DOTALL)
    if not objects_match:
        raise ValueError("Could not find objects declaration in file")
    
    objects_content = objects_match.group(1)
    
    # Find all objects declared as type state
    # Pattern: p0 p1 p2 - state
    state_objects = []
    state_pattern = r'([\w\-]+(?:\s+[\w\-]+)*)\s+-\s+state'
    state_matches = re.finditer(state_pattern, objects_content)
    
    for match in state_matches:
        objects_str = match.group(1)
        # Split by whitespace to get individual object names
        objects = objects_str.split()
        state_objects.extend(objects)
    
    if not state_objects:
        raise ValueError("Could not find any state objects in file")
    
    return problem_name, state_objects


def generate_hidden_file(problem_name, secret_states, output_path):
    """
    Generate a hidden instance file with the specified secret states.
    
    Args:
        problem_name: Name of the problem
        secret_states: List of state objects to mark as secret
        output_path: Path where the hidden file should be written
    """
    hidden_lines = '\n'.join(f"    (:hidden (secret {state}))" for state in secret_states)
    content = f"""(define (problem {problem_name})
{hidden_lines}
)
"""
    
    with open(output_path, 'w') as f:
        f.write(content)
    
    print(f"Generated hidden instance file: {output_path}")
    print(f"Secret states ({len(secret_states)}): {', '.join(secret_states)}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate hidden instance file for binary search domain"
    )
    parser.add_argument(
        'problem_file',
        type=str,
        help='Path to the PDDL problem file (can be relative to current directory)'
    )
    parser.add_argument(
        '-n', '--num-instances',
        type=int,
        default=None,
        help='Number of secret states to randomly select (default: prompt user)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output path for hidden file (default: <problem_file>_hidden.pddl)'
    )
    parser.add_argument(
        '-s', '--seed',
        type=int,
        help='Random seed for reproducibility'
    )
    
    args = parser.parse_args()
    
    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)
    
    # Parse problem file (resolve relative to current directory)
    problem_path = Path(args.problem_file).resolve()
    if not problem_path.exists():
        print(f"Error: Problem file not found: {problem_path}")
        return 1
    
    try:
        problem_name, state_objects = parse_problem_file(problem_path)
        print(f"Found {len(state_objects)} state objects: {', '.join(state_objects)}")
        
        # Determine number of instances
        if args.num_instances is None:
            while True:
                try:
                    user_input = input(f"How many secret states to select? (1-{len(state_objects)}): ")
                    num_instances = int(user_input)
                    if 1 <= num_instances <= len(state_objects):
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(state_objects)}")
                except ValueError:
                    print("Please enter a valid number")
        else:
            num_instances = args.num_instances
            if num_instances < 1 or num_instances > len(state_objects):
                print(f"Error: Number of instances must be between 1 and {len(state_objects)}")
                return 1
        
        # Randomly select secret states (without replacement)
        secret_states = random.sample(state_objects, num_instances)
        
        # Determine output path
        if args.output:
            output_path = Path(args.output).resolve()
        else:
            # Default: replace .pddl with _hidden.pddl
            output_path = problem_path.parent / f"{problem_path.stem}_hidden.pddl"
        
        # Generate hidden file
        generate_hidden_file(problem_name, secret_states, output_path)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
