#!/usr/bin/env bash
# Git clones a repo based on the URL provided, installs the dependencies and then runs pyflyte register

# Clone the repo
GIT_URL=$1
GIT_CHECKOUT_TARGET=$2
PROJECT_DIR=$3
SECRET_FILE=/var/inputs/secret_file

IM_REGISTRY=$(jq -r '.registry'  $SECRET_FILE)
IM_USER=$(jq -r '.user' $SECRET_FILE)
IM_PASS=$(jq -r '.pass' $SECRET_FILE)
FLYTE_SECRET=$(jq -r '.flyte_secret' $SECRET_FILE)

git clone "$GIT_URL"
echo "Cloned Repo Successfully"
repo_name=$(basename "$GIT_URL")
repo_path="${repo_name%.*}"
cd "$repo_path"
git checkout "$GIT_CHECKOUT_TARGET"

cd "$PROJECT_DIR" || exit
echo "CDed to directory"
# Install the dependencies
cat requirements.txt | xargs -n 1 -P 10 pip install
echo "Installed Dependencies Successfully"
pip install grpcio==1.51.3 grpcio-status==1.51.3
echo "Installed Flytekit Successfully"

echo $FLYTE_SECRET > /var/secret
echo "Created Secret File Successfully"

dockerd-entrypoint.sh &
sleep 30s
echo "Docker Daemon Started Successfully"


# Login to the image registry
docker login $IM_REGISTRY -u $IM_USER -p $IM_PASS
echo "Logged into Image Registry Successfully"

# Register the workflow
pyflyte --config /root/.uctl/config.yaml register . --project flytesnacks --domain development > log.txt 2>&1;  cat log.txt
workflow_name=$(cat log.txt | grep -oP '\[✔\] Registration \K\S+' | tail -n 1)
echo $workflow_name > /var/outputs/output