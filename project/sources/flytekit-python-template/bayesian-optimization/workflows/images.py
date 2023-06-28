from flytekit import ImageSpec

default = ImageSpec(
    name="flytekit",
    base_image="ghcr.io/flyteorg/flytekit:py3.8-1.6.0",
    registry="ghcr.io/unionai-oss",
    packages=["flytekit>=1.7.0", "bayesian-optimization==1.4.3"],
    python_version="3.10"
)