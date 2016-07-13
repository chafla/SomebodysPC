import discord
import json
import logging
import re
import utils



# TODO: Consider adding welcome message
# TODO: Consider using pickle to save data



try:
    with open('config.json', 'r+') as json_config_info:
        config = json.load(json_config_info)
except IOError:
    print("config.json not found in running directory.")
    exit(0)

try:
    with open('auth.json', 'r+') as json_auth_info:
        auth = json.load(json_auth_info)
except IOError:
    print("auth.json not found in running directory.")
    exit(0)

discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.CRITICAL)
log = logging.getLogger()
log.setLevel(logging.INFO)
handler = logging.FileHandler(filename='goPC.log', encoding='utf-8', mode='w')
log.addHandler(handler)

team_aliases = {
    "Valor": ["Valor", "Team Valor", "Red", "Team Red"],
    "Instinct": ["Instinct", "Team Instinct", "Yellow", "Team Yellow"],
    "Mystic": ["Mystic", "Team Mystic", "Blue", "Team Blue"]
}
full_list = ["Valor", "Team Valor", "Red", "Team Red", "Instinct", "Team Instinct", "Yellow", "Team Yellow",
             "Mystic", "Team Mystic", "Blue", "Team Blue"]  # Kinda bad practice, but w/e

team_list = ["Valor", "Mystic", "Instinct"]

bot_info_message = '''
This bot was created by Luc | ルカリオ#5653, who you can probably find in the /r/PokemonGO server, among a few others.\n
You can find this bot's code at https://github.com/chafla/SomebodysPC.\n
'''

help_message = '''
`%team [team name]`: Assign yourself to a team.\n
'''


client = discord.Client()


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')



@client.event
async def on_message(message):

    if message.author.id == client.user.id:
        return

    elif message.content.startswith("%team"):
        # TODO: Add possibility for channel-specific blacklisting here
        # TODO: Add ability for users to use an alias too
        # TODO: Add ability for server owners to possibly set roles to things that aren't V/M/I, but still use default roles
        # if role in full_list and role in message.server.roles:
        entered_team = message.content[6:]
        role = discord.utils.get(message.server.roles, name=entered_team)
        if (entered_team not in team_aliases) or (role is None):
            # If the role wasn't found by discord.utils.get() or is a role that we don't want to add:
            await client.send_message(message.channel, "Team doesn't exist. Teams that do are `Mystic`, `Valor`, and `Instinct`.\nBlue is Mystic, red is Valor, and yellow is Instinct.")

        elif role in message.author.roles:
            # If they already have the role
            await client.send_message(message.channel, "You already have this role. If you want to change, message a moderator.")

        else:
            try:
                await client.add_roles(message.author, role)
                await client.send_message(message.channel, "Successfully added role `{0}`.".format(role.name))
            except discord.Forbidden:
                await client.send_message(message.channel, "I need to be granted the Manage Permissions role first.")
            except discord.HTTPException:
                await client.send_message(message.channel, "Something went wrong, please try again.")

    elif message.content.startswith("%botinfo"):
        await client.send_message(message.channel, "Bot created b")

    elif message.content.startswith("%help") or message.content.startswith("%commands"):
        await client.send_message(message.channel, help_message)


    # TODO: ADD SERVER SETTINGS CONFIG
    # TODO: Add info command about the bot
    # TODO: Add a %commands or %help
    # TODO: Add whitelist command that makes %team only work in certain channels, then save the channel.id to a text file.





