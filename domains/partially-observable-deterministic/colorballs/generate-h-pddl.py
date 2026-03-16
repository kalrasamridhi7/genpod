import sys
import re
import random

#!/usr/bin/env python3

"""
Generate master h.pddl file for colorballs problems with random hidden state scenarios.

Constraints enforced:
- Each ball must be at exactly one position
- Each ball must have exactly one color
- Positions and colors are chosen randomly for each scenario

Usage: python3 generate-h-pddl.py <p_pddl_path> <num_scenarios> [seed]
    p_pddl_path: path to the p.pddl file (e.g., p3-1.pddl)
    num_scenarios: number of hidden state scenarios to generate (default: 100)
    seed: random seed for reproducibility (optional)

Example: python3 generate-h-pddl.py p3-1.pddl 100
                 This generates 100 scenarios using objects from p3-1.pddl
Example: python3 generate-h-pddl.py p3-1.pddl 100 42
                 This generates 100 scenarios using seed 42
"""



def parse_objects_from_pddl(pddl_path):
        """
        Parse objects (balls, positions, colors) from the p.pddl file.
        
        Args:
                pddl_path: path to the p.pddl file
        
        Returns:
                tuple: (problem_name, balls, positions, colors)
        """
        balls = []
        positions = []
        colors = []
        problem_name = None
        
        with open(pddl_path, 'r') as f:
                content = f.read()
        
        # Extract problem name
        problem_match = re.search(r'\(define\s+\(problem\s+(\S+)\)', content)
        if problem_match:
                problem_name = problem_match.group(1)
        
        # Extract objects from :objects section
        objects_section = re.search(r':objects\s+(.*?)\)', content, re.DOTALL)
        if objects_section:
                objects_text = objects_section.group(1)
                
                # Find balls (format: ball1, ball2, etc. - obj)
                ball_matches = re.findall(r'(o\d+)', objects_text)
                balls = ball_matches
                
                # Find positions (format: pos1, pos2, etc. - pos)
                pos_matches = re.findall(r'(p\d+-\d+)', objects_text)
                positions = pos_matches
                
                # Find colors (format: red blue green - col)
                # Match the entire line ending with "- col" and extract all words before it
                col_line_match = re.search(r'\n([\w\s]+)\s+-\s+col', objects_text)
                if col_line_match:
                        col_words = col_line_match.group(1).strip().split()
                        colors = col_words
        
        if not balls:
                raise ValueError(f"No balls found in {pddl_path}")
        if not positions:
                raise ValueError(f"No positions found in {pddl_path}")
        if not colors:
                raise ValueError(f"No colors found in {pddl_path}")
        if not problem_name:
                raise ValueError(f"No problem name found in {pddl_path}")
        
        return problem_name, balls, positions, colors


def generate_scenario(balls, positions, colors):
        """
        Generate a single hidden state scenario.
        
        For each ball, randomly assign a position and a color.
        
        Args:
                balls: list of ball objects
                positions: list of available positions
                colors: list of available colors
        
        Returns:
                list of tuples: [(ball, position, color), ...]
        """
        scenario = []
        for ball in balls:
                pos = random.choice(positions)
                col = random.choice(colors)
                scenario.append((ball, pos, col))
        
        return scenario


def format_hidden_clause(scenario):
        """
        Format a single :hidden clause.
        
        Args:
                scenario: list of (ball, position, color) tuples
        
        Returns:
                formatted string for the :hidden clause
        """
        elements = []
        
        for ball, pos, col in scenario:
                elements.append(f"(obj-at {ball} {pos})")
                elements.append(f"(color {ball} {col})")
        
        # Randomly shuffle the order
        random.shuffle(elements)
        
        return "    (:hidden " + " ".join(elements) + ")"


def generate_h_pddl(problem_name, balls, positions, colors, num_scenarios, seed=None):
        """
        Generate the complete h.pddl file with unique scenarios.
        
        Args:
                problem_name: name of the problem from p.pddl
                balls: list of ball objects
                positions: list of available positions
                colors: list of available colors
                num_scenarios: number of unique scenarios to generate
                seed: random seed (optional)
        """
        if seed is not None:
                random.seed(seed)
        
        # Calculate maximum possible unique scenarios
        max_possible = (len(positions) * len(colors)) ** len(balls)
        
        if num_scenarios > max_possible:
                print(f"# Warning: Requested {num_scenarios} scenarios but only {max_possible} unique scenarios possible.", file=sys.stderr)
                print(f"# Generating all {max_possible} possible scenarios instead.", file=sys.stderr)
                num_scenarios = max_possible
        
        # Generate header
        lines = [f"(define (problem {problem_name})"]
        
        # Generate unique scenarios
        seen_scenarios = set()
        attempts = 0
        max_attempts = num_scenarios * 1000  # Prevent infinite loops
        
        while len(seen_scenarios) < num_scenarios and attempts < max_attempts:
                attempts += 1
                scenario = generate_scenario(balls, positions, colors)
                
                # Convert to hashable tuple for uniqueness check
                scenario_tuple = tuple(sorted(scenario))
                
                if scenario_tuple not in seen_scenarios:
                        seen_scenarios.add(scenario_tuple)
                        hidden_clause = format_hidden_clause(scenario)
                        lines.append(hidden_clause)
        
        if len(seen_scenarios) < num_scenarios:
                print(f"# Warning: Could only generate {len(seen_scenarios)} unique scenarios out of {num_scenarios} requested.", file=sys.stderr)
        
        # Add closing parenthesis
        lines.append(")")
        
        return "\n".join(lines)


def main():
        if len(sys.argv) < 2:
                print(__doc__)
                sys.exit(1)
        
        try:
                pddl_path = sys.argv[1]
                num_scenarios = int(sys.argv[2]) if len(sys.argv) > 2 else 100
                seed = int(sys.argv[3]) if len(sys.argv) > 3 else None
                
                if num_scenarios < 1:
                        print("Error: Number of scenarios must be at least 1")
                        sys.exit(1)
                
                # Parse objects from p.pddl file
                problem_name, balls, positions, colors = parse_objects_from_pddl(pddl_path)
                
                print(f"# Parsed from {pddl_path}:", file=sys.stderr)
                print(f"#   {len(balls)} balls: {balls}", file=sys.stderr)
                print(f"#   {len(positions)} positions: {positions}", file=sys.stderr)
                print(f"#   {len(colors)} colors: {colors}", file=sys.stderr)
                print(f"# Problem name: {problem_name}", file=sys.stderr)
                print(f"# Generating {num_scenarios} scenarios", file=sys.stderr)
                
                # Generate and print the h.pddl content
                content = generate_h_pddl(problem_name, balls, positions, colors, num_scenarios, seed)
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
