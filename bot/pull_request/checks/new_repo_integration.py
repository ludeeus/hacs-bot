"""Checks for integrations."""
# pylint: disable=no-name-in-module, broad-except, missing-docstring


async def new_repo_integration(repository, repochecks):

    repochecks = await integration_directory_exsist(repository, repochecks)
    if not repochecks["integration exist"]["state"]:
        return repochecks


    repochecks = await integration_manifest_exsist(repository, repochecks)
    if not repochecks["manifest.json"]["state"]:
        return repochecks

    return repochecks


async def integration_directory_exsist(repository, repochecks):
    repochecks["integration exist"] = {
        "state": False,
        "description": "Integration exist in the custom_component directory",
        "url": "https://hacs.netlify.com/developer/integration/#repository-structure",
    }
    try:
        ccdir = await repository.get_contents("custom_components")
        if not isinstance(ccdir, list):
            return repochecks
        repochecks["integration exist"]["state"] = True
        repochecks["integration exist"]["url"] = ccdir[0].attributes["html_url"]
    except Exception:
        return repochecks
    return repochecks

async def integration_manifest_exsist(repository, repochecks):
    repochecks["manifest.json"] = {
        "state": False,
        "description": "Integration have a manifest.json file",
        "url": "https://hacs.netlify.com/developer/integration/#manifestjson",
    }
    try:
        ccdir = await repository.get_contents("custom_components")
        manifest_path = f"{ccdir[0].path}/manifest.json"
        manifest = await repository.get_contents(manifest_path)
        repochecks["manifest.json"]["state"] = True
        repochecks["manifest.json"]["url"] = manifest.attributes["html_url"]
    except Exception:
        return repochecks
    return repochecks
