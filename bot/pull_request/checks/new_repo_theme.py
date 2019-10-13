"""Checks for themes."""
# pylint: disable=no-name-in-module, broad-except, missing-docstring


async def new_repo_theme(repository, repochecks):

    repochecks = await theme_exsist(repository, repochecks)
    if not repochecks["theme exist"]["state"]:
        return repochecks

    return repochecks


async def theme_exsist(repository, repochecks):
    repochecks["theme exist"] = {
        "state": False,
        "description": "theme exist in the themes directory",
        "url": "https://hacs.netlify.com/docs/publish/theme#repository-structure",
    }
    try:
        themedir = await repository.get_contents("themes", repository.attributes['ref'])
        if not isinstance(themedir, list):
            return repochecks

        for filename in themedir:
            if filename.name.endswith(".yaml"):
                repochecks["theme exist"]["state"] = True
                repochecks["theme exist"]["url"] = filename.attributes["html_url"]
                break
    except Exception:
        return repochecks
    return repochecks
