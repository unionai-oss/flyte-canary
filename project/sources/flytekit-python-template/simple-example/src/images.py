from flytekit import ImageSpec


default = ImageSpec(
    name="flytekit",
    base_image="ghcr.io/flyteorg/flytekit:py3.8-1.6.0",
    registry="ghcr.io/zeryx",
    packages=["flytekit>=1.7", "pandas", "scikit-learn"],
    python_version="3.10"
)