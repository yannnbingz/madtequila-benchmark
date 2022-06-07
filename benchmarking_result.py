from orquestra.runtime import QERuntime, RayRuntime
from orquestra.runtime._config import read_config

# replace with URL of your remote cluster
CLUSTER_URL = "https://pse-1.orquestra.io"
# replace with workflow ID returned from submit command
WORKFLOW_ID = "benchmarking-h2-k7nod-r000"

runtime = QERuntime.from_runtime_configuration(
    project_dir=".",
    config=read_config(CLUSTER_URL),
)
runtime = RayRuntime('.')
workflow_results = runtime.get_workflow_run_outputs_non_blocking(WORKFLOW_ID)
print(workflow_results)