import json
import discord
import sys
import logging
from os import listdir, remove

log = logging.getLogger("bot")

# TODO: Standardize how I do function documentation since it's all over the place

# TODO: Add the new option to the server config


class Bot:

    def __init__(self, client):
        try:
            with open('config.json', 'r+') as json_config_info:
                config = json.load(json_config_info)
        except IOError:
            log.warning("config.json was not found, exiting.")
            sys.exit("config.json not found in running directory.")

        self.owner_id = config["owner_id"]
        self.info_message = config["info_message"]
        self.servers = {}  # List of server objects
        self.initializing = False
        self.client = client
        self.debug = True  # Just used for testing.

    def sudo(self, message):
        # Allows for owner-only commands.
        if message.author.id == self.owner_id:
            return True
        else:
            return False

    def get_server(self, server=None, svr_id=None):
        # Get server from server list.
        if server is not None:
            return self.servers[server.id]
        elif svr_id is not None:
            return self.servers[svr_id]

    def init(self, client):
        datafiles = listdir("server_data/")
        for file in datafiles:
            server = Server(client)

            # Pull the file ID from the name, so that we can be sure
            try:
                server.init_from_file("server_data/" + file, client)  # Probably a neater way of doing this
            except KeyError:  # If there's a discrepancy, update the file otg
                server.update_data_files(client, "server_data/" + file, file)

            self.servers[server.id] = server

    def add_new_server(self, client, server):
        # Create a new server datafile and object on the fly
        server_obj = Server(client)
        server_obj.init_from_join(server)
        self.servers[server.id] = server_obj
        return

    def remove_server(self, server):
        # Remove the server datafile and object when leaving a server.
        print("Removing datafile for {0.name}".format(server))
        remove("server_data/{0.id}.json".format(server))
        self.servers.pop(server.id)

    @staticmethod
    def update_datafiles(client):
        # Loop through all server objects and update their datafiles to reflect new changes.
        datafiles = listdir("server_data/")
        for file in datafiles:
            server = Server(client)
            # Pull the file ID from the name, so that we can be sure
            server.update_data_files(client, "server_data/" + file, file)  # Probably a neater way of doing this

    async def get_server_from_pm(self, message):
        # TODO: Work this out
        """
        Handle the logic for determining how many servers are shared between the bot and the message author.
        Implemented to be used in PMs so we can get the right server object to be able to assign roles through PMs.
        :param message:
        :return: Server object
        """

        # Get the servers shared between the author and the bot

        servers_shared = []
        for server in self.client.servers:
            for member in server.members:
                if member.id == message.author.id:
                    servers_shared.append(member.server)

        if len(servers_shared) == 0:  # This shouldn't normally appear
            await self.client.send_message(message.channel, "Something is wrong. We don't appear to share any servers.")
            return None

        elif len(servers_shared) == 1:  # This makes it really easy, since there's only one server, just use that one
            return servers_shared[0]

        else:  # Things get complicated. From here, it's mostly just message management.
            base_message = "Oops, looks like I share more than one server with you. Which server would you like to set your role in? Reply with the digit of the server.\n"
            i = 1

            for svr in servers_shared:
                base_message += "{0}: {1.name}\n".format(i, svr)
                i += 1

            await self.client.send_message(message.channel, base_message)

            # Wait for the message that the user sends back.
            server_selection = await get_message(self.client, message, i, base_message)

            # For some reason, the filter on wait_for_message isn't consistent, so we have to have more checks outside
            if server_selection > i:
                await self.client.send_message(message.channel, "That number was too large, try %team again.")
                return None
            else:
                try:
                    server = servers_shared[(int(server_selection) - 1)]
                except IndexError:
                    await self.client.send_message(message.channel, "That number was too large, try %team again.")
                    return None
                    # TODO: Fix possibility of IndexError

            return server


