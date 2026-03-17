# Task 2: Package and Publish Your Plugin

## Task

With a working [implementation](./task-1-write-a-npm-plugin.md) in place, your NPM plugin is ready for packaging and distribution. Your next task is to **create a Python wheel** and package this into an **OCI container image** to make the plugin portable and easy to deploy on any workstation.

## Hints

### Prerequisites: Docker Hub Repository and Credentials

Before running the workflow, make sure you have [created a Docker Hub repository and configured your Docker credentials as GitHub Secrets and Variables](./../getting-started/getting-started.md#set-up-your-docker-depsight-npm-plugin-repository) as described in the Getting Started guide. Publishing the Python wheel to a GitHub release requires no credentials, but publishing the container image to DockerHub does.

### Inline TODOs

The template repository already includes a `Dockerfile` and a GitHub Actions workflow script `build.yml`. Follow the inline `TODO` statements in both files to complete them. The expected outcome is a container image published to [DockerHub](https://hub.docker.com) and a Python wheel attached to a `1.0.0` release on your GitHub repository.

![Todos Overview](../../images/todos_task_2.png)


### Build and Push Image

Within your GitHub repository navigate to the **Actions** bar and click the **Manual Dispatch** entry on the left-side.

You can leave the default values, ensure to set the version of the plugin that is specified in the `pyproject.toml`. Enable the checkbox to push the image to Docker Hub and click the *Run Workflow* button.

![Run dispatch](../../images/run_dispatch.png)