"""Handle new repositories."""
# pylint: disable=no-name-in-module, broad-except, missing-docstring
from pull_request.checks.new_repo_common import new_repo_common
from pull_request.checks.summary import summary


async def new_repository(self, files, added, removed):
    """Handle PR's to the data branch."""
    files, added, removed = files, added, removed
    if self.action not in ["opened", "reopened", "synchronize", "labeled"]:
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

    if len(files) > 1:
        self.issue_comment.message = self.const.MULTIPLE_FILES_CHANGED
        await self.issue_comment.create()
        return

    elif len(added) > 1:
        self.issue_comment.message = self.const.MULTIPLE_REPOS_ADDED
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
    await summary(self, repository, repochecks, failed)
