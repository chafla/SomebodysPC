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
        self.servers = []
        self.initializing = False
        self.client = client

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





def init(client):  # TODO: Move into Bot()
    datafiles = listdir("server_data/")
    server_objs = {}
    for file in datafiles:
        server = Server(client)
        server.init_from_file(file)
        server_objs[server.id] = server
    return server_objs


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
        self.roles = {}
        self.channel_whitelist = []
        self.pm_config = ""
        self.default_roles = []
        self.obj = discord.utils.get(client.get_all_servers(), id=self.id)

    # Init on launch, if file has been stored.

    def init_from_file(self, datafile_path):
        with open(datafile_path, "r", encoding="utf-8") as tmp:
            data = json.load(tmp)
        self.id = data["server_id"]
        self.name = data["server_name"]
        self.roles = data["custom_roles"]
        self.channel_whitelist = data["team_ch_wl"]
        self.pm_config = data["pm"]
        self.default_roles = data["default_roles"]

    # Initialization on joining server, should be placed in on_server_add

    def init_from_join(self, server):
        # Kinda roundabout, probably a nicer way to do this
        self.id = server.id
        self.name = server.name
        self.roles = {}
        self.channel_whitelist = []
        self.pm_config = "0"
        self.default_roles = "0"

        with open("server_data/{0}.json".format(self.id), "w", encoding="utf-8") as tmp:
            json.dump(init_server_datafile, tmp)

    def export_to_file(self):

        # TODO: This might result in problems if multiple people call it at once, but we need it to export.

        with open("server_data/{0}.json".format(self.id), "r", encoding="utf-8") as tmp:
            data = json.load(tmp)

        data["server_id"] = self.id
        data["name"] = self.name
        data["custom_roles"] = self.roles  # List of IDs
        data["team_ch_wl"] = self.channel_whitelist
        data["pm"] = self.pm_config
        data["default_roles"] = self.default_roles

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
            self.roles[role.id] = role.name
            self.export_to_file()
            return role

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
        self.default_roles = "1"
        self.add_custom_role(message, "Valor")
        self.add_custom_role(message, "Mystic")
        self.add_custom_role(message, "Instinct")
        return

    def check_role(self, user_input):
        # Probably a more efficient way to do this
        for role_id, role_name in self.roles.items():
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
    "server_name": "",
    "server_id": "",
    "team_ch_wl": [],  # channel ids where it's allowed
    "pm": "0",
    "custom_roles": {},  # role id: role name. useful for
    "default_roles": "0"  # 0 means default roles don't exist, 1 means that they do.
}

# Required perms for bot operation. Used for sending an oauth link.

required_perms = discord.Permissions.none()
required_perms.read_messages = True
required_perms.send_messages = True
required_perms.manage_roles = True


# Default perms for the team role.

team_perms = discord.Permissions.none()





