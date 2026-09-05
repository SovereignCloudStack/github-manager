#!/usr/bin/env python3
"""
Remove org members and team members that are no longer defined in data.yaml.

Uses data.yaml as the source of truth. When exclusive: true is set,
any member present on GitHub but absent from the YAML will be removed.
"""

import logging
import os
import sys
from argparse import ArgumentParser

import github
import yaml
from github import Github

logging.basicConfig(
    format="%(asctime)s - %(message)s", level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S"
)

API_TOKEN = os.environ.get("API_TOKEN")
ORGANIZATION = os.environ.get("ORGANIZATION", "SovereignCloudStack")


def load_data(data_file: str) -> dict:
    with open(data_file) as f:
        return yaml.safe_load(f)


def remove_org_members(gh: Github, org_name: str, defined_logins: set, dry_run: bool) -> int:
    """Remove org members not defined in data.yaml. Returns number of removals."""
    org = gh.get_organization(org_name)
    removed = 0

    for member in org.get_members():
        login = member.login.lower()
        if login not in defined_logins:
            logging.info(f"Removing org member: {member.login}")
            if not dry_run:
                org.remove_from_members(member)
            removed += 1

    return removed


def remove_team_members(gh: Github, org_name: str, yaml_teams: list, dry_run: bool) -> int:
    """Remove team members/maintainers not defined in data.yaml for each team. Returns number of removals."""
    org = gh.get_organization(org_name)
    removed = 0

    defined_teams = {t["slug"]: t for t in yaml_teams}

    for gh_team in org.get_teams():
        slug = gh_team.slug
        if slug not in defined_teams:
            # Team not in YAML — skip (team creation/deletion is handled by Ansible)
            continue

        yaml_team = defined_teams[slug]
        yaml_members = {m.lower() for m in yaml_team.get("member", [])}
        yaml_maintainers = {m.lower() for m in yaml_team.get("maintainer", [])}
        yaml_all = yaml_members | yaml_maintainers

        for gh_member in gh_team.get_members():
            login = gh_member.login.lower()
            if login not in yaml_all:
                logging.info(f"Removing {gh_member.login} from team {slug}")
                if not dry_run:
                    gh_team.remove_membership(gh_member)
                removed += 1

    return removed


def main():
    parser = ArgumentParser(description="Remove GitHub org/team members not defined in data.yaml")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Report what would be removed without making any changes",
    )
    parser.add_argument(
        "--data-file",
        default=f"orgs/{ORGANIZATION}/data.yaml",
        help="Path to the data.yaml file",
    )
    args = parser.parse_args()

    if args.dry_run:
        logging.info("DRY RUN — no changes will be made")

    data = load_data(args.data_file)

    if not data.get("exclusive", False):
        logging.info("exclusive: false — skipping removal")
        sys.exit(0)

    defined_logins = {m["login"].lower() for m in data.get("members", [])}
    yaml_teams = data.get("teams", [])

    gh = Github(login_or_token=API_TOKEN)

    org_removals = remove_org_members(gh, ORGANIZATION, defined_logins, args.dry_run)
    team_removals = remove_team_members(gh, ORGANIZATION, yaml_teams, args.dry_run)

    total = org_removals + team_removals
    if total == 0:
        logging.info("No members to remove — everything is in sync")
    else:
        action = "Would remove" if args.dry_run else "Removed"
        logging.info(f"{action} {org_removals} org member(s) and {team_removals} team member(s)")

    sys.exit(0)


if __name__ == "__main__":
    main()
