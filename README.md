# Flyte Remote Build and Registration Workflow

This is a Flyte workflow that enables the use of a Flyte task and Kubernetes cluster as a remote build server and registration device for Flyte constructs. With this workflow, you can remotely register your Flyte workflows without needing to have the local dependencies installed. Simply configure, fire, and forget.

## How to Run

### 1. Prepare Your Config File
First, prepare your `config.yaml` file. Check the template provided in the repository to understand what you need to modify.

### 2. Create Secrets in AWS Secrets Manager
You'll need to create two secrets in AWS Secrets Manager:

#### Flyte App Secret
- Create an App with Kubernetes and record the app name (put it in the `config.yaml` file).
- Separately, record the secret and store that in the AWS Secrets Manager as raw text.

#### Second Secret
This secret is a JSON object containing an imageRegistry path, username, and password. For example:
```json
{
  "registry": "ghcr.io/zeryx/flytekit",
  "username": "zeryx",
  "password": "..."
} ```

Store this also in the AWS Secrets Manager.

Follow this guide to connect your AWS Secrets Manager with your Flyte cluster.

Inputs
Pass in a Git URL pointing to the workflows you want to register, along with the branch or commit hash.
Outputs
The full URL of your now registered workflow(s) that you can interact with will be provided as the output.
Support and Contributions
If you encounter any issues or have any questions, please open an issue in this repository. Contributions to enhance this workflow are also welcome!
