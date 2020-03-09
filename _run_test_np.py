import os
import pandas as pd

os.chdir(r'm:\work\github\primes_comparison')

import primes_np
from reporttime import get_functions_with_prefix, measure

funcs = get_functions_with_prefix('', module=primes_np)

d = {}
for n in [10**2, 10**3, 10**4, 10**5, 10**6]:
    m = measure(funcs, args=[n])
    d[n] = pd.Series({b:a for a,b in m}) 
r = pd.DataFrame(d)

####################################

import matplotlib.pyplot as plt
import matplotlib

%matplotlib

matplotlib.style.use('ggplot')

r.T.plot(loglog=True, grid=True, figsize=(8, 6))
plt.xlabel('N - generate all primes below N (+Numpy implemetations)')
plt.ylabel('Time in seconds')
plt.savefig(r'primes_np_comparison.png')