class Server:
    """
    Allowing servers to have different roles, and to be able to use different role names.
    """

    base_roles = ["Instinct", "Valor", "Mystic"]

    def __init__(self, client):
        self.id = ""
        self.name = ""
        self.roles = []
        self.channel_whitelist = []
        self.pm_config = ""
        self.exclusive = ""
        self.user_ctrl = "0"
        self.obj = discord.utils.get(client.servers, id=self.id)  # This actually seems to end up as None

    # Init on launch, if file has been stored.

    def init_from_file(self, datafile_path, client):

        # Note: if we do it when the server object is initialized, then we run a risk of it not existing then.

        with open(datafile_path, "r", encoding="utf-8") as tmp:
            data = json.load(tmp)
        self.channel_whitelist = data["team_ch_wl"]
        self.pm_config = data["pm"]
        self.id = data["server_id"]
        self.name = data["server_name"]  # Server name was blank in old code, let's fix that
        self.roles = data["custom_roles"]
        self.exclusive = data["exclusive"]
        self.user_ctrl = data["user_ctrl"]
        self.obj = discord.utils.get(client.servers, id=self.id)  # Needs to be called here and not __init__() for some reason

    def update_data_files(self, client, datafile_path, datafile_filename):
        # Utility to update all existing datafiles in case I add new stuff to dicts.
        # Mostly hardcoded, and requires that the client connect in the first place.
        # To use, add the new keys to test_var.
        server_id = datafile_filename[:-5]
        with open(datafile_path, "r", encoding="utf-8") as tmp:
            data = json.load(tmp)
        try:
            # Add the new keys here
            test_var = data["custom_roles"], data["server_id"], data["exclusive"], data["user_ctrl"]
        except KeyError:
            with open(datafile_path, "r", encoding="utf-8") as tmp:
                data = json.load(tmp)
            server = discord.utils.get(client.servers, id=server_id)

            if server is None:
                # This means that we don't belong to the server for some reason. Throws AttributeErrors.
                # Just reformat the file so that we don't get errors.
                self.name = ""
                self.id = server_id
                self.roles = []
                self.exclusive = "0"
                self.user_ctrl = "0"
                self.export_to_file()
                log.info("Datafile {0}.json blanked due to not belonging to the server anymore.".format(server_id))
                return
            else:
                self.name = server.name
                self.id = server.id  # omit .json
                # These we can assume already exist in the datafiles, so let's not try to re-create them.
                self.pm_config = data["pm"]
                self.channel_whitelist = data["team_ch_wl"]
                # This one already exists, but is empty. We really don't need to worry ourselves with it too much.

                # These ones don't exist in the new json files, so we need to add them.
                # We have to check to see if the server contains the default roles already, and if not, add them.
                self.exclusive = "0"
                self.user_ctrl = "0"
                for role in server.roles:
                    if role.name in ["Valor", "Mystic", "Instinct"]:
                        self.roles.append(role.name)

                print("Updated server datafiles for {0.name}".format(server))

                self.export_to_file()

    def init_from_join(self, server):
        # Creation of object on joining server through oauth.
        # Note that the first time through, it creates an empty object that should be popularized on next boot.
        # Kinda roundabout, probably a nicer way to do this
        self.id = server.id
        self.name = server.name
        self.roles = []
        self.channel_whitelist = []
        self.pm_config = "0"
        self.exclusive = "0"
        self.obj = server
        self.user_ctrl = "0"
        output = init_server_datafile
        output["server_id"] = server.id
        output["server_name"] = server.name
        with open("server_data/{0}.json".format(self.id), "w", encoding="utf-8") as tmp:
            json.dump(output, tmp)

    def export_to_file(self):
        # Take the current server object as it is and push it to a .json file.

        with open("server_data/{0}.json".format(self.id), "r", encoding="utf-8") as tmp:
            data = json.load(tmp)

        data["server_id"] = self.id
        data["name"] = self.name
        data["custom_roles"] = self.roles  # List of names
        data["team_ch_wl"] = self.channel_whitelist
        data["pm"] = self.pm_config
        data["exclusive"] = self.exclusive
        data["user_ctrl"] = self.user_ctrl

        with open("server_data/{0}.json".format(self.id), "w", encoding="utf-8") as tmp:
            json.dump(data, tmp)

    def add_custom_role(self, message, external_role=None):
        # TODO: Occasionally omits the role from the role list. Probably from failing to write to the file for some reason.
        # initialize a custom role that can be added through %team. Server dependent.
        # If external_role is not None, then it's being called by something that's not the command, and we're just passing in the names we know.
        if external_role is not None:
            role_name = external_role
        else:
            role_name = message.content[13:]
        role = discord.utils.get(message.server.roles, name=role_name)
        if role is None:
            return None
        else:
            self.roles.append(role.name)
            self.export_to_file()
            return role

    def remove_custom_role(self, message, external_role=None):
        # Remove a role from the server object's role list.
        # Returns True if it succeeds, or False if not.
        if external_role is not None:
            role_name = external_role
        else:
            role_name = message.content[14:]
        try:
            self.roles.remove(role_name)
            self.export_to_file()
            return True
        except IndexError:
            return False

    def add_to_whitelist(self, message):
        """Add a channel to the server whitelist and write it out."""
        self.channel_whitelist.append(message.channel.id)
        self.export_to_file()

    def remove_from_whitelist(self, message):
        """Remove the channel from the whitelist and write it out."""
        self.channel_whitelist.remove(message.channel.id)
        self.export_to_file()

    async def check_whitelist(self, message):
        """
        Check against the channel whitelist to see if the command should be allowed in this channel.
        :param message: message object from context
        :return: None if the command goes through, otherwise a message detailing why it didn't, and where to direct the messages.
        """
        if self.channel_whitelist is None or message.channel.id in self.channel_whitelist:
            # Command does go through
            return None
        elif message.channel.id not in self.channel_whitelist:
            # Command doesn't go through, return a message on where that should be allowed.
            if len(self.channel_whitelist) == 1:
                return "Please put team requests in <#{0}>.".format(self.channel_whitelist[0])
            elif len(self.channel_whitelist) > 1:  # Grammar for grammar's sake, any more are ignored.
                return "Please put team requests in <#{0}> or <#{1}>.".format(self.channel_whitelist[0], self.channel_whitelist[1])

        # TODO: Set this up to basically handle most of the code in the %rank command

    def init_default_roles(self, message):
        # To be called when someone calls %create_roles, after the roles have been created successfully.
        self.add_custom_role(message, "Valor")
        self.add_custom_role(message, "Mystic")
        self.add_custom_role(message, "Instinct")
        return

    def check_default_roles(self):
        # Check to see if the only roles that exist are the default roles.
        for role in self.roles:
            if role in ["Mystic", "Valor", "Instinct"]:
                continue
            else:
                return False
        else:
            return True

    def exists_default_roles(self):
        # Check to see if default roles exist or not.
        for role in self.obj.roles:
            if role.name in self.base_roles:  # Just assume that if one role exists, then they all do.
                return True
        else:
            return False

    def check_role(self, user_input):
        """
        A simple check to see if the user's message was in the role list.
        :param user_input: Message content.
        :return: True if role is in the team list, otherwise False.
        """
        for role_name in self.roles:
            if role_name == user_input:
                return True
        return False

    def list_roles(self):
        # Compile roles into a fancy, readable format.

        role_list = self.roles

        base_message = "roles that can be added with %team are "
        if len(role_list) == 1:  # If there's only one role addable, make it mostly clean.
            base_message += "`{}`."
        else:
            for role_name in role_list[:-1]:
                base_message += "`{}`, ".format(role_name)
            else:  # For the last object
                base_message += "and `{}`.".format(role_list[-1])
        return base_message

    def generate_config_msg(self):
        # Create a message used for %server_config.
        if self.roles != []:  # pycharm doesn't like this, but self.roles is not None doesn't work right
            addable_roles = pp_list(self.roles)
        else:
            addable_roles = "None"

        chan_name_list = []
        if self.channel_whitelist != []:
            for chan in self.channel_whitelist:
                chan_obj = discord.utils.get(self.obj.channels, id=chan)
                if chan_obj is not None:
                    chan_name_list.append(chan_obj.name)
                else:
                    continue
            else:
                whitelist = pp_list(chan_name_list)
        else:  # Should trigger if there are no channels in the whitelist.
            whitelist = "None"

        pm = "optional" if self.pm_config == "0" else "required"  # Python is so nice
        role_cfg = "exclusive" if self.exclusive == "0" else "multiple"
        user_ctrl = "disabled" if self.user_ctrl == "0" else "enabled"

        return server_config_message.format(addable_roles, whitelist, pm, role_cfg, user_ctrl)

