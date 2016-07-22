#!/usr/bin/env python3.5
import discord
import json
import logging
import utils
import messages
import mwclient
from sys import exit
from asyncio import sleep

wiki_base = 'bulbapedia.bulbagarden.net'
wiki_ua = 'Bills PC. /r/PokemonGO Discord Bot.'
wiki = mwclient.Site(('http', wiki_base), path='/w/', clients_useragent=wiki_ua)

try:
    with open('auth.json', 'r+') as json_auth_info:
        auth = json.load(json_auth_info)
except IOError:
    auth = None  # Tired of pycharm pointing it out
    exit("auth.json not found in running directory.")

discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.CRITICAL)
log = logging.getLogger()
log.setLevel(logging.INFO)
handler = logging.FileHandler(filename='goPC.log', encoding='utf-8', mode='w')
log.addHandler(handler)

help_message = messages.help_message
owner_message = messages.owner_message

server_info_message = '''
Server name: **{0.name}**
Server ID: **{0.id}**
Member Count: **{1}**
'''

client = discord.Client()

bot = utils.Bot(client)


@client.event
async def on_ready():
    bot.initializing = True
    print("Initializing server data...")
    bot.update_datafiles(client)  # Optional command that updates datafiles when there are changes to the json structure
    bot.init(client)  # Load the server datafiles, create objects. I frankly don't know how long this will take.
    print("Done.")
    bot.initializing = False
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_server_join(server):
    print("Joined {}".format(server.name))
    bot.add_new_server(client, server)
    await client.send_message(server.owner, owner_message)


@client.event
async def on_server_remove(server):
    print("Left {}".format(server.name))
    bot.remove_server(server)


