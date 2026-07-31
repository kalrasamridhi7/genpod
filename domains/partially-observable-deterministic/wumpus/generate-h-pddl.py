#!/usr/bin/env python3
"""
Generate master h.pddl file for wumpus problems with hidden state scenarios.

Constraints enforced:
- Pit, wumpus(es), and gold must all be at different positions
- Pits and wumpuses cannot be at safe starting positions: p1-1, p2-1, p1-2
- Gold can be at any position (including safe positions)
- Each scenario has 0 or 1 pit, N wumpuses (1 or 2), and 1 gold

Usage: python3 generate-h-pddl.py <p_pddl_path> <num_wumpus> <num_scenarios> [num_pits] [seed]
  p_pddl_path: path to the p.pddl file (e.g., p05-1f/p.pddl)
  num_wumpus: number of wumpuses (1 or 2, based on problem variant -1f or -2f)
  num_scenarios: number of scenarios to generate
                 Use 'all' to generate all unique combinations
                 Use a number for random sampling (default: 100)
  num_pits: number of pits (0 or 1, default: 1)
  seed: random seed for reproducibility (optional, only used for random sampling)

Example: python3 generate-h-pddl.py p05-1f/p.pddl 1 all 1
         This generates ALL unique scenarios from p05-1f/p.pddl with 1 wumpus and 1 pit
Example: python3 generate-h-pddl.py p05-1f/p.pddl 1 100 1 42
         This generates 100 random scenarios with 1 wumpus, 1 pit, using seed 42
Example: python3 generate-h-pddl.py p05-1f/p.pddl 2 all 0
         This generates all unique scenarios with 2 wumpuses and 0 pits
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
    
    if not positions:
        raise ValueError(f"No positions found in {pddl_path}")
    
    if not problem_name:
        raise ValueError(f"No problem name found in {pddl_path}")
    
    # Define safe starting area: p1-1, p2-1, p1-2
    # These positions should never have pits or wumpuses (but gold can be there)
    safe_positions = {'p1-1', 'p2-1', 'p1-2'}
    
    return problem_name, positions, safe_positions


def generate_scenario(positions, safe_positions, num_wumpus, num_pits=1):
    """
    Generate a single hidden state scenario.
    
    Ensures that:
    - Pit, wumpus(es), and gold are all at different positions
    - Pit and wumpuses are NOT in the safe starting area (p1-1, p2-1, p1-2)
    - Gold CAN be in any position (including safe area)
    
    Args:
        positions: list of all available positions
        safe_positions: set of safe positions where pit/wumpus cannot be placed
        num_wumpus: number of wumpuses to place (1 or 2)
        num_pits: number of pits to place (0 or 1)
    
    Returns:
        tuple: (pit_pos, wumpus_positions, gold_pos)
                pit_pos is None if num_pits is 0
    """
    # Filter positions for pit and wumpus (exclude safe positions)
    non_safe_positions = [p for p in positions if p not in safe_positions]
    
    # Randomly select positions for pit (if any) and wumpus(es) from non-safe positions
    sample_size = num_pits + num_wumpus
    
    if len(non_safe_positions) < sample_size:
        raise ValueError(f"Not enough non-safe positions available. Need {sample_size}, have {len(non_safe_positions)}")
    
    selected_hazards = random.sample(non_safe_positions, sample_size)
    
    if num_pits == 1:
        pit_pos = selected_hazards[0]
        wumpus_positions = selected_hazards[1:1+num_wumpus]
    else:  # num_pits == 0
        pit_pos = None
        wumpus_positions = selected_hazards[0:num_wumpus]
    
    # Select gold position from all positions, excluding where pit/wumpus already are
    occupied_positions = set(wumpus_positions)
    if pit_pos is not None:
        occupied_positions.add(pit_pos)
    
    available_for_gold = [p for p in positions if p not in occupied_positions]
    gold_pos = random.choice(available_for_gold)
    
    return pit_pos, wumpus_positions, gold_pos


def generate_all_scenarios(positions, safe_positions, num_wumpus, num_pits=1):
    """
    Generate all possible unique hidden state scenarios.
    
    Args:
        positions: list of all available positions
        safe_positions: set of safe positions where pit/wumpus cannot be placed
        num_wumpus: number of wumpuses to place (1 or 2)
        num_pits: number of pits to place (0 or 1)
    
    Returns:
        list of tuples: [(pit_pos, wumpus_positions, gold_pos), ...]
    """
    scenarios = []
    non_safe_positions = [p for p in positions if p not in safe_positions]
    
    if num_pits == 1:
        # For each pit position
        for pit_pos in non_safe_positions:
            # Get remaining non-safe positions for wumpus
            remaining_for_wumpus = [p for p in non_safe_positions if p != pit_pos]
            
            # For each combination of wumpus positions
            for wumpus_combo in combinations(remaining_for_wumpus, num_wumpus):
                wumpus_positions = list(wumpus_combo)
                
                # Get available positions for gold (all positions except pit and wumpuses)
                occupied = set(wumpus_positions) | {pit_pos}
                available_for_gold = [p for p in positions if p not in occupied]
                
                # For each gold position
                for gold_pos in available_for_gold:
                    scenarios.append((pit_pos, wumpus_positions, gold_pos))
    
    else:  # num_pits == 0
        # For each combination of wumpus positions
        for wumpus_combo in combinations(non_safe_positions, num_wumpus):
            wumpus_positions = list(wumpus_combo)
            
            # Get available positions for gold (all positions except wumpuses)
            occupied = set(wumpus_positions)
            available_for_gold = [p for p in positions if p not in occupied]
            
            # For each gold position
            for gold_pos in available_for_gold:
                scenarios.append((None, wumpus_positions, gold_pos))
    
    return scenarios


def format_hidden_clause(pit_pos, wumpus_positions, gold_pos, randomize_order=True):
    """Format a single :hidden clause. pit_pos can be None if no pit."""
    elements = []
    
    # Build list of items to include
    items = [("gold-at", gold_pos)]
    
    if pit_pos is not None:
        items.append(("pit-at", pit_pos))
    
    items.extend([("wumpus-at", wpos) for wpos in wumpus_positions])
    
    # Randomly shuffle the order (only for random mode)
    if randomize_order:
        random.shuffle(items)
    
    # Format each element
    for predicate, pos in items:
        elements.append(f"({predicate} {pos})")
    
    return "    (:hidden " + " ".join(elements) + ")"


def generate_h_pddl(problem_name, positions, safe_positions, num_wumpus, num_scenarios, num_pits=1, seed=None):
    """
    Generate the complete h.pddl file.
    
    Args:
        problem_name: name of the problem from p.pddl
        positions: list of all available positions
        safe_positions: set of safe positions where pit/wumpus cannot be placed
        num_wumpus: number of wumpuses (1 or 2)
        num_scenarios: number of scenarios to generate, or 'all' for all unique combinations
        num_pits: number of pits (0 or 1)
        seed: random seed (optional, only used for random sampling)
    """
    # Generate header
    lines = [f"(define (problem {problem_name})"]
    
    if num_scenarios == 'all':
        # Generate all unique combinations
        all_scenarios = generate_all_scenarios(positions, safe_positions, num_wumpus, num_pits)
        for pit_pos, wumpus_positions, gold_pos in all_scenarios:
            hidden_clause = format_hidden_clause(pit_pos, wumpus_positions, gold_pos, randomize_order=False)
            lines.append(hidden_clause)
    else:
        # Random sampling mode
        if seed is not None:
            random.seed(seed)
        
        # Generate random scenarios
        for _ in range(num_scenarios):
            pit_pos, wumpus_positions, gold_pos = generate_scenario(positions, safe_positions, num_wumpus, num_pits)
            hidden_clause = format_hidden_clause(pit_pos, wumpus_positions, gold_pos, randomize_order=True)
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
        
        num_pits = int(sys.argv[4]) if len(sys.argv) > 4 else 1
        seed = int(sys.argv[5]) if len(sys.argv) > 5 else None
        
        if num_wumpus not in [1, 2]:
            print("Error: Number of wumpuses must be 1 or 2")
            sys.exit(1)
        
        if num_pits not in [0, 1]:
            print("Error: Number of pits must be 0 or 1")
            sys.exit(1)
        
        # Parse positions from p.pddl file
        problem_name, positions, safe_positions = parse_positions_from_pddl(pddl_path)
        
        print(f"# Parsed {len(positions)} positions from {pddl_path}", file=sys.stderr)
        print(f"# Problem name: {problem_name}", file=sys.stderr)
        print(f"# Safe positions (pit/wumpus excluded, gold allowed): {safe_positions}", file=sys.stderr)
        
        if num_scenarios == 'all':
            # Calculate expected number of scenarios
            non_safe_count = len([p for p in positions if p not in safe_positions])
            if num_pits == 1:
                if num_wumpus == 1:
                    # pit choices * wumpus choices * gold choices
                    # = N * (N-1) * (P - 2) where N=non-safe, P=all positions
                    expected = non_safe_count * (non_safe_count - 1) * (len(positions) - 2)
                else:  # num_wumpus == 2
                    # pit choices * C(N-1, 2) * gold choices
                    # = N * C(N-1,2) * (P - 3)
                    from math import comb
                    expected = non_safe_count * comb(non_safe_count - 1, 2) * (len(positions) - 3)
            else:  # num_pits == 0
                if num_wumpus == 1:
                    # wumpus choices * gold choices = N * (P - 1)
                    expected = non_safe_count * (len(positions) - 1)
                else:  # num_wumpus == 2
                    # C(N, 2) * gold choices = C(N,2) * (P - 2)
                    from math import comb
                    expected = comb(non_safe_count, 2) * (len(positions) - 2)
            
            print(f"# Generating ALL unique scenarios ({expected} expected) with {num_wumpus} wumpus(es) and {num_pits} pit(s)", file=sys.stderr)
        else:
            print(f"# Generating {num_scenarios} random scenarios with {num_wumpus} wumpus(es) and {num_pits} pit(s)", file=sys.stderr)
        
        # Generate and print the h.pddl content
        content = generate_h_pddl(problem_name, positions, safe_positions, num_wumpus, num_scenarios, num_pits, seed)
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
