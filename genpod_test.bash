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

#python -m genfond  domains/partially-observable-deterministic/doors/{d.pddl,p2x5.pddl,p5x3.pddl,p3.pddl,p5.pddl,p7.pddl} -o output/doors_benchmark.pickle -l logs/output/output_doors_benchmark.log --min-complexity 6 --max-complexity 30 --train-set domains/partially-observable-deterministic/doors/{p2x5_hidden.pddl,p5x3_hidden.pddl,p3_hidden.pddl,p5_hidden.pddl,p7_hidden.pddl} --test-set domains/partially-observable-deterministic/doors/{p2x5_test.pddl,p5x3_test.pddl,p3_test.pddl,p5_test.pddl,p7_test.pddl} --stats output/doors_stats

#python -m genfond  domains/partially-observable-deterministic/binary-search/{d.pddl,p05.pddl,p10.pddl,p50.pddl} -o output/binary_search2.pickle -l logs/output/output_binary_search.log --min-complexity 6 --max-complexity 20 --train-set domains/partially-observable-deterministic/binary-search/{p05_hidden.pddl,p10_hidden.pddl,p50_hidden.pddl} --test-set domains/partially-observable-deterministic/binary-search/{p05_test.pddl,p10_test.pddl,p50_test.pddl} --stats output/binary_search_stats

python -m genfond  domains/partially-observable-deterministic/localize/{d.pddl,p3.pddl,p5.pddl,p7.pddl,p9.pddl,p11.pddl,p13.pddl,p15.pddl,p17.pddl} -o output/localize2.pickle -l logs/output/output_localize.log --min-complexity 6 --max-complexity 25 --train-set domains/partially-observable-deterministic/localize/{p3_hidden.pddl,p5_hidden.pddl,p7_hidden.pddl,p9_hidden.pddl,p11_hidden.pddl,p13_hidden.pddl,p15_hidden.pddl,p17_hidden.pddl} --test-set domains/partially-observable-deterministic/localize/{p3_test.pddl,p5_test.pddl,p7_test.pddl,p9_test.pddl,p11_test.pddl,p13_test.pddl,p15_test.pddl,p17_test.pddl} --stats output/localize_stats

#python -m genfond  domains/partially-observable-deterministic/ebtcs/{d2.pddl,p10.pddl,p30.pddl,p50.pddl,p70.pddl} -o output/ebtcs2.pickle -l logs/output/output_ebtcs.log --min-complexity 6 --max-complexity 25 --train-set domains/partially-observable-deterministic/ebtcs/{p10_hidden.pddl,p30_hidden.pddl,p50_hidden.pddl,p70_hidden.pddl} --test-set domains/partially-observable-deterministic/ebtcs/{p10_test.pddl,p30_test.pddl,p50_test.pddl,p70_test.pddl} --stats output/ebtcs_stats
