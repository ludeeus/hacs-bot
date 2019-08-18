"""Checks for appdaemon apps."""
# pylint: disable=no-name-in-module, broad-except, missing-docstring


async def new_repo_appdaemon(repository, repochecks):

    repochecks = await app_directory_exsist(repository, repochecks)
    if not repochecks["app exist"]["state"]:
        return repochecks

    return repochecks


async def app_directory_exsist(repository, repochecks):
    repochecks["app exist"] = {
        "state": False,
        "description": "App exist in the apps directory",
        "url": "https://hacs.netlify.com/developer/appdaemon/#repository-structure",
    }
    try:
        appdir = await repository.get_contents("apps", repository.attributes['ref'])
        if not isinstance(appdir, list):
            return repochecks

        appdir = await repository.get_contents(appdir[0].path, repository.attributes['ref'])
        for filename in appdir:
            if filename.name.endswith(".py"):
                repochecks["app exist"]["state"] = True
                repochecks["app exist"]["url"] = filename.attributes["html_url"]
                break
    except Exception:
        return repochecks
    return repochecks
