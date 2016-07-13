import json
# import discord



try:
    with open('config.json', 'r+') as json_config_info:
        config = json.load(json_config_info)
except IOError:
    print("config.json not found in running directory.")
    config = None
    exit(0)

sudo_list = config["owner"]



class ServerPrefs:
    """
    Allowing servers to have different roles, and to be able to use different role names.
    Should be called by way of a message, so that we can get all the useful data.

    Planned to be used in a future implementation, but currently non-functional.

    """

    # TODO: Implement this so that this can be used for multiple servers
    def __init__(self, message, role_list, role_message, commanders, default_roles=True):
        self.roles = {}  # List of server roles, associated with their callable names.
        self.role_names = []
        self.message = role_message  # Message to send when a role is added.
        self.server_whitelist = []
        self.commanders = []  # People who can adjust server specific settings
        self.server_id = message.server.id
        self.server_name = message.server.name

        if default_roles:
            # Allow for people to use the bot for other role-adding purposes.
            self.teams = ["Instinct", "Valor", "Mystic"]
        else:
            self.teams = []

    def check_perms(self, message):
        if message.author.id in self.commanders:
            return True
        else:
            return False

    #def add_bot_commander(self, message, client):










# TODO: Make a command to run on first launch that loads things from a db or json files or something
class Bot:
    pass



def sudo(message):
    # Allows for owner-only commands.
    if message.author.id in sudo_list:
        return True
    else:
        return False

