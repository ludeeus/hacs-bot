"""Handle Bot automations."""
# pylint: disable=missing-docstring,line-too-long,broad-except
from aiogithubapi import AIOGitHub

from const import (
    CLOSED_ISSUE,
    CHECKS,
    GREETING_PR,
    LABEL_BACKEND,
    LABEL_DOCUMENTATION,
    LABEL_FRONTEND,
    LABEL_NEW_REPO,
    MULTIPLE_FILES_CHANGED,
)
from github_actions import IssueComment, IssueUpdate, Status


class Bot:
    """Bot Auotmations."""

    def __init__(self, session, token, event_data):
        """initialize."""
        self.session = session
        self.repository = None
        self.token = token
        self.event_data = event_data
        self.aiogithub = None
        self.issue_number = None
        self.submitter = None
        self.action = None
        self.issue_type = None
        self.issue_comment = None
        self.issue_update = None
        self.status = None

    async def execute(self):
        self.aiogithub = AIOGitHub(self.token, self.session)
        self.repository = await self.aiogithub.get_repo(
            self.event_data["repository"]["full_name"]
        )

        self.submitter = self.event_data["sender"]["login"]
        self.action = self.event_data["action"]

        if self.event_data.get("pull_request") is not None:
            print("We now know that this is a PR.")
            self.issue_type = "pr"
            self.submitter = self.event_data["pull_request"]["user"]["login"]
            self.issue_number = self.event_data["pull_request"]["number"]

        elif self.event_data.get("issue") is not None:
            print("We now know that this is a issue.")
            self.issue_type = "issue"
            self.issue_number = self.event_data["issue"]["number"]

        self.issue_comment = IssueComment(self.issue_number, self.repository)
        self.issue_update = IssueUpdate(self.issue_number, self.repository)

        if self.issue_type == "pr":
            self.status = Status(self.event_data, self.session, self.token)
            await self.handle_pr()
        elif self.issue_type == "issue":
            await self.handle_issue()

        await self.issue_update.update()

    async def handle_pr(self):
        if self.action == "opened":
            self.issue_comment.message = GREETING_PR.format(self.submitter)
            await self.issue_comment.create()

        if self.event_data["pull_request"]["base"]["ref"] == "data":
            await self.pr_data_new_default_repository()

        files, added, removed = await self.get_pr_diff_data()
        print(f"{files} - {added}, {removed}")

        if "/docs/" in files:
            self.issue_update.labels.append(LABEL_DOCUMENTATION)
        if "/custom_components/hacs/frontend/" in files:
            self.issue_update.labels.append(LABEL_FRONTEND)
        if ".py" in files:
            self.issue_update.labels.append(LABEL_BACKEND)

    async def handle_issue(self):
        if self.action == "opened":
            known, description = self.issue_is_known()
            if known:
                self.issue_update.state = "closed"
                self.issue_comment.message = description
                await self.issue_comment.create()
                return

        if self.action == "created":
            if (
                self.event_data.get("comment") is not None
                and self.event_data["issue"].get("pull_request") is None
            ):
                if self.event_data["issue"]["state"] == "closed":
                    if (
                        self.event_data["issue"]["closed_at"]
                        != self.event_data["comment"]["created_at"]
                    ):
                        print("Someone commented on a closed issue!")
                        self.issue_update.state = "closed"
                        self.issue_comment.message = CLOSED_ISSUE.format(self.submitter)
                        await self.issue_comment.create()
                        return

    def issue_is_known(self):
        from known_issues import KNOWN_ISSUES

        for known_issue in KNOWN_ISSUES:
            all_checks_is_present = True
            for check in known_issue["check"]:
                if not all_checks_is_present:
                    continue
                if check not in self.event_data["issue"]["body"]:
                    all_checks_is_present = False
            if all_checks_is_present:
                return True, known_issue["description"]
        return False, None

    async def get_pr_diff_data(self):
        files = []
        added = []
        removed = []

        diff = await self.session.get(
            f"https://patch-diff.githubusercontent.com/raw/{self.event_data['repository']['full_name']}/pull/{self.issue_number}.diff"
        )
        diff = await diff.text()

        for line in diff.split("\n"):
            if line.startswith("+++ b"):
                files.append(line.split("+++ b")[1])
            elif line.startswith("-"):
                if '"' in line:
                    removed.append(line.split('"')[1])
            elif line.startswith("+"):
                if '"' in line:
                    added.append(line.split('"')[1])

        return files, added, removed

    async def pr_data_new_default_repository(self):
        """Handle PR's to the data branch."""
        if self.action not in ["opened", "synchronize", "labeled"]:
            return
        if self.action == "labeled":
            if self.event_data["label"]["name"] != "recheck":
                return
        self.issue_update.labels.append(LABEL_NEW_REPO)

        files, added, removed = await self.get_pr_diff_data()
        for repo in removed:
            if repo in added:
                added.remove(repo)

        for repo in added:
            if not "/" in repo:
                added.remove(repo)

        if len(files) > 1 or len(added) > 1:
            self.issue_update.labels.append("Manual review required")
            self.issue_comment.message = MULTIPLE_FILES_CHANGED
            await self.issue_comment.create()
            return

        failed = []

        repo = added[0]
        repochecks = CHECKS
        repository = None
        try:
            repository = await self.aiogithub.get_repo(repo)
            repochecks["exist"]["state"] = True
            repochecks["exist"]["url"] = f"https://github.com/{repo}"
            repochecks["fork"]["state"] = not repository.fork
            repochecks["owner"]["state"] = repo.split("/")[0] == self.submitter
        except Exception:
            pass

        if repository is not None:
            repochecks = await self.check_common(repository, repochecks)

        can_fail = ["description", "info", "readme"]

        for check in repochecks:
            if repochecks[check]["state"]:
                await self.status.create(
                    "success",
                    repochecks[check]["description"],
                    target_url=repochecks[check]["url"],
                )
            else:
                if check in can_fail:
                    failed.append([repository, check])
                    await self.status.create(
                        "error",
                        repochecks[check]["description"],
                        "This is not blocking",
                        target_url=repochecks[check]["url"],
                    )
                else:
                    failed.append([repository, check])
                    await self.status.create(
                        "error",
                        repochecks[check]["description"],
                        target_url=repochecks[check]["url"],
                    )

        if not failed:
            print("All is good, approving the PR.")
            endpoint = f"https://api.github.com/repos/{self.event_data['repository']['full_name']}/pulls/{self.issue_number}/reviews"
            data = {
                "commit_id": self.event_data["pull_request"]["head"]["sha"],
                "event": "APPROVE",
            }
            await self.session.post(
                endpoint,
                json=data,
                headers={
                    "Accept": "application/vnd.github.v3.raw+json",
                    "Authorization": f"token {self.token}",
                },
            )

    async def check_common(self, repository, repochecks):
        rootcontent = await repository.get_contents("")
        readme_files = ["readme", "readme.md"]
        info_files = ["info", "info.md"]

        repochecks["desc"] = {
            "state": repository.description != "",
            "description": "Repository have description",
            "url": None,
        }

        repochecks["readme"] = {
            "state": False,
            "description": "Repository have a readme file",
            "url": None,
        }

        repochecks["info"] = {
            "state": False,
            "description": "Repository have a info file",
            "url": "https://custom-components.github.io/hacs/developer/general/#enhance-the-experience",
        }

        for filename in rootcontent:
            if filename.name.lower() in readme_files:
                repochecks["readme"]["state"] = True
            if filename.name.lower() in info_files:
                repochecks["info"]["state"] = True

        return repochecks
