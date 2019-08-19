"""Checks for plugins."""
# pylint: disable=no-name-in-module, broad-except, missing-docstring


async def new_repo_plugin(repository, repochecks):

    repochecks = await check_import_type(repository, repochecks)
    if not repochecks["import type"]["state"]:
        return repochecks

    repochecks = await verify_plugin_location(repository, repochecks)
    if not repochecks["plugin location"]["state"]:
        return repochecks

    return repochecks

async def check_import_type(repository, repochecks):
    repochecks["import type"] = {
        "state": False,
        "description": "The repository README have info about how the plugin should be defined.",
        "url": "https://hacs.netlify.com/developer/plugin/#import-type",
    }
    readme = None
    import_type = None
    readme_files = ["readme", "readme.md"]
    try:
        root = await repository.get_contents("", repository.attributes['ref'])
        for file in root:
            if file.name.lower() in readme_files:
                readme = await repository.get_contents(file.name, repository.attributes['ref'])
                break
    except Exception:
        return repochecks

    if readme is None:
        return repochecks

    readme = readme.content
    for line in readme.splitlines():
        if "type: module" in line:
            import_type = "module"
            break
        elif "type: js" in line:
            import_type = "js"
            break

    if import_type is not None:
        repochecks["import type"]["state"] = True
    return repochecks


async def verify_plugin_location(repository, repochecks):
    repochecks["plugin location"] = {
        "state": False,
        "description": "The location of the plugin is in one of the expected locations",
        "url": "https://hacs.netlify.com/developer/plugin/#repository-structure",
    }

    possible_locations = ["dist", "release", ""]
    plugin_name = repository.full_name.split("/")[1]
    for location in possible_locations:
        try:
            objects = []
            files = []
            if location != "release":
                try:
                    objects = await repository.get_contents(location, repository.attributes['ref'])
                except Exception:
                    continue
            else:
                releases = await repository.get_releases()
                if releases:
                    objects = releases[0].assets

            for item in objects:
                if item.name.endswith(".js"):
                    files.append(item.name)

            # Handler for plug requirement 3
            valid_filenames = [
                f"{plugin_name.replace('lovelace-', '')}.js",
                f"{plugin_name}.js",
                f"{plugin_name}.umd.js",
                f"{plugin_name}-bundle.js",
            ]
            for name in valid_filenames:
                if name in files:
                    repochecks["plugin location"]["state"] = True
                    return repochecks
        except Exception:
            pass
