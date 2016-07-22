import json
import discord
import sys
from os import listdir, remove

# TODO: Run this at start of program, after on ready but make sure there's a flag that doesn't let commands be handled while it's still initializing, possibly in Bot


class Bot:

    def __init__(self, client):
        try:
            with open('config.json', 'r+') as json_config_info:
                config = json.load(json_config_info)
        except IOError:
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
                server.init_from_file("server_data/" + file)  # Probably a neater way of doing this
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
        datafiles = listdir("server_data/")
        for file in datafiles:
            server = Server(client)

            # Pull the file ID from the name, so that we can be sure

            server.update_data_files(client, "server_data/" + file, file)  # Probably a neater way of doing this


class Server:
    """
    Allowing servers to have different roles, and to be able to use different role names.
    Should be called by way of a message, so that we can get all the useful data.

    Planned to be used in a future implementation, but currently non-functional.

    """

    base_roles = ["Instinct", "Valor", "Mystic"]

    def __init__(self, client):
        self.id = ""
        self.name = ""
        self.roles = []
        self.channel_whitelist = []
        self.pm_config = ""
        self.exclusive = ""
        self.obj = discord.utils.get(client.servers, id=self.id)

    # Init on launch, if file has been stored.

    def init_from_file(self, datafile_path):

        # TODO: RE-INITIALIZE ALL EXISTING SERVER OBJECTS WITH THE NEW KEYS

        # TODO: Consider recreating files if they disappear - should really be only needed on manual delete when testing
        # Note: if we do it when the server object is initialized, then we run a risk of it not existing then.

        with open(datafile_path, "r", encoding="utf-8") as tmp:
            data = json.load(tmp)
        self.channel_whitelist = data["team_ch_wl"]
        self.pm_config = data["pm"]
        self.id = data["server_id"]
        self.name = data["server_name"]  # Server name was blank in old code, let's fix that
        self.roles = data["custom_roles"]
        self.exclusive = data["exclusive"]

    def update_data_files(self, client, datafile_path, server_id):
        # Utility to update all existing datafiles in case I add new stuff to dicts.
        # Mostly hardcoded, and requires that the client connect in the first place.
        with open(datafile_path, "r", encoding="utf-8") as tmp:
            data = json.load(tmp)
        try:
            # Add the new keys here
            test_var = data["custom_roles"], data["server_id"], data["exclusive"]
        except KeyError:
            with open(datafile_path, "r", encoding="utf-8") as tmp:
                data = json.load(tmp)
            server = discord.utils.get(client.servers, id=server_id[:-5])

            if server is None:
                # This means that we don't belong to the server for some reason. Throws AttributeErrors.
                # Just reformat the file so that we don't get errors.
                self.name = ""
                self.id = server_id[:-5]
                self.roles = []
                self.exclusive = "0"
                self.export_to_file()
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
                for role in server.roles:
                    if role.name in ["Valor", "Mystic", "Instinct"]:  # TODO: Consider the fact that this might have some impact on non-pokemon go servers. Possibly add check for roles that do actually exist on the server.
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

    async def check_whitelist(self, message):
        """
        Check against the channel whitelist to see if the command should be allowed in this channel.
        :param message: message object from context
        :return: None if the command goes through, otherwise a message detailing why it didn't.
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
        # TODO: Consider removing this first check because the default role list already doesn't contain the pogo roles.
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

    # TODO: Command to create a server when it already exists
    # TODO: Determine what I meant when I wrote the above TODO

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
    "pm": "0",
    # Here's where I run into a bit of a fix. Setting custom_roles to just a role name means that if the role is
    # re-named, it needs to be re-added. However, just using names means that it's made substantially easier to keep
    # track of roles. There seems to be a bit of a trade-off in utility here, but I'm going to make it a list for now.
    # This does mean possibly having to remake every single json file if I change my mind, though.
    "custom_roles": [],  # Just role name.
    "exclusive": "0"  # Whether or not the user can have more than one role. 0 is no, 1 is yes.
}

# Required perms for bot operation. Used for sending an oauth link.

required_perms = discord.Permissions.none()
required_perms.read_messages = True
required_perms.send_messages = True
required_perms.manage_roles = True


# Default perms for the team role.

team_perms = discord.Permissions.none()





