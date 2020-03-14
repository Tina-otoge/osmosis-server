from discord_webhook import DiscordWebhook
from discord import webhooks
from flask import current_app


def hook(content, name, files=[], username=None, avatar_url=None):
    if current_app.debug:
        name = 'debug'
    if isinstance(content, str):
        content = [content]
    links = webhooks.get(name)
    if isinstance(links, str):
        links = [links]
    for link in links:
        webhook = DiscordWebhook(link)
        webhook.username = username
        webhook.avatar_url = avatar_url
        for file in files:
            webhook.add_file(file=file['data'], filename=file['name'])
        for msg in content:
            webhook.content = msg
            webhook.execute()
