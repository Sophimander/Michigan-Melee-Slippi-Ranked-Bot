import datetime

import discord
from discord.ext import commands
from typing import Union, Optional

import math
from zoneinfo import ZoneInfo

import database.database_operations as do
import slippi.slippi_api as sa
import slippi.slippi_data as sd

from players import errors, users, local_user

import logging

logger = logging.getLogger(f'slippi_bot.{__name__}')

discordMemberStr = Union[discord.Member, str]
memberstr_description = 'Connect code or a discord member, if left empty it will use the person who issues the command'
memberstr_parameter = commands.parameter(default=lambda ctx: ctx.author, description=memberstr_description)
memberbool_description = 'Boolean (ex. 0, 1, True, False) or a discord member'


def has_database_permission():
    async def predicate(ctx: commands.Context):
        """Returns true if is me
        **Arguments**
        - `<ctx>` Context to check.
        """

        return ctx.author.id == 126913881879740416

    return commands.check(predicate)


class LeaderboardView(discord.ui.View):

    def __init__(self, embed: discord.Embed, leaderboard: list[str], date: str, pages: int, cur_page: int):
        super().__init__(timeout=180)
        self.embed = embed
        self.leaderboard = leaderboard
        self.date = date
        self.pages = pages
        self.cur_page = cur_page

    @discord.ui.button(emoji='⬅️', style=discord.ButtonStyle.green)
    async def button_callback_left(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.cur_page:
            self.cur_page -= 1
        else:
            self.cur_page = self.pages - 1

        page_start = self.cur_page * 10
        page_end = page_start + 10
        embed_text = '\n'.join([x for x in self.leaderboard[page_start:page_end]])

        self.embed.description = f'```{embed_text}```'
        await interaction.response.edit_message(embed=self.embed)

    @discord.ui.button(emoji='➡️', style=discord.ButtonStyle.green)
    async def button_callback_right(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.cur_page < self.pages - 1:
            self.cur_page += 1
        else:
            self.cur_page = 0

        page_start = self.cur_page * 10
        page_end = page_start + 10
        embed_text = '\n'.join([x for x in self.leaderboard[page_start:page_end]])

        self.embed.description = f'```{embed_text}```'
        await interaction.response.edit_message(embed=self.embed)


class UserCog(commands.Cog, name='Users'):

    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        logger.error(f'{error}')

        if isinstance(error.__cause__, errors.UserError):
            await ctx.send(f'{error.__cause__.message}')
            return

        await ctx.send('An error occurred: {}'.format(str(error)))

    @commands.command(name='refresh', help='Creates a ranked stats snapshot (Soph only)')
    @has_database_permission()
    async def __refresh_database(self, ctx: commands.Context):
        with do.create_con(do.db_path) as conn:
            results = sd.write_snapshot(conn)
            logger.debug(f'database_refresh: {results}')
        return results

    @commands.command(name='edituser', help='Edits a user manually (Soph only)')
    @has_database_permission()
    async def __edit_user(self, ctx: commands.Context, uid_target: int, uid_new: int, name: str, connect_code: str):
        logger.debug(f'edit_user: {uid_target}, {uid_new}, {name}, {connect_code}')
        with do.create_con(do.db_path) as conn:
            if do.update_user_name(conn, uid_target, name):
                logger.debug(f'editUser: name updated successfully')
                if do.update_user_connect_code(conn, uid_target, connect_code):
                    logger.debug(f'editUser: connect_code updated successfully')
                    if do.update_user_uid(conn, uid_target, uid_new):
                        logger.debug(f'editUser: uid updated successfully')
                        if do.update_elo_uid(conn, uid_target, uid_new):
                            logger.debug('editUser: elo updated successfully')
                            if do.update_rank_uid(conn, uid_target, uid_new):
                                logger.debug('editUser: rank updated successfully')
                                if do.update_win_loss_uid(conn, uid_target, uid_new):
                                    logger.debug('editUser: win_loss updated successfully')
                                    if do.update_leaderboard_uid(conn, uid_target, uid_new):
                                        logger.debug('editUser: leaderboard updated successfully')
                                        await ctx.send('User info updated')

    @commands.command(name='stats', help='Prints a users slippi ranked stats in chat')
    async def __get_stats(self, ctx: commands.Context, user_info: discordMemberStr = memberstr_parameter):
        logger.debug(f'get_stats: {ctx.author.name}: {user_info}')

        uid = 0
        cc = ''

        if isinstance(user_info, str):
            cc = user_info.lower()

        if isinstance(user_info, discord.Member):
            uid = user_info.id

        player = local_user.LocalUser(id=uid, connect_code=cc)
        if isinstance(user_info, discord.Member):
            player.assign_data_local()
        player.assign_slippi_data()

        logger.debug(f'player: {player}')

        await ctx.send(f"{player.connect_code}: {player.rank} | "
                       f"{player.elo} | "
                       f"({player.wins}/{player.losses})")

    @commands.command(name='user', help='Prints a detailed page of player info')
    async def __user(self, ctx: commands.Context, user_info: Optional[discordMemberStr] = memberstr_parameter):
        logger.debug(f'__user: {ctx.author}: {user_info}')

        uid = 0
        cc = ''

        if isinstance(user_info, str):
            cc = user_info.lower()

        if isinstance(user_info, discord.Member):
            uid = user_info.id

        player = local_user.get_user_local(uid, cc)
        try:
            player.assign_data_local()
        except Exception as error:
            if not isinstance(error, errors.FailedToGetLocalUserData):
                raise error

        player.assign_slippi_data()

        user_embed = discord.Embed(title=f'{player.position}. {player.name} [{player.connect_code}]',
                                   url=f'{sa.slippi_url_prefix}{sa.connect_code_to_html(player.connect_code)}')
        if player.characters:
            user_embed.set_thumbnail(url=player.characters[0].get_character_icon_url())
        else:
            user_embed.set_thumbnail(url='https://avatars.githubusercontent.com/u/45867030?s=200&v=4')
        user_embed.add_field(name='Elo', value=player.elo)
        user_embed.add_field(name='Rank', value=player.rank)
        user_embed.add_field(name='\u200b', value='\u200b')
        user_embed.add_field(name='Wins', value=player.wins)
        user_embed.add_field(name='Loses', value=player.losses)
        win_rate = (player.wins / (player.wins + player.losses)) * 100
        user_embed.add_field(name='Win rate', value=f'{win_rate:.2f}%')

        await ctx.send(embed=user_embed)

    @commands.command(name='reg', help='Registers a user for the bot')
    async def __reg_user(self, ctx: commands.Context, name: str, user_connect_code: str):
        logger.debug(f'reg_user: {ctx.author.name}, {name}, {user_connect_code}')

        if len(name) > 12:
            await ctx.send(f'Your name must be 12 characters or less. Your name was {len(name)} characters long')
            return

        connect_code_uid = 0
        with do.create_con(do.db_path) as conn:

            user_connect_code = user_connect_code.lower()
            results = sd.create_user_entry(conn, ctx.author.id, name, user_connect_code)
            logger.debug(f'results: {results}')

            # Check if user or connect code exists, then get the uid of the connect code
            if results == sd.ExitCode.USER_ALREADY_EXISTS or results == sd.ExitCode.CONNECT_CODE_ALREADY_EXISTS:
                connect_code_uid = do.get_user_by_connect_code(conn, user_connect_code)

                # Check if user for connect_code exists
                if not connect_code_uid:
                    do.update_user_connect_code(conn, ctx.author.id, user_connect_code)
                    await ctx.send('Updated player info.')
                    return

                # Check that connect_code uid matches author id
                if connect_code_uid[0] and connect_code_uid[0] == ctx.author.id:
                    if not do.update_user_connect_code(conn, ctx.author.id, user_connect_code):
                        await ctx.send('Error updating connect code')
                        return
                    if not do.update_user_name(conn, ctx.author.id, name):
                        await ctx.send('Error updating name')
                        return
                    await ctx.send('Updated player info')
                    return
                else:
                    await ctx.send('Someone else already has that connect code')
                    return
            elif results == sd.ExitCode.USER_CREATED_SUCCESSFULLY:
                await ctx.send('Thank you for registering')
                return

            await ctx.send('Unable to update info')

    @commands.command(name='leaderboard', help='Prints a pagified leaderboard')
    async def __leaderboard(self, ctx: commands.Context,
                            focus_me:  bool | discord.Member =
                            commands.parameter(default=None, description=memberbool_description)):
        logger.debug(f'leaderboard: {ctx.author}, {focus_me}')

        focus_user = 0

        if focus_me:
            focus_user = local_user.get_user_local(focus_me.id if isinstance(focus_me, discord.Member) else ctx.author)
            focus_user.assign_data_local()

        with do.create_con(do.db_path) as conn:
            leaderboard = sd.generate_leaderboard_text(conn)
            latest_date = do.get_latest_date(conn)

        if isinstance(leaderboard, sd.ExitCode) or not latest_date:
            await ctx.send('Error getting leaderboard data, please try again later')
            return

        logger.debug(f'{latest_date} | {leaderboard}')

        string_date = 'Failed to get date.'
        if latest_date:
            string_date = latest_date.astimezone(tz=ZoneInfo('America/Detroit')).strftime('%Y-%m-%d %H:%M:%S')

        pages = math.ceil(len(leaderboard) / 10)
        cur_page = 0

        if focus_me:
            cur_page = math.ceil(focus_user.position / 10)
            if cur_page:
                cur_page -= 1

        page_start = cur_page * 10
        page_end = page_start + 10

        inital_description = '\n'.join([x for x in leaderboard[page_start:page_end]])

        lb_embed = discord.Embed(title='Leaderboard',
                                 description=f'```{inital_description}```', colour=discord.Colour.green())
        lb_embed.set_thumbnail(url='https://avatars.githubusercontent.com/u/45867030?s=200&v=4')
        lb_embed.set_footer(text=string_date)
        lb_view = LeaderboardView(lb_embed, leaderboard, string_date, pages, 0)
        await ctx.send(view=lb_view, embed=lb_embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(UserCog(bot))
