import sys
sys.path.append('/app/qe-madtequila/steps')
sys.path.append('/app/qe-madtequila/src/python')
sys.path.append('/app/jax')
from run_madtequila import run_madness, compute_pyscf_energy
import os

for i in [4]:
    #run_madness('mol.json', i)
    compute_pyscf_energy('madmolecule.json', method='uccsd(t)')
    #compute_pyscf_energy('madmolecule-diag-4.json', method='uccsd(t)')
    #os.rename('energy.json', 'energy-' + str(i) + '.json')
    #os.rename('madmolecule.json', 'madmolecule-diag-' + str(i) + '.json')

