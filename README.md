# goPC
Multi-server role-assigning bot, similar to Bill's PC from the /r/PokemonGO discord, and written by `Luc | ルカリオ#5653`.
The purpose of this bot is to make assigning team-based roles for Pokemon GO servers a breeze, and to provide to other, smaller servers the same sort of functionality that Bill's PC provides with its `%team` command.
Designed out of demand for a similar sort of solution in smaller servers, where users want a no-fuss solution that adds roles based on Pokemon GO teams. Designed to be light, and shouldn't really interfere with anything. Doesn't log anything, either.

**You can easily add this bot to your server by clicking [this link](https://discordapp.com/oauth2/authorize?client_id=202615577041305600&scope=bot&permissions=268438528).**

Requires at least Python 3.5.1 be installed, as well as the latest version of discord.py.

__Note that this is **not** designed to be an extremely multi-functional bot like BooBot.__ It's designed for a niche, and should work alongside existing bots.
If you want to use this bot's code and launch your own instance, *please please please* don't name it goPC, so as to avoid confusion.

# Current features:

* Ability to add roles based on a simple command, `%team [team name]`, where team name is Instinct, Valor or Mystic.
Users would, for example, type:
`%team Valor`
to join Team Valor. The server is required to have roles that correspond to the team name, and are formatted as shown above.

* Ability to whitelist certain channels for assigning %team.

* Team requests can be sent through PMs, and have a selection menu if you share more than one server.

* Ability to create a set of empty template roles (no permissions) that can then be configured manually, by using %create_roles with the `Manage Server` permission.

# Current commands
__%team [team name]__: Assign yourself to a team. Typed like `%team Mystic` to set your role as Team Mystic.

__%whitelist\*__: Set a specific channel for team setting.

__%unwhitelist__\*: Re-allow team setting in a channel.

__%server_info__: Output a small list of information about the server.

__%help or %commands__: Show this message again.

__%pm [required/optional]__\*: Optional is default, and required disables setting roles in the server.

__%invite__: Generate a link that you can use to add goPC to your own server.

__%create_roles__\*: Create three empty team roles that goPC can use to assign.

__%stats__: List stats on the number of team members, including the percentage of the members on each team.

**Commands with an asterisk can only be run by the server owner or a user with the `Manage Server` permission.**

You can find this list by using %help or %oommands in chat.




# Roles Required:

* Manage Roles: Required in order to add roles to members, as well as create the template roles.

* Read Messages: Required in order to respond to commands.

* Send Messages: Not technically *required*, but rather very highly recommended, as you won't get any feedback on whether commands went through or not.


# Planned additions

At the moment, I'm going to go for an early release with the sole functionality of adding team commands, but there are some features I'd like to implement in the future.

* Aliases for team names.

* Ability to use different role lists than just the Pokemon Go team list, so as to make the bot useful in other applications.

* Perhaps adding some other commands that are a bit more fun. __This isn't really the intention of the bot, though, and I probably won't be adding many fun commands.__ So don't pester me about it, please. :P