import os
import json
import numpy
import argparse
from orquestra.runtime import QERuntime, RayRuntime
from orquestra.runtime._config import read_config

parser = argparse.ArgumentParser(description='Parse workflow information.')
parser.add_argument('id', type=str, help='workflow id')
parser.add_argument('--cluster', type=str, default="https://ps-chemistry.orquestra.io", help="cluster url")
args = parser.parse_args()

CLUSTER_URL = args.cluster
WORKFLOW_ID = args.id
PATH_TO_RESULT = "results/"

runtime = QERuntime.from_runtime_configuration(
    project_dir=".",
    config=read_config(CLUSTER_URL),
)

# read outputs 
workflow_results = runtime.get_workflow_run_outputs_non_blocking(WORKFLOW_ID)
madmolecule = workflow_results[0]
result = workflow_results[1]
h = workflow_results[2]
g = workflow_results[3]

# process results
result["MRA-PNO"] = "({},{})".format(result["n_electrons"], result["n_orbitals"]*2)
energy = result["energy"]
mol_name = result["name"]
n_pno = madmolecule["n_pno"]

print("pyscf energyc from MRA-PNO: ", energy)


# write output to files
# check if path exist
if not os.path.exists(PATH_TO_RESULT + mol_name):
    os.makedirs(PATH_TO_RESULT + mol_name) 

# write energy
with open ("{}{}/energy-{}.json".format(PATH_TO_RESULT, mol_name, str(n_pno)), "w") as f:
    f.write(json.dumps(result, indent=2))
print("*** ENERGY RESULTS WRITTEN TO: energy.json ***")


# save pno_info.txt for restart
with open ("{}{}/{}_pnoinfo_{}.txt".format(PATH_TO_RESULT, mol_name, mol_name, str(n_pno)), "w") as f:
    f.write("pairinfo=" + ','.join(str(x) for x in madmolecule['pairinfo']))
    f.write("nuclear_repulsion=" + str(madmolecule['nuclear_repulsion']) + '\n')
    f.write("occinfo=" + ','.join(str(x) for x in madmolecule['occinfo']))
    
# save integrals for restart
numpy.save("{}{}/{}_gtensor.npy".format(PATH_TO_RESULT, mol_name, mol_name), arr=g)
numpy.save("{}{}/{}_htensor.npy".format(PATH_TO_RESULT, mol_name, mol_name), arr=h)



# with open(PATH_TO_RESULT + mol_name + "/madmolecule-diag-" + str(n_pno) + ".json", "w") as f:
#     f.write(json.dumps(madmolecule, indent=2))
# print("*** MOLECULE RESULT WRITTEN TO: madmolecule.json ***")
