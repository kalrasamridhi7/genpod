#!/bin/bash
#
#SBATCH --partition=rleap_gpu_24gb
#SBATCH --cpus-per-task=32
#SBATCH --mem=128000
#SBATCH --time=2-00
#SBATCH --output=/u/samridhi.kalra/master_thesis/genpod/logs/genpod-%j.out

echo "Running: $@"
cd /u/samridhi.kalra/master_thesis/genpod/
source /u/samridhi.kalra/.cache/pypoetry/virtualenvs/genfond-yn4YVXNL-py3.10/bin/activate
#python -m genfond -v  domains/partially-observable-deterministic/wumpus/{d_no_pit.pddl,p2x3_no_pit.pddl} -o wumpus.pickle -l output_wumpus2x3_test.log

python -m genfond -v  domains/partially-observable-deterministic/colorballs/{d.pddl,p2x3-2.pddl} -o colorballs2x3-2.pickle -l output_colorballs2x3-2_test.log --min-complexity 7 --max-complexity 17
#python -m genfond -v domains/partially-observable-deterministic/wumpus/d_no_pit.pddl domains/partially-observable-deterministic/wumpus/p3/p3_no_pit.pddl -o wumpus3.pickle -l output_wumpus3_test.log --min-complexity 7 --max-complexity 17
    #--ground-truth domains/partially-observable-deterministic/wumpus/d_no_pit.pddl domains/partially-observable-deterministic/wumpus/p3/p3_hidden_no_pit.pddl \
    