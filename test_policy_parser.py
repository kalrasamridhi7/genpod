
from genfond.parse_rule_policy import PolicyParser, parse_policy_file
from pddl import parse_domain, parse_problem
from genfond.translate_domain import K_Translator
from pddl.formatter import domain_to_string, problem_to_string
from genfond.execute_rule_policy import execute_rule_policy
from genfond.config_handler import DEFAULT_CONFIG

import logging

logging.basicConfig(level=logging.DEBUG, filename="execution_rule.log", filemode="w", force=True)
logger = logging.getLogger('test_policy_parser')

def main():
    #get translated domain and problems
    logger.info("test_policy_parser executed as script")
    domain = parse_domain("domains/partially-observable-deterministic/wumpus/d_no_pit.pddl")
    problem1 = parse_problem("domains/partially-observable-deterministic/wumpus/p5x5_no_pit.pddl")
    k_translator = K_Translator(domain, [problem1])
    translated_domain = k_translator.translated_domain
    #print(domain_to_string(translated_domain))
    translated_problems = k_translator.translated_problems
    # Parse from file
    policy = parse_policy_file("wumpus.policy")

    # Or parse from string
    #parser = PolicyParser()
    #policy = parser.parse_string(policy_content)

    #print(policy)  # Uses the __repr__ method from the Policy class
    for i in range(50):
        execute_rule_policy(translated_domain, translated_problems[0], policy, DEFAULT_CONFIG)

    return 0


if __name__ == "__main__":
    main()