@client.event
async def on_message(message):

    # TODO: Make a call for the server object here

    if message.author.id == client.user.id:
        return

    elif bot.initializing:
        # If people call while the objects are being handled, which might just not happen
        await client.send_message(message.channel, "Currently re-initializing, please try again later.")

    elif message.content.startswith("%team"):

        if message.content[6:] == "":
            # User didn't put in anything. Note that we might want to find a way to clarify the roles that do exist.
            await client.send_message(message.channel,
                                      "Usage is `%team [team name]`.")
            return

            # First things first, determine if it's a PM or not.
            # We need to get the server object that the member wants a role in. If not PM, it's ez.

        if not message.channel.is_private:  # Not a PM.

            server_obj = bot.servers[message.server.id]  # TODO: is it possible to just do bot.servers(id=message.server.id)?

            # Run checks to see if the message should go through or not

            whitelist = await server_obj.check_whitelist(message)
            pm_prefs = int(server_obj.pm_config)

            if pm_prefs == 1:  # Server owner has required roles be set by PMs.
                await client.send_message(message.channel, "The server owner has required that roles be set by PM.")
                return
            elif whitelist is not None:  # The channel was not in the whitelist.
                await client.send_message(message.channel, whitelist)
                return

            member = message.author
            server = message.server

        else:  # Sent in a private message, so things might get tricky.
            servers_shared = []
            for server in client.servers:
                for member in server.members:
                    if member.id == message.author.id:
                        servers_shared.append(member.server)
            if len(servers_shared) == 0:
                await client.send_message(message.channel, "Something is wrong. We don't appear to share any servers.")
                return

            elif len(servers_shared) == 1:
                server = servers_shared[0]
            else:  # Time for issues
                base_message = "Oops, looks like I share more than one server with you. Which server would you like to set your role in? Reply with the digit of the server.\n"
                i = 1

                for svr in servers_shared:
                    base_message += "{0}: {1.name}\n".format(i, svr)
                    i += 1

                await client.send_message(message.channel, base_message)

                server_selection = await utils.get_message(client, message, i, base_message)
                if server_selection > i:
                    await client.send_message(message.channel, "That number was too large, try %team again.")
                    return
                else:
                    try:
                        server = servers_shared[(int(server_selection) - 1)]
                    except IndexError:
                        await client.send_message(message.channel, "That number was too large, try %team again.")
                        return
                    # TODO: Fix possibility of IndexError

            member = discord.utils.get(server.members, id=message.author.id)
            try:
                server_obj = bot.servers[server.id]
            except KeyError:  # Datafile is missing or something, it's not there.
                await client.send_message(message.channel, "The server datafile appears to be nonexistent for some reason.")
                return

        # Now, actually handle and process the roles.

        entered_team = message.content[6:]
        role = discord.utils.get(server.roles, name=entered_team)
        allowed_roles = server_obj.roles  # allowed_roles used to be team_list
        if server_obj.exclusive == "0":
            # Needs to be an exclusive if (not elif) because it has a chance at not returning anything
            for r in member.roles:
                if r.name in allowed_roles:
                    # If a role in the user's list of roles matches one of those we're checking
                    # or if the server has exclusive roles enabled
                    await client.send_message(message.channel,
                                              "You already have a team role. If you want to switch, message a moderator.")
                    return
        if (server_obj.check_role(entered_team)) & (role is None):
            # Role does not exist on the server, but is in the team_list, so the server just isn't configured properly.
            await client.send_message(message.channel,
                                      "The role you're trying to add existed at some point, but does not anymore, or has since been renamed.")
            # TODO: Consider using IDs in self.roles for this very reason!

        elif (not server_obj.check_role(entered_team)) or (role is None):
            # If the role wasn't found by discord.utils.get() or is a role that we don't want to add, such as it not
            # being in the roles list:
            await client.send_message(message.channel, "Role isn't addable; " + server_obj.list_roles())

        elif role in member.roles:
            # If they already have the role
            await client.send_message(message.channel, "You already have this role. If you want to change, message a moderator.")

        else:
            try:
                await client.add_roles(member, role)
                await client.send_message(message.channel, "Successfully added role `{0}`.".format(role.name))
            except discord.Forbidden:
                # Something's wrong with permissions or the role hierarchy.
                await client.send_message(message.channel, "I don't have the `Manage Roles` permission, or the role you want me to assign is located above my own.\nRoles need to be located beneath my highest role in order for me to be able to assign them.")
            except discord.HTTPException:
                # Some random HTTP Exception, usually unpredictable.
                await client.send_message(message.channel, "Something went wrong, please try again.")

    # From here on out, don't let commands work in a PM.

    elif message.channel.is_private:
        return

    # Checks the Pokemon GO Wiki for information

    elif message.content.startswith("%wiki "):
        content = message.content.replace('%wiki ', '')
        page = wiki.pages[content].resolve_redirect()

        if not page.exists:
            await client.send_message(message.channel, "{} :warning: Couldn't find a page on **{}**".format(message.author.mention, content))
        else:
            await client.send_message(message.channel, "{} :candy: Found **{}**:\nhttp://{}/wiki/{}_".format(message.author.mention, page.name, wiki_base, page.name.replace(" ", "_")))

    # Bot info message, listing things such as the creator and link to github

    elif message.content.startswith("%botinfo"):
        await client.send_message(message.channel, bot.info_message)

    # List of commands

    elif message.content.startswith("%help") or message.content.startswith("%commands"):
        await client.send_message(message.channel, help_message)

    # Commands to (un)whitelist channels. Can only be run by someone with `Manage Server`.

    elif message.content.startswith("%whitelist"):
        if utils.check_perms(message):

            server_obj = bot.servers[message.server.id]

            if message.channel.id in server_obj.channel_whitelist:
                await client.send_message(message.channel, "This channel is already whitelisted.")
            else:

                with open("server_data/{0}.json".format(message.server.id), "r", encoding="utf-8") as tmp:
                    temp_data = json.load(tmp)
                    temp_data["team_ch_wl"].append(message.channel.id)
                with open("server_data/{0}.json".format(message.server.id), "w", encoding="utf-8") as tmp:
                    json.dump(temp_data, tmp)
                await client.send_message(message.channel, "Channel successfully whitelisted.")

    elif message.content.startswith("%unwhitelist"):
        if utils.check_perms(message):
            server_obj = bot.servers[message.server.id]
            if message.channel.id in server_obj.channel_whitelist:
                await client.send_message(message.channel, "This channel is already whitelisted.")
            else:
                with open("server_data/{0}.json".format(message.server.id), "r", encoding="utf-8") as tmp:
                    temp_data = json.load(tmp)
                    temp_data["team_ch_wl"].remove(message.channel.id)
                with open("server_data/{0}.json".format(message.server.id), "w", encoding="utf-8") as tmp:
                    json.dump(temp_data, tmp)
                    await client.send_message(message.channel, "Channel successfully removed from the whitelist.")

    # Adjust server PM preferences

    elif message.content.startswith('%pm'):
        if not utils.check_perms(message):
            await client.send_message(message.channel,
                                      "This command is accessible by users with the `Manage Server` permission.")
            return
        else:
            flag = message.content.split()[1]
            flag_prefs = {
                "optional": "0",
                "required": "1",
            }
            if flag not in flag_prefs:
                await client.send_message(message.channel, "`%pm [required/optional]` (server owner only): Optional is default, allowing role setting in server and PMs; required disables setting roles in the server; disabled disables setting roles in PMs.")
                return
            server_obj = bot.servers[message.server.id]
            server_obj.pm_config = flag_prefs[flag]
            server_obj.export_to_file()
            await client.send_message(message.channel, "Server PM preferences now set to {0}.".format(flag))

    # TODO: Add server config command that handles %pm and %role_config

    elif message.content.startswith("%role_config"):
        if not utils.check_perms(message):
            await client.send_message(message.channel,
                                      "This command is accessible by users with the `Manage Server` permission.")
            return
        else:
            flag = message.content.split()[1]
            flag_prefs = {
                "exclusive": "0",
                "multiple": "1",
            }
            if flag not in flag_prefs:
                await client.send_message(message.channel,
                                          "%role_\config [exclusive/multiple]__*: Setting to exclusive (default) only allows one role to be set per user. Setting to multiple allows users to set as many roles as they want.")
                return
            server_obj = bot.servers[message.server.id]
            server_obj.exclusive = flag_prefs[flag]
            server_obj.export_to_file()
            await client.send_message(message.channel, "Server role preferences now set to {0}.".format(flag))

    # Small command listing information on the server itself.

    elif message.content.startswith('%server_info'):
        members = (i for i in message.server.members)
        member_count = sum(1 for _ in members)
        await client.send_message(message.channel, server_info_message.format(message.server, member_count))

    # Generate an oauth link so people can add it to their own servers.

    elif message.content.startswith('%invite'):
        oauth_url = discord.utils.oauth_url(auth["client_id"], utils.required_perms)
        await client.send_message(message.channel, "Add me to a server by clicking this link: {}".format(oauth_url))

    # Create roles in server.

    elif message.content.startswith("%create_roles"):
        if utils.check_perms(message):

            # First, check to make sure the server doesn't already have the roles.

            server_obj = bot.servers[message.server.id]

            for role in message.server.roles:
                if role.name in server_obj.base_roles:
                    await client.send_message(
                        message.channel, "One or more default Pokemon GO team roles that I can use already exist on this server. Role creating aborted.")
                    return

            # That passed, create the roles using blank templates.

            # !!!
            # THESE ROLES HAVE TO BE AT LEAST BELOW THE ROLE THAT THE BOT HAS, OR ELSE IT CAN'T ASSIGN THEM DUE TO
            # ROLE HIERARCHY
            # Hopefully, creating the roles at position 0 and up should fix this.

            try:
                await client.send_message(message.channel, "Creating roles...")
                await client.create_role(message.server, name="Mystic", color=discord.Color.blue(),
                                         permissions=utils.team_perms, position=0)
                sleep(1)  # Rate limiting purposes
                await client.create_role(message.server, name="Instinct", color=discord.Color.gold(),
                                         permissions=utils.team_perms, position=1)
                sleep(1)
                await client.create_role(message.server, name="Valor", color=discord.Color.red(),
                                         permissions=utils.team_perms, position=2)
                await client.send_message(message.channel, "Blank roles successfully added.")
                server_obj.init_default_roles(message)
            except discord.Forbidden:
                await client.send_message(message.channel, "I don't have the `Manage Roles` permission.")
                return

    # Create a custom role for the server.

    elif message.content.startswith("%enable_role"):
        if utils.check_perms(message):
            server_obj = bot.get_server(server=message.server)
            role = server_obj.add_custom_role(message)
            if role is not None:
                await client.send_message(message.channel, "Role `{}` can now be added with %team.".format(role.name))
            else:
                await client.send_message(message.channel, "Couldn't find that role.")

    elif message.content.startswith("%disable_role"):
        if utils.check_perms(message):
            server_obj = bot.get_server(server=message.server)
            if server_obj.remove_custom_role(message):
                await client.send_message(message.channel, "Role `{}` now can *not* be added with %team.".format(message.content[14:]))
            else:
                await client.send_message(message.channel, "Role `{}` was already not assignable.".format(message.content[14:]))

    # Team stats in the server. Only for pokemon go servers

    elif message.content.startswith('%stats'):

        server_obj = bot.servers[message.server.id]
        if not server_obj.exists_default_roles():
            await client.send_message(message.channel, "Pokemon GO roles don't exist on the server.")

        stats_message = '''
        Team stats for {0}
        Users on Team Mystic: {1} ({4:.2f}%)
        Users on Team Valor: {2} ({5:.2f}%)
        Users on Team Instinct: {3} ({6:.2f}%)
        '''

        # TODO: Make this work with the new server team list

        role_stats = {
            "Mystic": 0,
            "Valor": 0,
            "Instinct": 0,
        }
        total = 0

        for member in message.server.members:
            for role in member.roles:
                if role.name in role_stats:
                    role_stats[role.name] += 1
                    total += 1

        msg = stats_message.format(
            message.server.name,
            role_stats["Mystic"],
            role_stats["Valor"],
            role_stats["Instinct"],
            utils.get_percentage(role_stats["Mystic"], total),  # TODO: This throws a divide by zero error
            utils.get_percentage(role_stats["Valor"], total),
            utils.get_percentage(role_stats["Instinct"], total)
        )

        await client.send_message(message.channel, msg)

    # Evaluate an input. Only for bot owner.

    elif message.content.startswith('%eval'):
        if bot.sudo(message):
            await client.send_message(message.channel, eval(message.content[6:]))

    # !!!!!!!!
    # SENDS A MESSAGE TO EVERY SERVER CONNECTED TO THE BOT. NOT AN ECHO COMMAND.
    # NOT TO BE TAKEN LIGHTLY, AND I RECOMMEND YOU DON'T USE @everyone IN THE MESSAGE UNLESS YOU WANT HATE MAIL

    elif message.content.startswith("%announce"):
        if bot.sudo(message):
            for server_id, server in bot.servers:
                default_channel = discord.utils.find(lambda c: c.is_default, server.channels)
                await client.send_message(default_channel, message.content[9:])
                sleep(0.5)  # To be nice on the api

print("Logging in...")

client.run(auth["token"])
