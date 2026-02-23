#!/bin/bash
#
#SBATCH --partition=rleap_cpu
#SBATCH --cpus-per-task=32
#SBATCH --mem=64000
#SBATCH --time=2-00
#SBATCH --output=/u/samridhi.kalra/master_thesis/genpod/logs/genpod-%j.out

echo "Running: $@"
cd /u/samridhi.kalra/master_thesis/genpod/
#source /u/samridhi.kalra/.cache/pypoetry/virtualenvs/genfond-yn4YVXNL-py3.10/bin/activate

#python execute_policy.py domains/partially-observable-deterministic/doors/d.pddl  \
#    domains/partially-observable-deterministic/doors/p7.pddl doors5x3.pickle \
#    --test-set domains/partially-observable-deterministic/doors/p7_hidden.pddl

apptainer run --bind $PWD genfond_env.sif python execute_policy.py domains/partially-observable-deterministic/doors/d.pddl  \
    domains/partially-observable-deterministic/doors/p5.pddl doors5x3_local.pickle \
    --test-set domains/partially-observable-deterministic/doors/p5_test.pddl