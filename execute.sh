#!/usr/bin/env bash
# Git clones a repo based on the URL provided, installs the dependencies and then runs pyflyte register

# Clone the repo
GIT_URL=$1
GIT_CHECKOUT_TARGET=$2
PROJECT_DIR=$3
FLYTE_SECRET=$4
IM_REGISTRY=$5
IM_USER=$6
IM_PASS=$7


git clone "$GIT_URL"
echo "Cloned Repo Successfully"
repo_name=$(basename "$GIT_URL")
dirname="${repo_name%.*}"

cd "$dirname" || exit
echo "CDed to directory"
git checkout "$GIT_CHECKOUT_TARGET"
# Install the dependencies
pip install -r requirements.txt
echo "Installed Dependencies Successfully"
pip install flytekit
echo "Installed Flytekit Successfully"

echo $FLYTE_SECRET > /tmp/secret
echo "Created Secret File Successfully"

# Login to the image registry
docker login $IM_REGISTRY -u $IM_USER -p $IM_PASS
echo "Logged into Image Registry Successfully"

cat /root/config.yaml
echo "verified config file"
cd $PROJECT_DIR
# Register the workflow
pyflyte --config /root/config.yaml register . --project flytesnacks --domain development

echo "foobar" > /var/outputs/a