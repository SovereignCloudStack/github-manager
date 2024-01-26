#!/usr/bin/env python3

import os, sys
from pprint import pformat

import github
import yaml
from github import Github

API_TOKEN = os.environ.get("API_TOKEN")
ORGANIZATION = os.environ.get("ORGANIZATION", "SovereignCloudStack")


def check_repos(gh: Github) -> int:
    existing_repos = set()
    defined_repos = set()
    archived_repos = set()
    errors_repos = 0

    for repo in gh.get_organization(ORGANIZATION).get_repos(type="public", ):
        if repo.archived:
            archived_repos.add(repo.name)
        else:
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
        out_tmp = [f"\n# Repos not on GitHub:\n"]
        for repo in repos_not_on_github:
            if repo not in archived_repos:
                errors_repos += 1
                out_tmp.append(f"* [{repo}](https://www.github.com/{ORGANIZATION}/{repo}/settings)")
        if len(out_tmp) > 1:
            print("\n".join(out_tmp))

        out_tmp = [f"\n# Archived repos on GitHub, but still defined:\n"]
        for repo in repos_not_on_github:
            if repo in archived_repos:
                out_tmp.append(f"* [{repo}](https://www.github.com/{ORGANIZATION}/{repo}/settings)")
        if len(out_tmp) > 1:
            print("\n".join(out_tmp))

    if len(repos_not_defined) != 0:
        out_tmp = [f"\n# Repos not defined in github-manager:\n"]
        for repo in repos_not_defined:
            out_tmp.append(f"* [{repo}](https://www.github.com/{ORGANIZATION}/{repo}/settings)")
            errors_repos += 1
        if len(out_tmp) > 1:
            print("\n".join(out_tmp))
    return errors_repos


def check_user(data: dict) -> bool:
    valid = True
    for key in data.keys():
        if key not in ["login", "name", "role"]:
            valid = False
    return valid


def check_users(gh: Github) -> int:
    data_file = os.path.join("orgs/" + ORGANIZATION + "/data.yaml")

    errors_users = 0
    defined_users = dict()
    existing_users = dict()

    broken_users = []
    with open(data_file) as f:
        yaml_data = yaml.safe_load(f)
        for member in yaml_data["members"]:
            if check_user(member):
                defined_users[member["login"].lower()] = member["name"]
            else:
                broken_users.append(f"* User not correctly defined:  >>>{pformat(member)}<<<")

    for member in gh.get_organization(ORGANIZATION).get_members():
        existing_users[member.login.lower()] = member.name

    users_not_on_github = set(defined_users.keys()).difference(set(existing_users.keys()))
    users_not_defined = set(existing_users.keys()).difference(set(defined_users.keys()))

    if len(broken_users) != 0:
        print(f"\n# Users which are defined but are broken:\n")
        for user in  broken_users:
            print(user)
        print()
        errors_users += len(broken_users)

    if len(users_not_on_github) != 0:
        out_tmp = [f"\n# Users not (yet) assigned to the github organization:\n"]
        for user in sorted(users_not_on_github):
            out_tmp.append(f"* [{user} - {defined_users[user]}](https://www.github.com/{user})")
        print("\n".join(out_tmp))

    if len(users_not_defined) != 0:
        out_tmp = [ f"\n# Users which are not defined in github manager:\n" ]
        for user in sorted(users_not_defined):
            out_tmp.append(f"* [{user} - {existing_users[user]}](https://www.github.com/{user})")
            errors_users += 1
        print("\n".join(out_tmp))
    return errors_users


gh = github.Github(login_or_token=API_TOKEN)

errors = 0
errors += check_repos(gh)
errors += check_users(gh)

if errors > 0:
    print(f"\n{errors} errors detected", file=sys.stderr)

if errors >= 255:
    sys.exit(255)
else:
    sys.exit(0)
