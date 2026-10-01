import sys, time, numpy as np; sys.path.insert(0,'.')
from nanorod import simulate
t=time.time(); o=simulate('rod','z',5.0,res=0.25,trun=60,na_list=(0.9,))
i=o['Fp'].argmax(); j=o['T'].argmax()
print(f"rod z res=4nm: Fp {o['Fp'][i]:.0f}@{o['lam'][i]:.0f}  T {o['T'][j]:.1f}@{o['lam'][j]:.0f}  eta@T {100*o['eta'][j]:.1f}%  coll(NA0.9)@T {o['coll_NA0.9'][j]:.2f}  time {time.time()-t:.0f}s")
