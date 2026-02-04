#!/bin/bash
#
#SBATCH --partition=rleap_gpu_24gb
#SBATCH --cpus-per-task=32
#SBATCH --mem=5000
#SBATCH --time=2-00
#SBATCH --output=/u/samridhi.kalra/master_thesis/genpod/logs/genpod-%j.out
#SBATCH --exclude=cn-401,cn-402,cn-403,cn-404,cn-409,cn-407
#SBATCH --nodelist=cn-405

echo "Running: $@"
cd /u/samridhi.kalra/master_thesis/genpod/
source /u/samridhi.kalra/.cache/pypoetry/virtualenvs/genfond-yn4YVXNL-py3.10/bin/activate
python -m genfond -v  domains/partially-observable-deterministic/wumpus/{d_no_pit.pddl,p.pddl} -o wumpus.pickle
