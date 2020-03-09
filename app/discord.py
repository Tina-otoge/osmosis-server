from discord_webhook import DiscordWebhook
from discord import webhooks


def hook(content, links=None, files=[], username=None, avatar_url=None):
    if isinstance(content, str):
        content = [content]
    if links is None:
        links = webhooks
    for link in links:
        webhook = DiscordWebhook(link)
        webhook.username = username
        webhook.avatar_url = avatar_url
        for file in files:
            webhook.add_file(file=file['data'], filename=file['name'])
        for msg in content:
            webhook.content = msg
            webhook.execute()
