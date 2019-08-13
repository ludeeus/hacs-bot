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

        if self.event_data.get("pull_request") is not None:
            print("We now know that this is a PR.")
            self.issue_type = "pr"
            self.issue_number = self.event_data["number"]

        elif self.event_data.get("issue") is not None:
            print("We now know that this is a issue.")
            self.issue_type = "issue"
            self.issue_number = self.event_data["issue"]["number"]

        self.submitter = self.event_data["sender"]["login"]
        self.action = self.event_data["action"]

        self.issue_comment = IssueComment(self.issue_number, self.repository)
        self.issue_update = IssueUpdate(self.issue_number, self.repository)
        self.status = Status(self.event_data, self.session, self.token)

        if self.issue_type == "pr":
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
            if self.event_data.get("comment") is not None:
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
            if not all_checks_is_present:
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
        if self.action not in ["opened", "synchronize"]:
            return
        self.issue_update.labels.append(LABEL_NEW_REPO)

        files, added, removed = await self.get_pr_diff_data()
        for repo in removed:
            if repo in added:
                added.remove(repo)

        for repo in added:
            if not "/" in repo:
                added.remove(repo)

        if len(files) > 1:
            self.issue_update.labels.append("Manual review required")
            self.issue_comment.message = MULTIPLE_FILES_CHANGED

        issue_comment = "# Repository checks\n\n"
        issue_comment += "These checks are automatic.\n\n"

        for repo in added:
            repochecks = CHECKS
            try:
                repository = await self.aiogithub.get_repo(repo)
                repochecks["exists"]["state"] = True
                print(repository.fork)
                repochecks["fork"]["state"] = not repository.fork
                repochecks["owner"]["state"] = repo.split("/")[0] == self.submitter
            except Exception:
                pass

            issue_comment += f"## Checks for `{repo}`\n\n"
            issue_comment += f"[Repository link](https://github.com/{repo})\n\n"
            issue_comment += "Status | Check\n-- | --\n"
            for check in repochecks:
                issue_comment += "✔️" if repochecks[check]["state"] else "❌"
                issue_comment += f" | {check.capitalize()}\n"
            issue_comment += "\n"

            for check in repochecks:
                if repochecks[check]["state"]:
                    await self.status.create("success", repochecks[check]["description"])
                else:
                    await self.status.create("error", repochecks[check]["description"], repochecks[check]["url"])

        comments = await self.repository.list_issue_comments(self.issue_number)
        comment_number = None
        for comment in comments:
            if "# Repository checks\n\n" in comment.body:
                comment_number = comment.id
                break

        self.issue_comment.message = issue_comment
        if comment_number is None:
            await self.issue_comment.create()
        else:
            await self.issue_comment.update(comment_number)
