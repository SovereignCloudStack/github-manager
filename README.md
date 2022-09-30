# GitHub permissions management through Ansible & Python

This repository manages the GitHub permissions for the SCS organization.

The CI is based on the great work contributed by [OTC](https://github.com/opentelekomcloud/ansible-collection-gitcontrol).
and [OSISM](https://github.com/osism/github-manager).

## Installation

```sh
python3 -m pip install --upgrade pip
python3 -m pip install pipenv wheel
pipenv install
ansible-galaxy collection install otc.ansible-collection-gitcontrol
```

## Usage

As a prerequisite, a PAT must be created. The rights ``repo`` and ``admin:org`` are required.

```sh
export API_TOKEN="<github-token>"
pipenv run ansible-playbook playbook.yaml -e  api_token=$API_TOKEN
```

## Limitiations

* It is not possible to add already created, but still empty, repositories here. Before this is possible,
at least one commit must have been made on the main branch.

* It is not possible to remove members from the organization or any team. Please first delete the corresponding
lines in `data.yaml` here in this repository and delete the user afterwards via the GitHub UI.

We're working on these issues upstream: <https://github.com/opentelekomcloud/ansible-collection-gitcontrol> and   
<https://github.com/opentelekomcloud-infra/gitstyring>

## Github Actions

For the Github Action workflows a repository secret ``GHP_{{github_username}}`` needs to be provided. This should only have a short
validity and must be renewed regularly.

If the following error in the logs comes from ``Manage github repositories``x the token has
expired and must be renewed.
