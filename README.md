# goPC
Multi-server role-assigning bot, similar to Bill's PC from the /r/PokemonGO discord, and written by `Luc | ルカリオ#5653`.
The original purpose of this bot is to make assigning team-based roles for Pokemon GO servers a breeze, and to provide to other, smaller servers the same sort of functionality that Bill's PC provides with its `%team` command. Its use cases aren't just limited to Pokemon GO servers, though, as goPC can be easily set up to assign other roles as well.
Designed out of demand for a similar sort of solution in smaller servers, where users want a no-fuss solution that adds roles based on Pokemon GO teams. Designed to be light, and shouldn't really interfere with anything. Doesn't log anything, either.

**You can easily add this bot to your server by clicking [this link](https://discordapp.com/oauth2/authorize?client_id=202615577041305600&scope=bot&permissions=268438528).**

__Note that this is **not** designed to be an extremely multi-functional bot like BooBot.__ It's designed for a niche, and should work alongside existing bots.
If you want to use this bot's code and launch your own instance, *please please please* don't name it goPC, so as to avoid confusion.

# Current features:

* Ability to add roles based on a simple command, `%team [team name]`, where team name is the name of the role you would like to assign.
Users would, for example, type:
`%team Valor`
to join Team Valor if it's enabled on the server. By default, the bot supports Pokemon GO team roles, if their names are formatted like `Valor`, `Instinct`, and `Mystic` (case sensitive).

* Ability to whitelist certain channels for assigning %team.

* Team requests can be sent through PMs, and have a selection menu if you share more than one server.

* Ability to create a set of empty template roles (no permissions) that can then be configured manually, by using `%create_roles` with the `Manage Server` permission.

* Ability to assign roles that aren't Pokemon GO roles, by adding them with `%enable_role` and then using `%team`.

* Ability to let users assign either one role or multiple roles to themselves.

# Current commands

__%team [team name]__: Assign yourself to a team. Typed like `%team Mystic` to set your role as Team Mystic.

__%whitelist__\*: Set a specific channel for team setting.

__%unwhitelist__\*: Re-allow team setting in a channel.

__%server_info__: Output a small list of information about the server.

__%help or %commands__: Show this message again.

__%pm [required/optional]__\*: Optional is default, and required disables setting roles in the server.

__%invite__: Generate a link that you can use to add goPC to your own server.

__%create_roles__\*: Create three empty team roles that goPC can use to assign.

__%stats__: List stats on the number of team members, including the percentage of the members on each team. Only works with the default Pokemon GO roles.

__%wiki [page]__: Find a page on bulbapedia.

__%enable_role [role name]__\*: Allow a role to be added by goPC.

__%disable_role [role name]__\*: Disallow a role from being added by goPC, if it already can be.

__%role_config [exclusive/multiple]__\*: Setting to exclusive (default) only allows one role to be set per user. Setting to multiple allows users to set as many roles as they want.

__%server_config__: Output the current server settings (whitelisted channels, role config setting, addable roles, and PM role-assignment settings).

**Commands with an asterisk can only be run by the server owner or a user with the `Manage Server` permission.**

You can find this list by using %help or %oommands in chat.

# Roles Required:

* Manage Roles: Required in order to add roles to members, as well as create the template roles.

* Read Messages: Required in order to respond to commands.

* Send Messages: Not technically *required*, but rather very highly recommended, as you won't get any feedback on whether commands went through or not.


# Planned additions

At the moment, I'm going to go for an early release with the sole functionality of adding team commands, but there are some features I'd like to implement in the future.

* Aliases for team names.

* Perhaps adding some other commands that are a bit more fun. __This isn't really the intention of the bot, though, and I probably won't be adding many fun commands.__ So don't pester me about it, please. :P

# Running an instance

If you're going to be running your own instance of goPC, take the `config_default.json` and `auth_default.json` files, and rename them to `auth.json` and `config.json`, and fill them in with the corresponding data.

goPC uses the `await` syntax, and as such python 3.5 or greater is required.

Also, the following packages need to be installed:

* discord.py

* mwclient