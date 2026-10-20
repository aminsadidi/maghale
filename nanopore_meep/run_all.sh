#!/bin/bash
# Runs every case reported in README.md (4 MPI ranks each). Usage: bash run_all.sh
PY="${PY:-python}"; MPI="${MPI:-mpiexec -n 4}"
cd "$(dirname "$0")"; mkdir -p runs
run() { out=$1; shift; [ -f runs/$out.npz ] && return; echo "$(date +%T) start $out"
        $MPI $PY "$@" --out runs/$out.npz > runs/$out.log 2>&1 && echo "$(date +%T) done $out" || echo "$(date +%T) FAILED $out"; }
# order: main results first, convergence runs after
run empty_r1000       bowl_cyl.py --shape empty --res 1000
run bowl_R10_r1000    bowl_cyl.py --shape bowl --R 10 --res 1000
run conv_R10_r1000    bowl_cyl.py --shape conv --R 10 --res 1000
run sphere_r1000      bowl_cyl.py --shape sphere --R 25 --res 1000
run pip_empty_r500    particle_in_pore_3d.py --mode empty --res 500
run pip_g5_r500       particle_in_pore_3d.py --gap 5 --res 500
run pip_hole_r500     particle_in_pore_3d.py --mode hole --res 500
run empty_r1500       bowl_cyl.py --shape empty --res 1500
run bowl_R10_r1500    bowl_cyl.py --shape bowl --R 10 --res 1500
run bowl_R2.5_r1500   bowl_cyl.py --shape bowl --R 2.5 --res 1500
run bowl_R1_r1500     bowl_cyl.py --shape bowl --R 1 --res 1500
run conv_R2.5_r1500   bowl_cyl.py --shape conv --R 2.5 --res 1500
run bowl_R10_jc_r1000 bowl_cyl.py --shape bowl --R 10 --gold jc --res 1000
run pip_empty_r667    particle_in_pore_3d.py --mode empty --res 667
run pip_g5_r667       particle_in_pore_3d.py --gap 5 --res 667
run pip_hole_r667     particle_in_pore_3d.py --mode hole --res 667
