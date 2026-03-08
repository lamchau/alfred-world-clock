## SETUP

This documentation is for those who want to setup this workflow locally to do some work on it. PRs welcomed!


### uv

This workflow uses [uv](https://docs.astral.sh/uv/) for dependency management.
To install uv in your local environment follow [these instructions](https://docs.astral.sh/uv/getting-started/installation/).


### dependencies

Once you have uv installed, the next thing is to fetch all of this project's dependencies using the command `uv sync`.
This command will use the `pyproject.toml` file to create a virtual env and install all the necessary libraries from PyPI.


### release

To import the current state of the workflow into Alfred, you can use the script `./scripts/release.sh`.
This will package all the required components to run the workflow in Alfred without any external dependencies.

At the end, you'll be automatically prompted to import it into Alfred.

> You can find the generated `.alfredworkflow` files in the `releases/` folder.
