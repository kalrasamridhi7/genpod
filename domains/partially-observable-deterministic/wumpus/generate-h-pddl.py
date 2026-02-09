#!/usr/bin/env python3
"""
Generate master h.pddl file for wumpus problems with random hidden state scenarios.

Constraints enforced:
- Pit, wumpus(es), and gold must all be at different positions
- None can be at safe starting positions: p1-1 (agent start), p2-1, p1-2
- Each scenario has 0 or 1 pit, N wumpuses (1 or 2), and 1 gold

Usage: python3 generate-h-pddl.py <p_pddl_path> <num_wumpus> <num_scenarios> [num_pits] [seed]
  p_pddl_path: path to the p.pddl file (e.g., p05-1f/p.pddl)
  num_wumpus: number of wumpuses (1 or 2, based on problem variant -1f or -2f)
  num_scenarios: number of hidden state scenarios to generate (default: 100)
  num_pits: number of pits (0 or 1, default: 1)
  seed: random seed for reproducibility (optional)

Example: python3 generate-h-pddl.py p05-1f/p.pddl 1 100 1
         This generates scenarios using positions from p05-1f/p.pddl with 1 wumpus, 1 pit, and 100 scenarios
Example: python3 generate-h-pddl.py p05-1f/p.pddl 1 100 0 42
         This generates scenarios with 1 wumpus, 0 pits, 100 scenarios, using seed 42
"""

import sys
import random
import re


def parse_positions_from_pddl(pddl_path):
    """
    Parse positions from the p.pddl file.
    
    Args:
        pddl_path: path to the p.pddl file
    
    Returns:
        tuple: (problem_name, list of positions excluding safe starting area)
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
    
    # Remove safe starting area: p1-1, p2-1, p1-2
    # These positions should never have pits or wumpuses
    safe_positions = {'p1-1', 'p2-1', 'p1-2'}
    positions = [p for p in positions if p not in safe_positions]
    
    if not positions:
        raise ValueError(f"No positions found in {pddl_path}")
    
    if not problem_name:
        raise ValueError(f"No problem name found in {pddl_path}")
    
    return problem_name, positions


def generate_scenario(positions, num_wumpus, num_pits=1):
    """
    Generate a single hidden state scenario.
    
    Ensures that:
    - Pit, wumpus(es), and gold are all at different positions
    - None are in the safe starting area (p1-1, p2-1, p1-2)
    
    Args:
        positions: list of available positions (already excluding safe area)
        num_wumpus: number of wumpuses to place (1 or 2)
        num_pits: number of pits to place (0 or 1)
    
    Returns:
        tuple: (pit_pos, wumpus_positions, gold_pos)
                pit_pos is None if num_pits is 0
    """
    # Randomly select positions for pit (if any), wumpus(es), and gold
    # All must be different positions
    sample_size = num_pits + num_wumpus + 1  # pits + wumpuses + gold
    
    if len(positions) < sample_size:
        raise ValueError(f"Not enough positions available. Need {sample_size}, have {len(positions)}")
    
    selected = random.sample(positions, sample_size)
    
    if num_pits == 1:
        pit_pos = selected[0]
        wumpus_positions = selected[1:1+num_wumpus]
        gold_pos = selected[-1]
    else:  # num_pits == 0
        pit_pos = None
        wumpus_positions = selected[0:num_wumpus]
        gold_pos = selected[-1]
    
    return pit_pos, wumpus_positions, gold_pos


def format_hidden_clause(pit_pos, wumpus_positions, gold_pos):
    """Format a single :hidden clause. pit_pos can be None if no pit."""
    elements = []
    
    # Build list of items to include
    items = [("gold-at", gold_pos)]
    
    if pit_pos is not None:
        items.append(("pit-at", pit_pos))
    
    items.extend([("wumpus-at", wpos) for wpos in wumpus_positions])
    
    # Randomly shuffle the order
    random.shuffle(items)
    
    # Format each element
    for predicate, pos in items:
        elements.append(f"({predicate} {pos})")
    
    return "    (:hidden " + " ".join(elements) + ")"


def generate_h_pddl(problem_name, positions, num_wumpus, num_scenarios, num_pits=1, seed=None):
    """
    Generate the complete h.pddl file.
    
    Args:
        problem_name: name of the problem from p.pddl
        positions: list of available positions
        num_wumpus: number of wumpuses (1 or 2)
        num_scenarios: number of scenarios to generate
        num_pits: number of pits (0 or 1)
        seed: random seed (optional)
    """
    if seed is not None:
        random.seed(seed)
    
    # Generate header
    lines = [f"(define (problem {problem_name})"]
    
    # Generate scenarios
    for _ in range(num_scenarios):
        pit_pos, wumpus_positions, gold_pos = generate_scenario(positions, num_wumpus, num_pits)
        hidden_clause = format_hidden_clause(pit_pos, wumpus_positions, gold_pos)
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
        num_scenarios = int(sys.argv[3]) if len(sys.argv) > 3 else 100
        num_pits = int(sys.argv[4]) if len(sys.argv) > 4 else 1
        seed = int(sys.argv[5]) if len(sys.argv) > 5 else None
        
        if num_wumpus not in [1, 2]:
            print("Error: Number of wumpuses must be 1 or 2")
            sys.exit(1)
        
        if num_scenarios < 1:
            print("Error: Number of scenarios must be at least 1")
            sys.exit(1)
        
        if num_pits not in [0, 1]:
            print("Error: Number of pits must be 0 or 1")
            sys.exit(1)
        
        # Parse positions from p.pddl file
        problem_name, positions = parse_positions_from_pddl(pddl_path)
        
        print(f"# Parsed {len(positions)} positions from {pddl_path}", file=sys.stderr)
        print(f"# Problem name: {problem_name}", file=sys.stderr)
        print(f"# Generating {num_scenarios} scenarios with {num_wumpus} wumpus(es) and {num_pits} pit(s)", file=sys.stderr)
        
        # Generate and print the h.pddl content
        content = generate_h_pddl(problem_name, positions, num_wumpus, num_scenarios, num_pits, seed)
        print(content)
        
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
