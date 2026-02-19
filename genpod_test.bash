#!/bin/bash
#
#SBATCH --partition=rleap_gpu_24gb
#SBATCH --cpus-per-task=32
#SBATCH --mem=64000
#SBATCH --time=2-00
#SBATCH --output=/u/samridhi.kalra/master_thesis/genpod/logs/jobs/genpod-%j.out

echo "Running: $@"
cd /u/samridhi.kalra/master_thesis/genpod/
source /u/samridhi.kalra/.cache/pypoetry/virtualenvs/genfond-yn4YVXNL-py3.10/bin/activate
#python -m genfond -v  domains/partially-observable-deterministic/wumpus/{d_no_pit.pddl,p2x3_no_pit.pddl} -o wumpus.pickle -l output_wumpus2x3_test.log

#python -m genfond  domains/partially-observable-deterministic/colorballs/{d2.pddl,p2-2_d2.pddl,p3-2_d2.pddl} -o output_policies/colorballs2-2.pickle -l logs/output/output_colorballs2-2_test.log --min-complexity 5 --max-complexity 20 --train-set domains/partially-observable-deterministic/colorballs/{p2-2_hidden.pddl,p3-2_hidden.pddl} --test-set domains/partially-observable-deterministic/colorballs/{p2-2_test.pddl,p3-2_test.pddl}

python -m genfond domains/partially-observable-deterministic/wumpus/d.pddl domains/partially-observable-deterministic/wumpus/{p2x3_no_pit.pddl,p3/p3_no_pit.pddl} -o output_policies/wumpus_new_lp.pickle -l logs/output/output_wumpus_new_lp.log --min-complexity 10 --max-complexity 25 --train-set domains/partially-observable-deterministic/wumpus/{p2x3_no_pit_hidden.pddl,p3/p3_no_pit_hidden.pddl} --test-set domains/partially-observable-deterministic/wumpus/{p2x3_no_pit_hidden.pddl,p3/p3_no_pit_test.pddl}

#python -m genfond domains/partially-observable-deterministic/doors/{d.pddl,p2x5.pddl,p5x3.pddl} -o doors5x3.pickle -l output2_doors_test.log --train-set domains/partially-observable-deterministic/doors/{p2x5_hidden.pddl,p5x3_hidden.pddl} --test-set domains/partially-observable-deterministic/doors/{p2x5_test.pddl,p5x3_test.pddl} --min-complexity 10 --max-complexity 20 --one-shot
