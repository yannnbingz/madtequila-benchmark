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
energy = workflow_results[0]
ecorr = workflow_results[1]


print("pyscf energy w/ ccpv5z ", energy + ecorr)


# # write output to files
# # check if path exist
# if not os.path.exists(PATH_TO_RESULT + mol_name):
#     os.makedirs(PATH_TO_RESULT + mol_name) 

# # write energy
# with open ("{}{}/energy-{}.json".format(PATH_TO_RESULT, mol_name, str(n_pno)), "w") as f:
#     f.write(json.dumps(result, indent=2))
# print("*** ENERGY RESULTS WRITTEN TO: energy.json ***")


