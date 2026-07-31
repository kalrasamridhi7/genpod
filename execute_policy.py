import argparse
import logging
import pickle

import pddl

from genpod.config_handler import ConfigHandler
from genpod.datalog_policy import DatalogPolicy
from genpod.execute_policy import execute_policy
from genpod.translate_domain import K_Translator
from genpod.util import parse_hidden_state_predicates

logging.basicConfig(format="%(asctime)s %(levelname)-8s %(message)s", level=logging.DEBUG, filename="execute_policy_new.log", filemode="w")
log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("domain", help="domain file")
    parser.add_argument("problem", help="problem file")
    parser.add_argument("policy", help="policy file")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose output")
    parser.add_argument("--config", type=argparse.FileType("r"), help="config file")
    parser.add_argument("--test-set", help="test set for the problems", nargs="*")
    parser.add_argument("-i", "--policy-iterations", help="number of policy iterations", type=int, default=1)
    args = parser.parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    with open(args.policy, "rb") as f:
        policy = pickle.load(f)
    type = "datalog" if isinstance(policy, DatalogPolicy) else "rule"
    config = ConfigHandler(args.config, type, vars(args))
    domain = pddl.parse_domain(args.domain)
    problem = pddl.parse_problem(args.problem)
    hidden_predicates = parse_hidden_state_predicates(args.test_set) if args.test_set else None
    k_translator = K_Translator(domain, [problem], hidden_predicates)
    domain = k_translator.translated_domain
    problem = k_translator.translated_problems[0]
    for i in range(args.policy_iterations):
        execute_policy(domain, problem, policy, config)


if __name__ == "__main__":
    main()
