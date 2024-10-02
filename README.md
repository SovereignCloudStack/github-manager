# GitHub permissions management through Ansible & Python

This repository manages the GitHub permissions for the SCS organization.

The CI is based on the great work contributed by [OTC](https://github.com/opentelekomcloud/ansible-collection-gitcontrol)
and [OSISM](https://github.com/osism/github-manager).

# Local usage

You can use the following procedure to test, debug or improve github manager on your local system.

* Installation
  ```sh
  git clone git@github.com:SovereignCloudStack/github-manager.git
  cd github-manager
  rm -rf ansible-collection-gitcontrol
  git submodule update --init --recursive
  python3 -m pip install --upgrade pip
  python3 -m pip install pipenv wheel
  pipenv install
  pipenv run ansible-galaxy collection install git+https://github.com/opentelekomcloud/ansible-collection-gitcontrol.git
  ```
* Create a [personal access token - classic (PAT)](https://github.com/settings/tokens)
  This should only have a short validity and must be renewed regularly.
  (The rights ``repo`` and ``admin:org`` are required)
* Execute Manager
  ```sh
  export API_TOKEN="<github-token>"
  pipenv run ansible-playbook playbook.yaml -e api_token=${API_TOKEN}

  # Debugging with Ansiballs: https://docs.ansible.com/ansible/latest/dev_guide/debugging.html
  ANSIBLE_KEEP_REMOTE_FILES=1 pipenv run ansible-playbook playbook.yaml -e api_token=${API_TOKEN} -vvv
  ```
* Execute Consistency Check
  ```
  pipenv run ./check_consistency.py
  ```

## Limitiations

* It is not possible to add already created, but still empty, repositories here. Before this is possible,
at least one commit must have been made on the main branch.

* It is not possible to remove members from the organization or any team. Please first delete the corresponding
lines in `data.yaml` here in this repository and delete the user afterwards via the GitHub UI.

We're working on these issues upstream: <https://github.com/opentelekomcloud/ansible-collection-gitcontrol> and
<https://github.com/opentelekomcloud-infra/gitstyring>

## Github Actions

For the Github Action workflows a repository secret ``GHP_{{github_username}}`` needs to be provided. i
This should only have a short validity and must be renewed regularly.
Add the created token of the second step in the topic "Local usage" to
[REPOSITORTY_SECRETS](https://github.com/SovereignCloudStack/github-manager/settings/secrets/actions)
(Name: "GHP_<GITHUB_ID_IN_UPPERCASE>")

If the following error in the logs comes from ``Manage github repositories``x the token has
expired and must be renewed.
