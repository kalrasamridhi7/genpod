import logging
from lark import logger
from pddl import parse_domain, parse_problem
from pddl.formatter import domain_to_string, problem_to_string
from .state_space_generator import generate_state_space
from .ground import ground_sensing_models, ground_domain_predicates, ground
from .translate_domain import K_Translator
    
logger = logging.getLogger('genfond.test_domain_translation')
#logging.basicConfig(level=logging.DEBUG, filename='output.log', filemode='w')

def main():
    logger.info("test_domain_translation executed as script")
    domain = parse_domain("domains/partially-observable-deterministic/colorballs/d.pddl")
    #domain = parse_domain("domains/partially-observable-deterministic/wumpus/d_no_pit.pddl")
    #logger.info(domain_to_string(domain))
    problem = parse_problem("domains/partially-observable-deterministic/colorballs/p2-1.pddl")
    #problem = parse_problem("domains/partially-observable-deterministic/wumpus/p.pddl")
    k_translator = K_Translator(domain, [problem])
    translated_domain = k_translator.translated_domain
    translated_problem = k_translator.translated_problems[0]
    #logger.info(problem_to_string(translated_problem))
    graph = generate_state_space(translated_domain, translated_problem)
    logger.info(f"Generated state space with {len(graph.nodes)} nodes")
    return 0


if __name__ == "__main__":
    main()