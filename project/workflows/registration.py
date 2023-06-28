"""A simple Flyte example."""
import typing
from pathlib import Path

from flytekit.configuration import SerializationSettings, Config, PlatformConfig, ImageConfig, \
    FastSerializationSettings
from flytekit.core.base_task import PythonTask
from flytekit.core.workflow import WorkflowBase
from flytekit import task, dynamic
from flytekit.image_spec.image_spec import ImageBuildEngine
from flytekit.remote import FlyteRemote
from contextlib import contextmanager
import yaml
import importlib
import os, sys

@contextmanager
def module_management(workflow_name: str, file_name: str = "", module: str = "workflows", secondary: bool = False):
    """
    allows for the import of a workflow module from a path,
    but imports from the templates root directory; preserving the correct path for imports
    """
    path = os.path.join("project", "sources", "flytekit-python-template", workflow_name)
    if secondary:
        path = os.path.join("root", path)
        directory_contents = os.listdir(path)

        # Print the results
        for item in directory_contents:
            print(item)
    sys.path.insert(0, path)
    imported_module = None

    try:
        if file_name == "":
            import_path = ".".join([module])
            imported_module = importlib.import_module(import_path, package=module)
        else:
            import_path = ".".join([module, file_name])
            if import_path in sys.modules:
                del sys.modules[import_path]
            imported_module = importlib.import_module(import_path, package=file_name)
        yield imported_module
    finally:
        sys.path.remove(path)
        if imported_module in sys.modules:
            del sys.modules[imported_module.__name__]
@task
def register_workflow(workflow_content: dict, platform_args: dict) -> str:
    directory_name = workflow_content["directory"]
    workflow_name = workflow_content["workflow_name"]
    workflow_file_name = workflow_content["workflow_file"]
    print("workflow registration started")
    remote = FlyteRemote(config=Config(platform=PlatformConfig(**platform_args)), default_project="flytetester", default_domain="development")
    with module_management(directory_name, file_name=workflow_file_name, secondary=True) as project_mod:
        print("registering workflow")
        workflow = getattr(project_mod, workflow_name)
        source_root = os.path.join("/root", "project", "sources", "flytekit-python-template", directory_name)
        md5_bytes, native_url = remote.fast_package(Path(source_root), False)
        fast_serialization_settings = FastSerializationSettings(
            enabled=True,
            destination_dir="root",
            distribution_location=native_url,
        )
        serialization_settings = SerializationSettings(
            image_config=ImageConfig(),
            project="flytetester",
            domain="development",
            fast_serialization_settings=fast_serialization_settings,
        )

        version = remote._version_from_hash(md5_bytes, serialization_settings)

        if isinstance(workflow, WorkflowBase):
            wf = remote.register_workflow(entity=workflow,
                                          serialization_settings=serialization_settings,
                                          version=version
                                          )
        elif isinstance(workflow, PythonTask):
            wf = remote.register_task(entity=workflow,
                                      serialization_settings=serialization_settings,
                                      version=version
                                      )
        else:
            raise Exception("unknown workflow type")
        return remote.generate_console_url(wf)


@dynamic
def prepare_and_register(workflows_to_register: typing.List[dict]) -> typing.List[str]:
    workflows_to_register = [{"directory": "bayesian-optimization", "workflow_name": "wf", "workflow_file": "bayesian_optimization_example"}]
    config_path = os.path.join("project", "config", "config.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    platform_args = {
        "endpoint": config["endpoint"],
        "insecure": False,
        "auth_mode": "CLIENT_CREDENTIALS",
        "client_id": config["client_id"],
        "client_credentials_secret": config["client_credentials_secret"]
    }
    if platform_args["client_id"] == "":
        platform_args["client_id"] = os.getenv("FLYTE_CLIENT_ID")
    if platform_args["client_credentials_secret"] == "":
        platform_args["client_credentials_secret"] = os.getenv("FLYTE_CLIENT_SECRET")
    workflows = []
    for workflow in workflows_to_register:
        with module_management(workflow["directory"], module="workflows", file_name="images") as image_module:
            image = getattr(image_module, "default")
            print(f"image: {image}")
            registered_wf = register_workflow(workflow_content=workflow, platform_args=platform_args).with_overrides(
                container_image=image)
        workflows.append(registered_wf)
    return workflows


if __name__ == '__main__':
    # Build the image for the workflow by running python project/workflows/registration.py
    # Note: The flytekit version should be the same as the version in the imageSpec
    workflows_to_register = [
        {"directory": "bayesian-optimization", "workflow_name": "wf", "workflow_file": "bayesian_optimization_example"}]
    for workflow in workflows_to_register:
        with module_management(workflow["directory"], module="workflows", file_name="images") as image_module:
            image = getattr(image_module, "default")
            print(f"image: {image}")
            ImageBuildEngine.build(image)
