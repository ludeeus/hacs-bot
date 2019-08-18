"""Checks for python scripts."""
# pylint: disable=no-name-in-module, broad-except, missing-docstring


async def new_repo_python_script(repository, repochecks):

    repochecks = await python_script_exsist(repository, repochecks)
    if not repochecks["python_script exist"]["state"]:
        return repochecks

    return repochecks


async def python_script_exsist(repository, repochecks):
    repochecks["python_script exist"] = {
        "state": False,
        "description": "python_script exist in the python_script directory",
        "url": "https://hacs.netlify.com/developer/python_script/#repository-structure",
    }
    try:
        psdir = await repository.get_contents("python_script")
        if not isinstance(psdir, list):
            return repochecks

        for filename in psdir:
            if filename.name.endswith(".py"):
                repochecks["python_script exist"]["state"] = True
                repochecks["python_script exist"]["url"] = filename.attributes["html_url"]
                break
    except Exception:
        return repochecks
    return repochecks
