"""A simple Flyte example."""

import typing
from flytekit import ContainerTask, workflow, kwtypes, task, Secret, current_context, PodTemplate, Resources
from flytekit.types.file import FlyteFile
import json
from typing import Tuple
from kubernetes.client import V1PodSpec, V1Container, V1SecurityContext

SECRET_GROUP = "arn:aws:secretsmanager:us-east-2:356633062068:secret:"
SECRET_FLYE_CONFIG = "flyte/secret/config-v0djCs"
SECRET_FLYTE_APP_SECRET = "flyte/secret/data-RbucyV"
SECRET_IM = "img/registry/data-ihWOo0"


register = ContainerTask(
    name="register",
    input_data_dir="/var/inputs",
    output_data_dir="/var/outputs",
    inputs=kwtypes(git_url=str, git_commit_target=str, project_dir=str, secret_file=FlyteFile),
    outputs=kwtypes(output=str),
    image="ghcr.io/zeryx/canary:register",
    requests=Resources(cpu="10", mem="10Gi", ephemeral_storage="15Gi"),
    command=[
        "./execute.sh",
        "{{.inputs.git_url}}",
        "{{.inputs.git_commit_target}}",
        "{{.inputs.project_dir}}",
        "{{.inputs.secret_file}}",
        "/var/outputs"
    ],
    pod_template=PodTemplate(
        primary_container_name="register",
        pod_spec=V1PodSpec(
            containers=[
                V1Container(
                    name="register",
                    image_pull_policy="Always",
                    security_context=V1SecurityContext(
                        privileged=True,
                    )
            )]
        )
    )
)

@task(secret_requests=[
        Secret(
            group=SECRET_GROUP,
            key=SECRET_FLYTE_APP_SECRET,
            mount_requirement=Secret.MountType.FILE),
    Secret(
        group=SECRET_GROUP,
        key=SECRET_IM,
        mount_requirement=Secret.MountType.FILE)
    ])
def get_credentials() -> FlyteFile:
    flyte_secret = current_context().secrets.get(SECRET_GROUP, SECRET_FLYTE_APP_SECRET)
    im_data_content = current_context().secrets.get(SECRET_GROUP, SECRET_IM)
    output_data = json.loads(im_data_content)
    output_data["flyte_secret"] = flyte_secret
    with open("/tmp/secrets.json", "w") as f:
        json.dump(output_data, f)
    return FlyteFile("/tmp/secrets.json")

@workflow
def proxy_registration_wf(git_url: str, git_commit_target: str = "master", project_dir: str =".") -> str:
    """This is a dynamic task that will be executed at runtime."""
    creds = get_credentials()

    return register(
        git_url=git_url,
        git_commit_target=git_commit_target,
        project_dir=project_dir,
        secret_file=creds
    )
