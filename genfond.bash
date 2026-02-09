#!/bin/bash
#
#SBATCH --partition=rleap_gpu_24gb
#SBATCH --cpus-per-task=32
#SBATCH --mem=64g
#SBATCH --time=2-00
#SBATCH --output=/u/samridhi.kalra/master_thesis/genpod/logs/genpod-%j.out


echo "Running: $@"
apptainer run --bind $PWD genfond_env.sif "$@"
