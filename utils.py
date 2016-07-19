import json
import discord
import sys
from os import listdir

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

            server.init_from_file("server_data/" + file)  # Probably a neater way of doing this
            self.servers[server.id] = server

    def update_datafiles(self, client):
        datafiles = listdir("server_data/")
        for file in datafiles:
            server = Server(client)

            # Pull the file ID from the name, so that we can be sure

            server.update_data_files(client, "server_data/" + file, file)  # Probably a neater way of doing this
            print("Updated data files.")


class Server:
    """
    Allowing servers to have different roles, and to be able to use different role names.
    Should be called by way of a message, so that we can get all the useful data.

    Planned to be used in a future implementation, but currently non-functional.

    """

    # TODO: Implement this so that this can be used for multiple servers
    # TODO: Consider removing self.teams, or even self.default_roles

    base_roles = ["Instinct", "Valor", "Mystic"]

    def __init__(self, client):
        self.id = ""
        self.name = ""
        self.roles = []
        self.channel_whitelist = []
        self.pm_config = ""
        self.obj = discord.utils.get(client.servers, id=self.id)

    # Init on launch, if file has been stored.

    def init_from_file(self, datafile_path):

        # TODO: RE-INITIALIZE ALL EXISTING SERVER OBJECTS WITH THE NEW KEYS
        # Note: if we do it when the server object is initialized, then we run a risk of it not existing then.

        with open(datafile_path, "r", encoding="utf-8") as tmp:
            data = json.load(tmp)
        self.channel_whitelist = data["team_ch_wl"]
        self.pm_config = data["pm"]
        self.id = data["server_id"]
        self.name = data["server_name"]  # Server name was blank in old code, let's fix that
        self.roles = data["custom_roles"]

    def update_data_files(self, client, datafile_path, server_id):
        # Utility to update all existing datafiles in case I add new stuff to dicts.
        # Mostly hardcoded, and requires that the client connect in the first place.
        with open(datafile_path, "r", encoding="utf-8") as tmp:
            data = json.load(tmp)
        try:
            test_var = data["custom_roles"], data["server_id"]
        except KeyError:
            with open(datafile_path, "r", encoding="utf-8") as tmp:
                data = json.load(tmp)
            server = discord.utils.get(client.servers, id=server_id[:-5])

            if server is None:  # This means that we don't belong to the server for some reason. Throws AttributeErrors.
                self.name = "LEFT"
                belongs = False
                return
            else:
                self.name = server.name
                self.id = server.id  # omit .json
                # These we can assume already exist in the datafiles, so let's not try to re-create them.
                self.pm_config = data["pm"]
                self.channel_whitelist = data["team_ch_wl"]
                # This one already exists, but is empty. We really don't need to worry ourselves with it too much.

                # These ones don't exist in the new json files, so we need to add them.
                # We have to check to see if the server contains the default roles already, and if so, add them.
                for role in server.roles:
                    if role.name in ["Valor", "Mystic", "Instinct"]:
                        self.roles.append(role.name)

                print("Updated server datafiles for {}".format(server.name))

                self.export_to_file()

    def init_from_join(self, server):
        # Creation of object on joining server through oauth.
        # Kinda roundabout, probably a nicer way to do this
        self.id = server.id
        self.name = server.name
        self.roles = []
        self.channel_whitelist = []
        self.pm_config = "0"
        with open("server_data/{0}.json".format(self.id), "w", encoding="utf-8") as tmp:
            json.dump(init_server_datafile, tmp)

    def export_to_file(self):
        # Take the current server object as it is and

        # TODO: This might result in problems if multiple people call it at once, but we need it to export.

        with open("server_data/{0}.json".format(self.id), "r", encoding="utf-8") as tmp:
            data = json.load(tmp)

        data["server_id"] = self.id
        data["name"] = self.name
        data["custom_roles"] = self.roles  # List of IDs
        data["team_ch_wl"] = self.channel_whitelist
        data["pm"] = self.pm_config

        with open("server_data/{0}.json".format(self.id), "w", encoding="utf-8") as tmp:
            json.dump(data, tmp)

    def add_custom_role(self, message, external_role=None):
        # initialize a custom role that can be added through %team. Server dependent.
        # If external_role is not None, then it's being called by something else, and we're just passing in the names we know.
        if external_role is not None:
            role_name = external_role
        else:
            role_name = message.content[21:]
        role = discord.utils.get(message.server.roles, name=role_name)
        if role is None:
            return None
        else:
            self.roles.append(role.name)
            self.export_to_file()
            return role

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

    def get_role_from_server(self, role_name, message, client):
        # TODO: FINISH THIS
        """

        :param role_name: String that contains a name of a role. Should be passed in by message.content[6:]
        :param message: Message object.
        :param client: Client object
        :return:
        """

        # TODO: Set this up to grab the role object based on context
        # Get role from server context
        if message.channel.is_private:
            member = message.author
            server = message.server
            return member, server
        else:
            pass

    def init_default_roles(self, message):
        # To be called when someone calls %create_roles, after the roles have been created successfully.
        self.add_custom_role(message, "Valor")
        self.add_custom_role(message, "Mystic")
        self.add_custom_role(message, "Instinct")
        return

    def check_role(self, user_input):
        # Probably a more efficient way to do this
        for role_name in self.roles:
            if role_name == user_input:
                return True
        return False

    # TODO: Command to create a server when it already exists

async def get_message(client, message, i, base_message):
    msg = await client.wait_for_message(author=message.author, channel=message.channel)
    try:
        if 0 < int(msg.content) <= i:
            print(i)
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
        return False

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
}

# Required perms for bot operation. Used for sending an oauth link.

required_perms = discord.Permissions.none()
required_perms.read_messages = True
required_perms.send_messages = True
required_perms.manage_roles = True


# Default perms for the team role.

team_perms = discord.Permissions.none()