# Function used to check the message received for an int.

async def get_message(client, message, i, base_message):
    msg = await client.wait_for_message(author=message.author, channel=message.channel)
    try:
        if 0 < int(msg.content) <= i:
            return int(msg.content)
        else:
            await client.send_message(message.channel, base_message)
            await get_message(client, message, i, base_message)
    except ValueError:  # In case what they return isn't convertible to an int
        await client.send_message(message.channel, base_message)
        await get_message(client, message, i, base_message)


def check_perms(message):

    # Only allows execution of command if author has Manage Server permission, or is owner.

    if message.server.owner.id == message.author.id:
        return True
    else:
        for role in message.author.roles:
            if role.permissions.manage_server:  # May throw errors.
                return True
        else:
            return False


def pp_list(ls):
    # Take a list of strings and format it nicely
    output = ""
    for item in ls[:-1]:
        output += "{}, ".format(item)
    else:
        output += ls[-1]
    return output


def get_percentage(amount, total):
    if amount > 0:
        percentage = (amount / total) * 100
        return percentage
    else:
        return amount  # Avoiding div by zero

init_server_datafile = {
    "server_name": "",  # Server name, ofc subject to change.
    "server_id": "",  # Server ID
    "team_ch_wl": [],  # channel ids where %team is allowed.
    "pm": "0",  # Whether or not users can set roles in messages or not.
    # Here's where I run into a bit of a fix. Setting custom_roles to just a role name means that if the role is
    # re-named, it needs to be re-added. However, just using names means that it's made substantially easier to keep
    # track of roles. There seems to be a bit of a trade-off in utility here, but I'm going to make it a list for now.
    # This does mean possibly having to remake every single json file if I change my mind, though.
    "custom_roles": [],  # Just role name.
    "exclusive": "0",  # Whether or not the user can have more than one role. 0 is no, 1 is yes.
    "user_ctrl": "0"  # Whether or not users can remove their roles that goPC can assign
}

# Required perms for bot operation. Used for sending an oauth link.

server_config_message = '''
Current server settings:
```
Addable roles: {0}

Channels whitelisted: {1}

PM settings: {2}

Role settings:
Role exclusivity: {3}
User control (whether or not %leaveteam is usable): {4}
```'''

# Flags used for config commands

flags = {
    "pm":  {
        "optional": "0",
        "required": "1",
    },
    "role": {
        "exclusive": "0",
        "multiple": "1"
    },
    "ctrl": {
        "disabled": "0",
        "enabled": "1"
    }

}

required_perms = discord.Permissions.none()
required_perms.read_messages = True
required_perms.send_messages = True
required_perms.manage_roles = True


# Default perms for the team role.

team_perms = discord.Permissions.none()





