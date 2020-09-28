from azureml.core import Workspace
from azureml.core import Experiment
from azureml.pipeline.core import PipelineRun

import argparse
from time import sleep

from ml_service.util.env_variables import Env


def main():
    e = Env()

    parser = argparse.ArgumentParser("check-status")
    parser.add_argument(
        "--run_id",
        type=str,
        help="Run ID to monitor"
    )

    args = parser.parse_args()

    aml_workspace = Workspace.get(
        name=e.workspace_name,
        subscription_id=e.subscription_id,
        resource_group=e.resource_group
    )

    experiment = Experiment(aml_workspace, e.experiment_name)
    pipeline_run = PipelineRun(experiment, args.run_id)
    run = pipeline_run.get(aml_workspace, args.run_id)

    while(True):
        status = run.get_status()
        print(status)

        if status == "Failed" or status == "Finished" or status == "Canceled":
             print(f"Run {args.run_id} has been completed with status: {status}")
             break

        sleep(5)

if __name__ == '__main__':
    main()
