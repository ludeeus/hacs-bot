"""Handle Bot automations."""
# pylint: disable=missing-docstring,line-too-long,broad-except,no-name-in-module
from aiogithubapi import AIOGitHub
import const as const
from github_actions import IssueComment, IssueUpdate, Status
from issue.issue import handle_issue
from pull_request.pull_request import handle_pull_request

class Bot:
    """Bot Auotmations."""

    def __init__(self, session, token, event_data):
        """initialize."""
        self.branch = None
        self.category = None
        self.session = session
        self.const = const
        self.repository = None
        self.token = token
        self.event_data = event_data
        self.aiogithub = None
        self.multiple = False
        self.issue_number = None
        self.submitter = None
        self.action = None
        self.common_fails = []
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
            await handle_pull_request(self)
        elif self.issue_type == "issue":
            await handle_issue(self)

        await self.issue_update.update()
