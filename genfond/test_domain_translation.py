import logging
from lark import logger
from pddl import parse_domain, parse_problem
from pddl.formatter import domain_to_string, problem_to_string

from genfond.util import parse_hidden_state_predicates
from .state_space_generator import generate_state_space
from .ground import ground_sensing_models, ground_domain_predicates, ground
from .translate_domain import K_Translator
    
logger = logging.getLogger('genfond.test_domain_translation')
logging.basicConfig(level=logging.DEBUG, filename='output1.log', filemode='w')

def main():
    logger.info("test_domain_translation executed as script")
    domain = parse_domain("domains/partially-observable-deterministic/colorballs/d.pddl")
    #domain = parse_domain("domains/partially-observable-deterministic/wumpus/d_no_pit.pddl")
    #logger.info(domain_to_string(domain))
    problem = parse_problem("domains/partially-observable-deterministic/colorballs/p2x3.pddl")

    logger.debug("actions for first problem: {}".format(domain.actions))
    #problem = parse_problem("domains/partially-observable-deterministic/wumpus/p2x3_no_pit.pddl")
    #hidden_predicates = parse_hidden_state_predicates(["domains/partially-observable-deterministic/wumpus/p3/p3_hidden_no_pit.pddl"])
    hidden_predicates = None
    k_translator = K_Translator(domain, [problem], hidden_predicates)
    translated_domain = k_translator.translated_domain
    translated_problem = k_translator.translated_problems[0]
    #logger.info(problem_to_string(translated_problem))
    graph = generate_state_space(translated_domain, translated_problem)
    logger.info(f"Generated state space with {len(graph.nodes)} nodes")
    return 0


if __name__ == "__main__":
    main()