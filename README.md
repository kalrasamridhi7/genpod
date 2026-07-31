# Generalized FOND Planning

## Installation

### Installing in a virtualenv

You can install all dependencies in a virtualenv managed by `poetry`:


1. Install `poetry`:
   ```
   pip install --user poetry
   ```
1. Install dependencies:
   ```
   poetry install --no-root
   ```
1. Activate a virtualenv shell (you will need to redo this every time you open a new terminal):
   ```
   poetry shell
   ```

You can then run benchmarks for respective pddl domains with:
```
python -m genpod  domains/partially-observable-deterministic/localize/{d.pddl,p3.pddl,p5.pddl,p7.pddl} -o output/localize.pickle -l output_localize.log  --train-set domains/partially-observable-deterministic/localize/{p3_hidden.pddl,p5_hidden.pddl,p7_hidden.pddl} --test-set domains/partially-observable-deterministic/localize/{p3_test.pddl,p5_test.pddl,p7_test.pddl} --stats localize.stat

```

## Executing a policy

After learning a policy and writing it to a file (by writing a policy file with `--output <policyfile>`, both for the main solver and `genpod_oneshot.py`), you can execute the policy with `execute_policy.py`, e.g.,:
```
python execute_policy.py domains/non-deterministic/acrobatics/{domain.pddl,p0005.pddl} acrobatics.policy
```

# Copyright

All rights reserved by the authors.

Upon publication, this project will be made publicly available and licensed under an open-source license.
