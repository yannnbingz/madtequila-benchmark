import sys
sys.path.append('/app/jax')
sys.path.append('/app/yz-openshell-madtequila/src/python')
import os
import json
from typing import Dict
import qemadtequila as madtq
import tequila as tq

name="h2o"
geometry="o           -0.000000000000     0.000000000000     0.065705222098 \n h           -0.000000000000     0.754700000000    -0.521394777902 \n h            0.000000000000    -0.754700000000    -0.521394777902"
frozen_core=False
n_pno=20
maxrank=4

mol = tq.Molecule(
    name = name,
    geometry = geometry,
    frozen_core = frozen_core,
#    n_pno = n_pno,
    #maxrank = maxrank
)
#with open ('h2o' + '_pnoinfo.txt', 'r') as f:
#    for line in f.readlines():
#        if "nuclear_repulsion" in line:
#            nuclear_repulsion = float(line.split("=")[1])
#        elif "pairinfo" in line:
#            pairinfo = line.split("=")[1].split(",")
#            #pairinfo = [tuple([int(i) for i in x.split(".")]) for x in pairinfo]
#        elif "occinfo" in line:
#            occinfo = line.split("=")[1].split(",")
#            occinfo = [float(x) for x in occinfo]
#
#
#print("nuclear_repulsion: ", nuclear_repulsion)
#print("pairinfo: ", pairinfo)
#print("occinfo: ",  occinfo)
#h,g = mol.read_tensors(name=name)
#print(h)
#print(g)
#
#numpy.save("{}_htensor.npy".format(name), arr=h)

#results_dict = {}
#results_dict["name"] = name
#results_dict["geometry"] = geometry
#results_dict["frozen_core"] = frozen_core
#results_dict["n_pno"] = n_pno
#results_dict["maxrank"] = maxrank
#json_string = madtq.mol_to_json(mol)
#results_dict["mol"]=json_string
#with open("madmolecule.json", "w") as f:
#    f.write(json.dumps(results_dict, indent=2))


# avoid re-computation of madness orbitals
mol2 = tq.chemistry.QuantumChemistryPySCF.from_tequila(mol)
                                                      # , active_orbitals=[0,3])
#hf = mol2.compute_energy("hf")
#print(hf)
#ccsd = mol2.compute_energy("ccsd")
#print(ccsd)
ccsdt = mol2.compute_energy("ccsd(t)")
print("ccsd(t) energy: ", ccsdt)


#sys.path.append('/app/yz-openshell-madtequila/steps')
#from run_madtequila import compute_pyscf_energy
#compute_pyscf_energy('madmolecule.json',method='ccsd(t)')
