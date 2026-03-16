#!/usr/bin/env python3
"""
Generate master h.pddl file for wumpus problems with hidden state scenarios.

Constraints enforced:
- Wumpuses cannot be at the safe starting position: p1-1
- Wumpuses can be at p2-1 and p1-2 (these are now allowed)
- Multiple wumpuses must be at different positions

Usage: python3 generate-h-pddl.py <p_pddl_path> <num_wumpus> <num_scenarios> [seed]
  p_pddl_path: path to the p.pddl file (e.g., p05-1f/p.pddl)
  num_wumpus: number of wumpuses (1 or 2, based on problem variant -1f or -2f)
  num_scenarios: number of scenarios to generate
                 Use 'all' to generate all unique combinations
                 Use a number for random sampling (default: 100)
  seed: random seed for reproducibility (optional, only used for random sampling)

Example: python3 generate-h-pddl.py p05-1f/p.pddl 1 all
         This generates ALL unique scenarios from p05-1f/p.pddl with 1 wumpus
Example: python3 generate-h-pddl.py p05-1f/p.pddl 1 100 42
         This generates 100 random scenarios with 1 wumpus, using seed 42
Example: python3 generate-h-pddl.py p05-1f/p.pddl 2 all
         This generates all unique scenarios with 2 wumpuses
"""

import sys
import random
import re
from itertools import combinations


def parse_positions_from_pddl(pddl_path):
    """
    Parse positions from the p.pddl file.
    
    Args:
        pddl_path: path to the p.pddl file
    
    Returns:
        tuple: (problem_name, list of positions, safe starting position)
    """
    positions = []
    problem_name = None
    
    with open(pddl_path, 'r') as f:
        content = f.read()
    
    # Extract problem name
    problem_match = re.search(r'\(define\s+\(problem\s+(\S+)\)', content)
    if problem_match:
        problem_name = problem_match.group(1)
    
    # Extract positions from :objects section
    # Look for lines with positions followed by '- pos'
    objects_section = re.search(r':objects\s+(.*?)\)', content, re.DOTALL)
    if objects_section:
        objects_text = objects_section.group(1)
        # Find all position identifiers (format: pX-Y)
        pos_matches = re.findall(r'(p\d+-\d+)', objects_text)
        positions = pos_matches
    
    if not positions:
        raise ValueError(f"No positions found in {pddl_path}")
    
    if not problem_name:
        raise ValueError(f"No problem name found in {pddl_path}")
    
    # Define safe starting position: p1-1 only
    # Wumpuses cannot be at this position
    # p2-1 and p1-2 are now allowed for wumpuses
    safe_positions = {'p1-1'}
    
    return problem_name, positions, safe_positions


def generate_scenario(positions, safe_positions, num_wumpus):
    """
    Generate a single hidden state scenario with wumpus positions only.
    
    Ensures that:
    - Wumpuses are NOT at the safe starting position (p1-1)
    - Multiple wumpuses are at different positions
    
    Args:
        positions: list of all available positions
        safe_positions: set of safe positions where wumpus cannot be placed
        num_wumpus: number of wumpuses to place (1 or 2)
    
    Returns:
        list: wumpus_positions
    """
    # Filter positions for wumpus (exclude safe position p1-1)
    non_safe_positions = [p for p in positions if p not in safe_positions]
    
    if len(non_safe_positions) < num_wumpus:
        raise ValueError(f"Not enough non-safe positions available. Need {num_wumpus}, have {len(non_safe_positions)}")
    
    # Randomly select positions for wumpus(es)
    wumpus_positions = random.sample(non_safe_positions, num_wumpus)
    
    return wumpus_positions


def generate_all_scenarios(positions, safe_positions, num_wumpus):
    """
    Generate all possible unique hidden state scenarios with wumpus positions.
    
    Args:
        positions: list of all available positions
        safe_positions: set of safe positions where wumpus cannot be placed
        num_wumpus: number of wumpuses to place (1 or 2)
    
    Returns:
        list of lists: [[wumpus_positions], ...]
    """
    scenarios = []
    non_safe_positions = [p for p in positions if p not in safe_positions]
    
    # For each combination of wumpus positions
    for wumpus_combo in combinations(non_safe_positions, num_wumpus):
        wumpus_positions = list(wumpus_combo)
        scenarios.append(wumpus_positions)
    
    return scenarios


