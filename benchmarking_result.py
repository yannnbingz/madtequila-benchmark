import json
from orquestra.runtime import QERuntime, RayRuntime
from orquestra.runtime._config import read_config

# replace with URL of your remote cluster
CLUSTER_URL = "https://pse-1.orquestra.io"
# replace with workflow ID returned from submit command
# WORKFLOW_ID = "benchmarking-project-jozqe-r000"
WORKFLOW_ID = "benchmarking-project-yaten-r000"
PATH_TO_RESULT = "results/"

runtime = QERuntime.from_runtime_configuration(
    project_dir=".",
    config=read_config(CLUSTER_URL),
)
#runtime = RayRuntime('.')
workflow_results = runtime.get_workflow_run_outputs_non_blocking(WORKFLOW_ID)
# madmolecule = workflow_results[0]
# result = workflow_results[1]
# mol_name = workflow_results[2]
# n_pno = madmolecule["n_pno"]

print(n_pno)


# print("energy: ", energy)
# with open(PATH_TO_RESULT + mol_name + "/energy-" + str(n_pno) + ".json", "w") as f:
#     f.write(json.dumps(e_result, indent=2))
# print("***ENERGY RESULT WRITTEN TO: energy.json ***")

# with open(PATH_TO_RESULT + mol_name + "/madmolecule-diag-" + str(n_pno) + ".json", "w") as f:
#     f.write(json.dumps(madmolecule, indent=2))
