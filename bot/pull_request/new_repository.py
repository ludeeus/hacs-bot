"""Handle new repositories."""
# pylint: disable=no-name-in-module, broad-except, missing-docstring
from pull_request.checks.new_repo_common import new_repo_common
from pull_request.checks.summary import summary


async def new_repository(self, files, added, removed):
    """Handle PR's to the data branch."""
    files, added, removed = files, added, removed
    if self.action not in ["opened", "synchronize", "labeled"]:
        return
    if self.action == "labeled":
        if self.event_data["label"]["name"] != "recheck":
            return
    self.issue_update.labels.append(self.const.LABEL_NEW_REPO)

    for repo in removed:
        if repo in added:
            added.remove(repo)

    for repo in added:
        if not "/" in repo:
            added.remove(repo)

    if len(files) > 1 or len(added) > 1:
        if self.const.LABEL_MANUAL_REVIEW not in self.issue_update.labels:
            self.issue_update.labels.append(self.const.LABEL_MANUAL_REVIEW)
            self.issue_comment.message = self.const.MULTIPLE_FILES_CHANGED
            await self.issue_comment.create()
        return

    failed = []

    repo = added[0]
    self.category = files[0].split("/")[-1]
    repochecks = {}
    for check in self.const.CHECKS:
        repochecks[check] = self.const.CHECKS[check]
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
        releases = await repository.get_releases()
        if releases:
            repository.attributes["ref"] = f"tags/{releases[0].tag_name}"
        else:
            repository.attributes["ref"] = repository.default_branch
        repochecks = await new_repo_common(repository, repochecks, files)

    for check in repochecks:
        if repochecks[check]["state"]:
            await self.status.create(
                "success",
                repochecks[check]["description"],
                target_url=repochecks[check]["url"],
            )
        else:
            failed.append([repository, check])
            await self.status.create(
                "error",
                repochecks[check]["description"],
                target_url=repochecks[check]["url"],
            )

    await summary(self, repository, repochecks)
    print("Adding review.")
    endpoint = f"https://api.github.com/repos/{self.event_data['repository']['full_name']}/pulls/{self.issue_number}/reviews"
    data = {
        "commit_id": self.event_data["pull_request"]["head"]["sha"],
        "event": "APPROVE",
    }
    if failed:
        data["event"] = "REQUEST_CHANGES"
        data["body"] = "One (or more) check(s) failed\nTo get information about what it is, click the 'Details' link\nFor genreal documentation about requirements [look here](https://hacs.netlify.com/developer/general/)."

        if self.const.LABEL_MANUAL_REVIEW not in self.issue_update.labels:
            self.issue_update.labels.append(self.const.LABEL_MANUAL_REVIEW)

    await self.session.post(
        endpoint,
        json=data,
        headers={
            "Accept": "application/vnd.github.v3.raw+json",
            "Authorization": f"token {self.token}",
        },
    )


    