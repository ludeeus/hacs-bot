"""GitHub Actrions."""
# pylint: disable=missing-docstring,line-too-long,broad-except
from aiogithubapi.repository import AIOGithubRepository
from const import FOOTER, NAME


class IssueComment:
    def __init__(self, issue_number: int, repository: AIOGithubRepository):
        self.issue_number = issue_number
        self.repository = repository
        self.message = None

    async def update(self, comment_number):
        self.message += FOOTER
        print(f"Updating comment to #{self.issue_number}")
        await self.repository.update_comment_on_issue(comment_number, self.message)

    async def create(self):
        self.message += FOOTER
        print(f"Adding comment to #{self.issue_number}")
        await self.repository.comment_on_issue(self.issue_number, self.message)


class IssueUpdate:
    def __init__(self, issue_number: int, repository: AIOGithubRepository):
        self.issue_number = issue_number
        self.repository = repository
        self.labels = []
        self.assignees = []
        self.state = None

    async def update(self):
        print(f"updating #{self.issue_number}")
        if self.labels:
            await self.repository.update_issue(self.issue_number, labels=self.labels)

        if self.assignees:
            await self.repository.update_issue(
                self.issue_number, assignees=self.assignees
            )

        if self.state:
            await self.repository.update_issue(self.issue_number, state=self.state)


class Status:
    def __init__(self, event_data: dict, session, token):
        self.event_data = event_data
        self.repo = event_data["repository"]["full_name"]
        self.sha = event_data["pull_request"]["head"]["sha"]
        self.session = session
        self.token = token

    async def create(self, state, context, description=None, target_url=None):

        endpoint = f"https://api.github.com/repos/{self.repo}/statuses/{self.sha}"

        data = {}
        data["state"] = state
        data["context"] = f"{NAME}: {context}"
        if description is not None:
            data["description"] = description
        if target_url is not None:
            data["target_url"] = target_url

        await self.session.post(
            endpoint,
            json=data,
            headers={
                "Accept": "application/vnd.github.v3.raw+json",
                "Authorization": f"token {self.token}",
            },
        )