def format_hidden_clause(wumpus_positions, randomize_order=True):
    """Format a single :hidden clause with wumpus positions."""
    elements = []
    
    # Add wumpus positions
    wumpus_items = [("wumpus-at", wpos) for wpos in wumpus_positions]
    
    # Randomly shuffle the order (only for random mode)
    if randomize_order:
        random.shuffle(wumpus_items)
    
    # Format each element
    for predicate, pos in wumpus_items:
        elements.append(f"({predicate} {pos})")
    
    return "    (:hidden " + " ".join(elements) + ")"


def generate_h_pddl(problem_name, positions, safe_positions, num_wumpus, num_scenarios, seed=None):
    """
    Generate the complete h.pddl file.
    
    Args:
        problem_name: name of the problem from p.pddl
        positions: list of all available positions
        safe_positions: set of safe positions where wumpus cannot be placed
        num_wumpus: number of wumpuses (1 or 2)
        num_scenarios: number of scenarios to generate, or 'all' for all unique combinations
        seed: random seed (optional, only used for random sampling)
    """
    # Generate header
    lines = [f"(define (problem {problem_name})"]
    
    if num_scenarios == 'all':
        # Generate all unique combinations
        all_scenarios = generate_all_scenarios(positions, safe_positions, num_wumpus)
        for wumpus_positions in all_scenarios:
            hidden_clause = format_hidden_clause(wumpus_positions, randomize_order=False)
            lines.append(hidden_clause)
    else:
        # Random sampling mode
        if seed is not None:
            random.seed(seed)
        
        # Generate random scenarios
        for _ in range(num_scenarios):
            wumpus_positions = generate_scenario(positions, safe_positions, num_wumpus)
            hidden_clause = format_hidden_clause(wumpus_positions, randomize_order=True)
            lines.append(hidden_clause)
    
    # Add closing parenthesis
    lines.append(")")
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    try:
        pddl_path = sys.argv[1]
        num_wumpus = int(sys.argv[2])
        
        # Handle 'all' or numeric value for num_scenarios
        num_scenarios_arg = sys.argv[3] if len(sys.argv) > 3 else "100"
        if num_scenarios_arg.lower() == 'all':
            num_scenarios = 'all'
        else:
            num_scenarios = int(num_scenarios_arg)
            if num_scenarios < 1:
                print("Error: Number of scenarios must be at least 1")
                sys.exit(1)
        
        seed = int(sys.argv[4]) if len(sys.argv) > 4 else None
        
        if num_wumpus not in [1, 2]:
            print("Error: Number of wumpuses must be 1 or 2")
            sys.exit(1)
        
        # Parse positions from p.pddl file
        problem_name, positions, safe_positions = parse_positions_from_pddl(pddl_path)
        
        print(f"# Parsed {len(positions)} positions from {pddl_path}", file=sys.stderr)
        print(f"# Problem name: {problem_name}", file=sys.stderr)
        print(f"# Safe positions (wumpus excluded): {safe_positions}", file=sys.stderr)
        
        if num_scenarios == 'all':
            # Calculate expected number of scenarios
            non_safe_count = len([p for p in positions if p not in safe_positions])
            if num_wumpus == 1:
                # wumpus choices = N (number of non-safe positions)
                expected = non_safe_count
            else:  # num_wumpus == 2
                # C(N, 2) combinations
                from math import comb
                expected = comb(non_safe_count, 2)
            
            print(f"# Generating ALL unique scenarios ({expected} expected) with {num_wumpus} wumpus(es)", file=sys.stderr)
        else:
            print(f"# Generating {num_scenarios} random scenarios with {num_wumpus} wumpus(es)", file=sys.stderr)
        
        # Generate and print the h.pddl content
        content = generate_h_pddl(problem_name, positions, safe_positions, num_wumpus, num_scenarios, seed)
        print(content)
        
        # Report actual number generated (only for 'all' mode)
        if num_scenarios == 'all':
            actual_count = content.count(':hidden')
            print(f"# Generated {actual_count} unique scenarios", file=sys.stderr)
        
    except FileNotFoundError:
        print(f"Error: File not found - {sys.argv[1]}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Invalid argument - {e}")
        print(__doc__)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
