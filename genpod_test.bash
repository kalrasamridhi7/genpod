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


#python -m genfond  domains/partially-observable-deterministic/colorballs/{d.pddl,p2-1.pddl,p2x3-1.pddl,p3-1.pddl,p5-1.pddl} -o output_policies/colorballs2-1.pickle -l logs/output/output_colorballs2-1_test.log --min-complexity 6 --max-complexity 20 --train-set domains/partially-observable-deterministic/colorballs/{p3-1_hidden.pddl,p5-1_hidden.pddl} --test-set domains/partially-observable-deterministic/colorballs/{p2-1_test.pddl,p3-1_test.pddl}

#python -m genfond domains/partially-observable-deterministic/wumpus/d_no_pit.pddl domains/partially-observable-deterministic/wumpus/p2x3_no_pit.pddl -o output_policies/wumpus_new_lp.pickle -l logs/output/output_wumpus_new_lp.log --min-complexity 10 --max-complexity 25 --train-set domains/partially-observable-deterministic/wumpus/p3/p3_no_pit_hidden.pddl --test-set domains/partially-observable-deterministic/wumpus/{p2x3_no_pit_hidden.pddl,p3/p3_no_pit_test.pddl}

#python -m genfond -v domains/partially-observable-deterministic/doors/{d.pddl,p2x5.pddl,p5x3.pddl} -o doors5x3_local.pickle -l output2_doors_test_local.log --train-set domains/partially-observable-deterministic/doors/{p2x5_hidden.pddl,p5x3_hidden.pddl} --test-set domains/partially-observable-deterministic/doors/{p2x5_test.pddl,p5x3_test.pddl} --min-complexity 10 --max-complexity 30 --one-shot

python -m genfond  domains/partially-observable-deterministic/binary-search/{d.pddl,p05.pddl,p10} -o output_policies/binary_search.pickle -l logs/output/output_binary_search.log --min-complexity 6 --max-complexity 20 --train-set domains/partially-observable-deterministic/binary-search/{p05_hidden.pddl,p10_hidden.pddl} --test-set domains/partially-observable-deterministic/binary-search/{p05_test.pddl,p10_test.pddl}
