#!/usr/bin/env python3

import os, sys
import github
import yaml
from github import Github

API_TOKEN = os.environ.get("API_TOKEN")
ORGANIZATION = os.environ.get("ORGANIZATION", "SovereignCloudStack")


def check_repos(gh: Github) -> int:
    existing_repos = set()
    defined_repos = set()
    errors = 0

    for repo in gh.get_organization(ORGANIZATION).get_repos(type="public"):
        existing_repos.add(repo.name)

    repositories_dir = os.path.join("orgs/" + ORGANIZATION + "/repositories")

    for filename in os.listdir(repositories_dir):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            with open(os.path.join(repositories_dir, filename)) as f:
                yaml_data = yaml.safe_load(f)
                if yaml_data is not None:
                    defined_repos.add(list(yaml_data.keys())[0])

    repos_not_on_github = defined_repos.difference(existing_repos)
    repos_not_defined = existing_repos.difference(defined_repos)

    if len(repos_not_on_github) != 0:
        print(f"# Repos not on GitHub:\n", file=sys.stderr)
        for repo in repos_not_on_github:
            print(f"* [{repo}](https://www.github.com/{ORGANIZATION}/{repo}/settings)", file=sys.stderr)
        errors += 1
        print("\n", file=sys.stderr)

    if len(repos_not_defined) != 0:
        print(f"# Repos not defined in github-manager:\n", file=sys.stderr)
        for repo in repos_not_defined:
            print(f"* [{repo}](https://www.github.com/{ORGANIZATION}/{repo}/settings)", file=sys.stderr)
        errors += 1
        print("\n", file=sys.stderr)
    return errors


def check_users(gh: Github) -> int:
    data_file = os.path.join("orgs/" + ORGANIZATION + "/data.yaml")

    errors = 0
    defined_users = dict()
    existing_users = dict()

    with open(data_file) as f:
        yaml_data = yaml.safe_load(f)
        for member in yaml_data["members"]:
            defined_users[member["login"].lower()] = member["name"]

    for member in gh.get_organization(ORGANIZATION).get_members():
        existing_users[member.login.lower()] = member.name

    users_not_on_github = set(defined_users.keys()).difference(set(existing_users.keys()))
    users_not_defined = set(existing_users.keys()).difference(set(defined_users.keys()))

    if len(users_not_on_github) != 0:
        print(f"# Users not assigned to the GitHub organization:\n", file=sys.stderr)
        for user in sorted(users_not_on_github):
            print(f"* [{user} - {defined_users[user]}](https://www.github.com/{user})")
        errors += 1
        print("\n", file=sys.stderr)

    if len(users_not_defined) != 0:
        print(f"# Users which are not member of the github-organization {ORGANIZATION}:\n", file=sys.stderr)
        for user in sorted(users_not_defined):
            print(f"* [{user} - {existing_users[user]}](https://www.github.com/{user})")
        errors += 1
        print("\n", file=sys.stderr)
    return errors


gh = github.Github(login_or_token=API_TOKEN)

errors = 0
errors += check_repos(gh)
errors += check_users(gh)

if errors >= 255:
    print(f"\n{errors} detected", file=sys.stderr)
    sys.exit(1)
else:
    sys.exit(0)
