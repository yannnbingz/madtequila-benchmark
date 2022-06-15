import sys
sys.path.append('/app/yz-openshell-madtequila/steps')
sys.path.append('/app/yz-openshell-madtequila/src/python')
sys.path.append('/app/jax')
from run_madtequila import run_madness, compute_pyscf_energy
import os

for i in [2]:
    run_madness('mol.json', i, name="o2", frozen_core=True, debgug=True, maxrank=4)
    compute_pyscf_energy('madmolecule.json', method='ccsd(t)')
    os.rename('energy.json', 'energy-' + str(i) + '.json')
    os.rename('madmolecule.json', 'madmolecule-diag-' + str(i) + '.json')

    #compute_pyscf_energy('madmolecule-diag-2.json', method='hf')
