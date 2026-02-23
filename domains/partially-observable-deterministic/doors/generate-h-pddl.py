import re
import itertools
import random
from pathlib import Path

def parse_pddl_problem(problem_file):
    """Parse PDDL problem file to extract grid size and positions."""
    with open(problem_file, 'r') as f:
        content = f.read()
    
    # Extract problem name
    problem_match = re.search(r'\(define\s+\(problem\s+(\w+)\)', content)
    problem_name = problem_match.group(1) if problem_match else "doors"
    
    # Extract all position objects (e.g., p1-1, p2-3, etc.)
    objects_match = re.search(r':objects\s+(.*?)\s*-\s*pos', content, re.DOTALL)
    if not objects_match:
        raise ValueError("Could not find position objects in problem file")
    
    positions = objects_match.group(1).split()
    
    # Find max column number to determine grid size
    max_col = 0
    for pos in positions:
        match = re.match(r'p(\d+)-(\d+)', pos)
        if match:
            col = int(match.group(1))
            max_col = max(max_col, col)
    
    return problem_name, max_col, positions

def get_even_column_positions(max_col, positions):
    """Get positions for each even column (p2-*, p4-*, p6-*, ...)."""
    even_cols = {}
    
    for col in range(2, max_col + 1, 2):
        col_positions = [pos for pos in positions if pos.startswith(f'p{col}-')]
        if col_positions:
            even_cols[col] = sorted(col_positions)
    
    return even_cols

def generate_random_combinations(even_cols, num_combinations):
    """Generate random combinations of one open door per even column."""
    # Get list of positions for each column
    col_lists = [even_cols[col] for col in sorted(even_cols.keys())]
    
    # Calculate total possible combinations
    total_possible = 1
    for col_list in col_lists:
        total_possible *= len(col_list)
    
    # If requested more than possible, generate all combinations
    if num_combinations >= total_possible:
        print(f"Requested {num_combinations} combinations, but only {total_possible} possible.")
        print(f"Generating all {total_possible} combinations.")
        all_combos = []
        for combo in itertools.product(*col_lists):
            selected = list(combo)
            not_selected = []
            for col_list in col_lists:
                not_selected.extend([pos for pos in col_list if pos not in selected])
            all_combos.append((selected, not_selected))
        return all_combos
    
    # Generate random unique combinations with non-selected positions
    combinations = []
    seen_combos = set()
    
    while len(combinations) < num_combinations:
        selected = []
        not_selected = []
        
        for col_list in col_lists:
            chosen = random.choice(col_list)
            selected.append(chosen)
            # Track positions that were not selected from this column
            not_selected.extend([pos for pos in col_list if pos != chosen])
        
        combo_tuple = tuple(selected)
        if combo_tuple not in seen_combos:
            seen_combos.add(combo_tuple)
            combinations.append((selected, not_selected))
    
    return combinations

def write_hidden_file(problem_name, combinations, output_file):
    """Write hidden PDDL file with door combinations."""
    with open(output_file, 'w') as f:
        f.write(f"(define (problem {problem_name})\n")
        
        for selected, not_selected in combinations:
            # Write one :hidden clause per combination
            # Include opened doors and negated formulas for non-opened doors
            formulas = []
            
            # Add opened doors
            for pos in selected:
                formulas.append(f"(opened {pos})")
            
            # Add (not (opened pos)) for all non-selected doors
            for pos in not_selected:
                formulas.append(f"(not (opened {pos}))")
            
            hidden_str = " ".join(formulas)
            f.write(f"    (:hidden {hidden_str})\n")
        
        f.write(")\n")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python generate-h-pddl.py <problem_file> [num_combinations] [output_file]")
        print("Example: python generate-h-pddl.py p5.pddl 10 p5_hidden.pddl")
        print("         python generate-h-pddl.py p5.pddl 10")
        sys.exit(1)
    
    problem_file = sys.argv[1]
    
    # Get number of combinations (default to 25 if not specified)
    if len(sys.argv) >= 3:
        try:
            num_combinations = int(sys.argv[2])
            if num_combinations <= 0:
                print("Error: Number of combinations must be positive")
                sys.exit(1)
        except ValueError:
            print("Error: Number of combinations must be an integer")
            sys.exit(1)
    else:
        num_combinations = 25
    
    # Generate output filename if not provided
    if len(sys.argv) >= 4:
        output_file = sys.argv[3]
    else:
        base_name = Path(problem_file).stem
        output_file = f"{base_name}_hidden.pddl"
    
    # Parse problem file
    print(f"Reading problem file: {problem_file}")
    problem_name, max_col, positions = parse_pddl_problem(problem_file)
    print(f"Problem: {problem_name}, Grid size: {max_col}x{max_col}")
    
    # Get even column positions
    even_cols = get_even_column_positions(max_col, positions)
    print(f"Even columns found: {sorted(even_cols.keys())}")
    for col, pos_list in sorted(even_cols.items()):
        print(f"  Column {col}: {len(pos_list)} positions")
    
    # Calculate total possible combinations
    total_possible = 1
    for col_list in even_cols.values():
        total_possible *= len(col_list)
    print(f"Total possible combinations: {total_possible}")
    
    # Generate combinations
    print(f"\nGenerating {num_combinations} random combinations...")
    combinations = generate_random_combinations(even_cols, num_combinations)
    print(f"Generated {len(combinations)} combinations")
    
    # Write output file
    write_hidden_file(problem_name, combinations, output_file)
    print(f"Hidden file written to: {output_file}")

if __name__ == "__main__":
    main()