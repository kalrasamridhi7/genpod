#!/usr/bin/env python3
"""
Generate hidden-state clauses for the lightbulbs domain.

Usage:
  python3 generate-light-hidden.py <p_pddl_path> <num_scenarios|'all'> [seed]

Examples:
  python3 generate-light-hidden.py p2.pddl all
  python3 generate-light-hidden.py p5.pddl 100 42

Output format:
  (define (problem <name>)
      (:hidden (light-on r11) (not (light-on r12)) ...)
      ...
  )
"""

import random
import re
import sys
from itertools import product


def parse_rooms_from_pddl(pddl_path):
    with open(pddl_path, "r", encoding="utf-8") as f:
        content = f.read()

    name_match = re.search(r"\(define\s+\(problem\s+(\S+)\)", content)
    if not name_match:
        raise ValueError(f"No problem name found in {pddl_path}")
    problem_name = name_match.group(1)

    objects_match = re.search(r":objects\s+(.*?)\s+-\s*room", content, re.DOTALL)
    if not objects_match:
        raise ValueError(f"No :objects section with room type found in {pddl_path}")

    objects_text = objects_match.group(1)
    rooms = re.findall(r"\b([A-Za-z0-9_-]+)\b", objects_text)
    if not rooms:
        raise ValueError(f"No room objects parsed from {pddl_path}")

    return problem_name, rooms


def format_hidden_clause(bits, rooms):
    parts = []
    for room, bit in zip(rooms, bits):
        if bit:
            parts.append(f"(light-on {room})")
        else:
            parts.append(f"(not (light-on {room}))")
    return "    (:hidden " + " ".join(parts) + ")"


def generate_all(rooms):
    for bits in product([0, 1], repeat=len(rooms)):
        yield format_hidden_clause(bits, rooms)


def generate_random(rooms, count, seed=None):
    total = 1 << len(rooms)
    if count >= total:
        yield from generate_all(rooms)
        return

    if seed is not None:
        random.seed(seed)

    seen = set()
    while len(seen) < count:
        idx = random.randrange(total)
        if idx in seen:
            continue
        seen.add(idx)
        bits = [(idx >> shift) & 1 for shift in range(len(rooms) - 1, -1, -1)]
        yield format_hidden_clause(bits, rooms)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    pddl_path = sys.argv[1]
    num_arg = sys.argv[2]
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else None

    problem_name, rooms = parse_rooms_from_pddl(pddl_path)

    if num_arg.lower() == "all":
        clauses = list(generate_all(rooms))
    else:
        try:
            count = int(num_arg)
        except ValueError:
            print("Second argument must be an integer or 'all'", file=sys.stderr)
            sys.exit(1)
        clauses = list(generate_random(rooms, count, seed))

    print(f"(define (problem {problem_name})")
    for clause in clauses:
        print(clause)
    print(")")


if __name__ == "__main__":
    main()