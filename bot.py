#!/usr/bin/env python3.5
import discord
import json
import logging
import re
import utils
from os import path
from sys import exit



# TODO: Consider adding welcome message
# TODO: Consider using pickle to save data



try:
    with open('config.json', 'r+') as json_config_info:
        config = json.load(json_config_info)
except IOError:
    exit("config.json not found in running directory.")

try:
    with open('auth.json', 'r+') as json_auth_info:
        auth = json.load(json_auth_info)
except IOError:
    exit("auth.json not found in running directory.")

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
This bot was created by Luc | ルカリオ#5653, who you can probably find in the /r/PokemonGO server, among a few others.
You can find this bot's code at https://github.com/chafla/SomebodysPC.
'''

help_message = '''
`%team [team name]`: Assign yourself to a team.
'''


client = discord.Client()


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_server_join(server):
    with open("server_data/{0}.json".format(server.id), "w", encoding="utf-8") as tmp:
        json.dump(utils.init_server_datafile, tmp)


@client.event
async def on_message(message):

    if message.author.id == client.user.id:
        return

    elif message.content.startswith("%team"):
        with open("server_data/{0}".format(message.server.id), "r", encoding="utf-8") as tmp:
            temp_data = json.load(tmp)
            chan_whitelist = temp_data["team_cl_wl"]

            # First things first, determine if it's a PM or not.
            # We need to get the server object that the member wants a role in. If not PM, it's ez.

        if not message.channel.is_private: # Not a PM.

            # Is the channel whitelisted?

            if chan_whitelist is None:  # Nothing in the whitelist, needs to come first
                server = message.server
            elif message.channel.id not in chan_whitelist:
                if len(temp_data) == 1:
                    await client.send_message(message.channel, "Please put team requests in <#{0}>".format(chan_whitelist[0]))
                    return
                elif len(temp_data) > 1:  # Grammar for grammar's sake, any more are ignored.
                    await client.send_message(message.channel,
                                              "Please put team requests in <#{0}> or : {1}".format(chan_whitelist[0], chan_whitelist[1]))
                    return
            else:
                server = message.server

            member = message.author

        else:  # Sent in a private message, so things might get tricky.
            servers_shared = []
            for server in client.servers:
                for member in server.members:
                    if member.id == message.author.id:
                        servers_shared.append(member.server.id)

            if servers_shared == 1:
                server = servers_shared[0]
            else:  # Wew, time for issues
                base_message = '''
                Oops, looks like I share more than one server with you.
                Which server would you like to set your rank in?
                Reply with the number of the server.
                '''
                i = 1

                def check(msg, i):
                    try:
                        if 0 > int(msg.content) >= i:
                            return True
                        else:
                            return False
                    except AttributeError or TypeError:  # In case what they return isn't convertible to an int
                        return False

                for svr in servers_shared:
                    base_message += "{0}: {1.name}\n".format(i, svr)

                msg = await client.wait_for_message(author=message.author, check=check)

                server = servers_shared[int(message.content) - 1]

            member = discord.utils.get(server.members, id=message.author.id)

        # TODO: Add ability for users to use an alias too
        # TODO: Add ability for server owners to possibly set roles to things that aren't V/M/I, but still use default roles
        # if role in full_list and role in message.server.roles:
        entered_team = message.content[6:]
        role = discord.utils.get(server.roles, name=entered_team)
        if (entered_team not in team_aliases) or (role is None):
            # If the role wasn't found by discord.utils.get() or is a role that we don't want to add:
            await client.send_message(message.channel, "Team doesn't exist. Teams that do are `Mystic`, `Valor`, and `Instinct`.\nBlue is Mystic, red is Valor, and yellow is Instinct.")

        elif role in member.roles:
            # If they already have the role
            await client.send_message(message.channel, "You already have this role. If you want to change, message a moderator.")

        else:
            try:
                await client.add_roles(member, role)
                await client.send_message(message.channel, "Successfully added role `{0}`.".format(role.name))
            except discord.Forbidden:
                await client.send_message(message.channel, "I need to be granted the Manage Permissions role first.")
            except discord.HTTPException:
                await client.send_message(message.channel, "Something went wrong, please try again.")

    elif message.content.startswith("%botinfo"):
        await client.send_message(message.channel, bot_info_message)

    elif message.content.startswith("%help") or message.content.startswith("%commands"):
        await client.send_message(message.channel, help_message)

    elif message.content.startswith("%whitelist"):
        if utils.check_perms(message):

            with open("server_data/{0}".format(message.server.id), "r", encoding="utf-8") as tmp:
                temp_data = json.load(tmp)
                temp_data["team_ch_wl"].append(message.channel.id)
            with open("server_data/{0}".format(message.server.id), "w", encoding="utf-8") as tmp:
                json.dump(temp_data, tmp)

    elif message.content.startswith("%unwhitelist"):
        if utils.check_perms(message):

            with open("server_data/{0}".format(message.server.id), "r", encoding="utf-8") as tmp:
                temp_data = json.load(tmp)
                temp_data["team_ch_wl"].pop(message.channel.id)
            with open("server_data/{0}".format(message.server.id), "w", encoding="utf-8") as tmp:
                json.dump(temp_data, tmp)

    # TODO: ADD SERVER SETTINGS CONFIG
    # TODO: Add a %commands or %help
    # TODO: Add whitelist command that makes %team only work in certain channels, then save the channel.id to a text file.





