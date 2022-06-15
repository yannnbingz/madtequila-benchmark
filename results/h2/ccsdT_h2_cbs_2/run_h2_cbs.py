import sys
sys.path.append('/app/qe-madtequila/steps')
sys.path.append('/app/qe-madtequila/src/python')
sys.path.append('/app/jax')
from run_madtequila import run_madness, compute_pyscf_energy
import os

for i in [2]:
    run_madness('../mol.json', i)
    compute_pyscf_energy('madmolecule.json', method='ccsd(t)')
    os.rename('energy.json', 'energy-' + str(i) + '.json')

