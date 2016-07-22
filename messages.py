# Command list, called with %help or %commands

help_message = '''
**%team [team name]**: Assign yourself to a team. Typed like `%team Mystic` to set your role as Team Mystic.\n
**%whitelist**\*: Set a specific channel for team setting.\n
**%unwhitelist**\*: Re-allow team setting in a channel.\n
**%server_info**: Output a small list of information about the server.\n
**%help or %commands**: Show this message again.\n
**%pm [required/optional]**\*: Optional is default, and required disables setting roles in the server.\n
**%invite**: Generate a link that you can use to add goPC to your own server.\n
**%create_roles**\*: Create three empty team roles that goPC can use to assign.\n
**%stats**: List stats on the number of team members, including the percentage of the members on each team. Note that this only works for Pokemon GO teams that use the default format.\n
**%wiki [page]**: Find a page on bulbapedia.\n
**%enable_role [role name]**\*: Allow a role to be added by goPC.
**%disable_role [role name]**\*: Disallow a role from being added by goPC, if it already can be.
**%role_config [exclusive/multiple]**\*: Setting to exclusive (default) only allows one role to be set per user. Setting to multiple allows users to set as many roles as they want.
**Commands with an asterisk (\*) can only be run by the server owner or a user with the `Manage Server` permission.**
'''

# Owner message, sent to the owner when connecting to a server

owner_message = '''
Hi, thanks for adding me to your server!
In case you weren't aware, I'm a role managing bot. Assuming proper role setup, posting __%team__ followed by a designated role name will add the role to a user automatically. By default, I work with the role names `Valor`, `Mystic`, and `Instinct`, but of course only if the roles actually exist.

This should work in a channel within the server, as well as in PMs. If you want to specify a channel that people can set roles in, type __%whitelist__ in said channel.

Otherwise, users can just PM me with %team, and it will work even if we share multiple servers. If you want users to only be able to assign roles via PMs, post __%pm required__.

If you would just like me to create roles, someone with the Manage Server permission (or you, the owner) can type **%create_roles** in the server, and I will create empty template roles for Pokemon GO teams.

Regardless, in order for me to work, the role names should be `Valor`, `Mystic`, and `Instinct` (case sensitive), and users should call %team with those exact parameters.

**The team roles *need* to be located below goPC's role in order for them to be able to be assigned, or else it will say it does not have permissions.**

My code base is available at https://github.com/chafla/SomebodysPC.
If you have any questions, problems, compliments, etc., you can find `Luc | ルカリオ#5653` (my writer) in the /r/PokemonGO server.
'''

