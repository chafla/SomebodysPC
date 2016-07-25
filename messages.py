# Command list, called with %help or %commands

help_message = '''
**%team [team name]**: Assign yourself to a team. Typed like `%team Mystic` to set your role as Team Mystic.
**%whitelist**\*: Set a specific channel for team setting.
**%unwhitelist**\*: Re-allow team setting in a channel.
**%server_info**: Output a small list of information about the server.
**%help or %commands**: Show this message again.
**%pm [required/optional]**\*: Optional is default, and required disables setting roles in the server.
**%invite**: Generate a link that you can use to add goPC to your own server.
**%create_roles**\*: Create three empty Pokemon GO team roles that goPC can use to assign.
**%stats**: List stats on the number of team members, including the percentage of the members on each team. Note that this only works for Pokemon GO teams that use the default format.
**%wiki [page]**: Find a page on bulbapedia.
**%enable_role [role name]**\*: Allow a role to be added by goPC.
**%disable_role [role name]**\*: Disallow a role from being added by goPC, if it already can be.
**%role_config [exclusive/multiple]**\*: Setting to exclusive (default) only allows one role to be set per user. Setting to multiple allows users to set as many roles as they want.
**%server_config**: Output the current server settings (whitelisted channels, role config, addable roles, and PM settings).\n
**Commands with an asterisk (\*) can only be run by the server owner or a user with the `Manage Server` permission.**
'''

# Owner message, sent to the owner when connecting to a server

owner_message = '''
Hi, thanks for adding me to your server!
In case you weren't aware, I'm a role managing bot. Assuming proper role setup, posting __%team__ followed by a designated role name will add the role to a user automatically. By default, I work with the role names `Valor`, `Mystic`, and `Instinct`, but of course only if the roles actually exist on the server. You (or someone with the Manage Server permission) can type **%enable_role [role name]** to enable adding that role with %team.

Adding roles works within server channels, as well as in PMs. If you want to specify a channel that people can set roles in, type __%whitelist__ in said channel.

Otherwise, users can just PM me with %team, and it will work even if we share multiple servers. If you want users to only be able to assign roles via PMs, post __%pm required__ in the server.

If you would just like me to create default Pokemon GO roles, someone with the Manage Server permission (or you, the owner) can type **%create_roles** in the server, and I will create empty template roles for Pokemon GO teams, which I can then assign.

**The team roles *need* to be located below goPC's role in order for them to be able to be assigned, or else it will say it does not have permissions.**

My code base, as well as some more information on what I can do, is available at https://github.com/chafla/SomebodysPC.
If you have any questions, problems, compliments, etc., you can find `Luc | ルカリオ#5653` (my writer) in the /r/PokemonGO server.
'''

stats_message = '''
Pokémon GO team stats for {0}
Users on Team Mystic: {1} ({4:.2f}%)
Users on Team Valor: {2} ({5:.2f}%)
Users on Team Instinct: {3} ({6:.2f}%)
'''

