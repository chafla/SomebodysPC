# lol fuck good practices

# Command list, called with %help or %commands

help_message = '''
__%team [team name]__: Assign yourself to a team. Typed like `%team Mystic` to set your role as Team Mystic.\n
__%whitelist\*__: Set a specific channel for team setting.\n
__%unwhitelist__\*: Re-allow team setting in a channel.\n
__%server_info__: Output a small list of information about the server.\n
__%help or %commands__: Show this message again.\n
__%pm [required/optional]__\*: Optional is default, and required disables setting roles in the server.\n
__%invite__: Generate a link that you can use to add goPC to your own server.\n
__%create_roles__\*: Create three empty team roles that goPC can use to assign.\n
__%stats__: List stats on the number of team members, including the percentage of the members on each team.\n
__%wiki [page]__: Find a page on bulbapedia.\n
**Commands with an asterisk can only be run by the server owner or a user with the `Manage Server` permission.**
'''

# Owner message, sent to the owner when connecting to a server

owner_message = '''
Hi, thanks for adding me to your server!
In case you weren't aware, I'm a role managing bot. Assuming proper role setup, posting __%team__ followed by `Instinct`, `Valor`, or `Mystic` will add a role to a user automatically.

This should work in a channel within the server, as well as in PMs. If you want to specify a channel that people can set roles in, type __%whitelist__ in said channel.

Otherwise, users can just PM me with %team, and it will work even if we share multiple servers. If you want users to only be able to assign roles via PMs, post __%pm required__.

If you would like me to create roles, someone with the Manage Server permission (or you, the owner) can type __%create_roles__ in the server, and I will create empty template roles for the server that work with me.

Regardless, in order for me to work, the role names should be `Valor`, `Mystic`, and `Instinct` (case sensitive), and users should call %team with those exact parameters.

**The team roles *need* to be located below goPC's role in order for them to be able to be assigned, or else it will say it does not have permissions.**

My code base is available at https://github.com/chafla/SomebodysPC.
If you have any questions, problems, compliments, etc., you can find `Luc | ルカリオ#5653` (my writer) in the /r/PokemonGO server.
'''

