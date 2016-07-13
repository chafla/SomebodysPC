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

owner_message = '''
Hi, thanks for adding me!
If you would like me to create roles, you can post %init, and I will create roles for the server that work with me.
Otherwise, the role names that I use are `Valor`, `Mystic`, and `Instinct` (case sensitive).
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
    logging.log("INFO", "Joined new server {0}".format(server.id))
    # TODO: Add ability for bot to create roles on its own.

    await client.send_message(server.owner, owner_message)


@client.event
async def on_message(message):

    if message.author.id == client.user.id:
        return

    elif message.content.startswith("%team"):

            # First things first, determine if it's a PM or not.
            # We need to get the server object that the member wants a role in. If not PM, it's ez.

        if not message.channel.is_private: # Not a PM.

            # Is the channel whitelisted?
            with open(r"server_data/{0}.json".format(message.server.id), "r+", encoding="utf-8") as tmp:
                temp_data = json.load(tmp)
                chan_whitelist = temp_data["team_ch_wl"]

            if chan_whitelist is None:  # Nothing in the whitelist, needs to come first
                pass
            elif message.channel.id not in chan_whitelist:
                if len(chan_whitelist) == 1:
                    await client.send_message(message.channel, "Please put team requests in <#{0}>".format(chan_whitelist[0]))
                    return
                elif len(chan_whitelist) > 1:  # Grammar for grammar's sake, any more are ignored.
                    await client.send_message(message.channel,
                                              "Please put team requests in <#{0}> or <#{1}>".format(chan_whitelist[0], chan_whitelist[1]))
                    return
            else:
                pass

            member = message.author
            server = message.server

        else:  # Sent in a private message, so things might get tricky.
            servers_shared = []
            for server in client.servers:
                for member in server.members:
                    if member.id == message.author.id:
                        servers_shared.append(member.server)
            print(servers_shared)
            if len(servers_shared) == 0:
                await client.send_message(message.channel, "Something is wrong. We don't appear to share any servers.")
                return

            elif len(servers_shared) == 1:
                server = servers_shared[0]
            else:  # Wew, time for issues
                base_message = '''
Oops, looks like I share more than one server with you. Which server would you like to set your role in? Reply with the digit of the server.\n
'''
                i = 1

                for svr in servers_shared:
                    base_message += "{0}: {1.name}\n".format(i, svr)
                    i += 1

                await client.send_message(message.channel, base_message)

                server_selection = await utils.get_message(client, message, i, base_message)
                print(server_selection)
                try:
                    server = servers_shared[int(server_selection) - 1]
                except IndexError:
                    await client.send_message(message.channel, "Try %team again.")
                    return

            member = discord.utils.get(server.members, id=message.author.id)

        # TODO: Add ability for users to use an alias too
        # TODO: Add ability for server owners to possibly set roles to things that aren't V/M/I, but still use default roles
        # if role in full_list and role in message.server.roles:
        entered_team = message.content[6:]
        role = discord.utils.get(server.roles, name=entered_team)

        for r in member.roles:
            if r.name in team_list:
                # If a role in the user's list of roles matches one of those we're checking
                await client.send_message(message.channel,
                                          "You already have a team role. If you want to switch, message a moderator.")
                return

        if (entered_team not in team_list) or (role is None):
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

            with open("server_data/{0}.json".format(message.server.id), "r", encoding="utf-8") as tmp:
                temp_data = json.load(tmp)
                temp_data["team_ch_wl"].append(message.channel.id)
            with open("server_data/{0}.json".format(message.server.id), "w", encoding="utf-8") as tmp:
                json.dump(temp_data, tmp)
            await client.send_message(message.channel, "Channel successfully whitelisted.")

    elif message.content.startswith("%unwhitelist"):
        if utils.check_perms(message):

            with open("server_data/{0}.json".format(message.server.id), "r", encoding="utf-8") as tmp:
                temp_data = json.load(tmp)
                temp_data["team_ch_wl"].pop(message.channel.id)
            with open("server_data/{0}.json".format(message.server.id), "w", encoding="utf-8") as tmp:
                json.dump(temp_data, tmp)
                await client.send_message(message.channel, "Channel successfully removed from the whitelist.")

    # TODO: ADD SERVER SETTINGS CONFIG



client.run(auth["token"])