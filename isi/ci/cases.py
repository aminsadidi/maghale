"""Case definitions for the CI (GitHub Actions) runs. Same cases as stages A and B of the Colab notebook."""
STAGES = {
    'A': [('bench_sphere_res0.5', dict(shape='sphere', orient='z', gap=5.0, res=0.5)),
          ('bench_sphere_res0.75', dict(shape='sphere', orient='z', gap=5.0, res=0.75)),
          ('bench_sphere_res1.0', dict(shape='sphere', orient='z', gap=5.0, res=1.0)),
          ('bench_sphere_res1.0_pml0.3', dict(shape='sphere', orient='z', gap=5.0, res=1.0, dpml=0.3))],
    'B': [('rodA_z_gap5_res0.5', dict(shape='rod', orient='z', gap=5.0, res=0.5, na_list=[0.5, 0.9, 1.3])),
          ('rodA_z_gap5_res0.75', dict(shape='rod', orient='z', gap=5.0, res=0.75, na_list=[0.5, 0.9, 1.3])),
          ('rodA_z_gap5_res1.0', dict(shape='rod', orient='z', gap=5.0, res=1.0, na_list=[0.5, 0.9, 1.3])),
          ('rodC_x_gap5_res1.0', dict(shape='rod', orient='x', gap=5.0, res=1.0)),
          ('sphereDp_x_gap5_res1.0', dict(shape='sphere', orient='x', gap=5.0, res=1.0))],
}
