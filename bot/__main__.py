"""HACS Bot"""
# pylint: disable=missing-docstring,line-too-long,broad-except
import time
import jwt
from aiohttp import ClientSession, web

from bot import Bot
from const import APP_ID, REPOSITORY


async def repo_not_accepted(event_data, token, session):
    from const import REPO_NOT_ACCEPTED_BODY, REPO_NOT_ACCEPTED_TITLE

    print(f"Repository {event_data['repository']['full_name']} is not accepted.")
    endpoint = (
        f"https://api.github.com/repos/{event_data['repository']['full_name']}/issues"
    )

    data = {
        "title": REPO_NOT_ACCEPTED_TITLE,
        "body": REPO_NOT_ACCEPTED_BODY.format(
            event_data["repository"]["owner"]["login"]
        ),
        "assignees": [event_data["repository"]["owner"]["login"]],
    }

    await session.post(
        endpoint,
        json=data,
        headers={
            "Accept": "application/vnd.github.v3.raw+json",
            "Authorization": f"token {token}",
        },
    )


def get_jwtoken():
    """Create a JWT (Bearer) Token."""
    with open("/cert/hacsbot.pem", "rt") as cert:
        pem = cert.read()

    payload = {}
    payload["exp"] = int(time.time()) + 500
    payload["iat"] = int(time.time())
    payload["iss"] = APP_ID

    print(payload)

    encoded = jwt.encode(payload, pem, algorithm="RS256")
    return encoded.decode("utf-8")


async def bot_handler(request):
    """Handle POST request."""
    event_data = await request.json()
    if event_data.get("comment") is not None:
        if event_data["comment"]["user"]["type"] == "Bot":
            # Skip bots
            return web.Response(status=200)
    jwtoken = get_jwtoken()
    async with ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {jwtoken}",
            "Accept": "application/vnd.github.machine-man-preview+json",
        }
        token = await session.post(
            f"https://api.github.com/app/installations/{event_data['installation']['id']}/access_tokens",
            headers=headers,
        )
        token = await token.json()
        print(token)
        if event_data["repository"]["full_name"] != REPOSITORY:
            await repo_not_accepted(event_data, token["token"], session)
            # return web.Response(status=200)
        handler = Bot(session, token["token"], event_data)
        await handler.execute()
    return web.Response(status=200)


APP = web.Application()
APP.add_routes([web.post("/", bot_handler)])

web.run_app(APP, host="0.0.0.0")
