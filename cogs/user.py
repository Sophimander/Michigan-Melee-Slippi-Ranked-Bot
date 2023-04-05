import datetime

import discord
from discord.ext import commands
from typing import Union

import math
import asyncio
from zoneinfo import ZoneInfo

import slippi.slippi_api as sa
import slippi.slippi_data as sd
import database.database_operations as do
from users.users import *

import logging

logger = logging.getLogger(f'slippi_bot.{__name__}')


def has_database_permission():
    async def predicate(ctx: commands.Context):
        """Returns true if is me
        **Arguments**
        - `<ctx>` Context to check.
        """

        return ctx.author.id == 126913881879740416
    return commands.check(predicate)


class LeaderboardView(discord.ui.View):

    def __init__(self, embed: discord.Embed, leaderboard: list[str], date:str, pages: int, cur_page: int):
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

    async def cog_command_error(self, ctx: commands.Context,
                                error: commands.CommandError):
        logger.error(f'{error}')
        await ctx.send('An error occurred: {}'.format(str(error)))

    @commands.command(name='refresh', help='Creates a ranked stats snapshot (Soph only)')
    @has_database_permission()
    async def __refreshDatabase(self, ctx: commands.Context):
        with do.create_con(do.db_path) as conn:
            results = sd.write_snapshot(conn)
            logger.debug(f'database_refresh: {results}')
        return results

    @commands.command(name='edituser', help='Edits a user manually (Soph only)')
    @has_database_permission()
    async def __editUser(self, ctx: commands.Context, uid_target: int, uid_new: int, name: str, connect_code: str):
        logger.debug(f'editUser: {uid_target}, {uid_new}, {name}, {connect_code}')
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
    async def __getStats(self, ctx: commands.Context, user_connect_code: Union[discord.Member, str] = None):
        logger.debug(f'getStats: {ctx.author.name}: {user_connect_code}')

        if type(user_connect_code) == str:
            user_connect_code = user_connect_code.lower()
        with do.create_con(do.db_path) as conn:

            if not user_connect_code or type(user_connect_code) == discord.Member:
                user = do.get_user_by_uid(conn, ctx.author.id if not user_connect_code else user_connect_code.id)
                if not user:
                    logger.debug(f'User not found: {ctx.author.id} | {user_connect_code}')
                    await ctx.send("Not registered please use the \"$reg\" command to register.")
                    return
                user_connect_code = user[2]

            if not sa.is_valid_connect_code(user_connect_code):
                logger.debug(f'Invalid connect code: {user_connect_code}')
                await ctx.send('Invalid connect code.')
                return

            player_stats = sa.get_player_ranked_data_fast(user_connect_code)
            logger.debug(f'player_stats: {player_stats}')

            if not player_stats:
                await ctx.send('Unable to find user.')
                return

            await ctx.send(f"{player_stats[0]}: {player_stats[1]} | "
                           f"{player_stats[2]} | "
                           f"({player_stats[3]}/{player_stats[4]})")

    @commands.command(name='user', help='Prints a detailed page of user info')
    async def __User(self, ctx: commands.Context, user_connect_code: Union[discord.Member, str] = None):
        logger.debug(f'__User: {ctx.author}: {user_connect_code}')

        uid = 0

        if isinstance(user_connect_code, str):
            user_connect_code = user_connect_code.lower()

        if isinstance(user_connect_code, discord.Member):
            uid = user_connect_code.id

        if user_connect_code is None:
            uid = ctx.author.id

        user = get_user_local_cc(user_connect_code)\
            if isinstance(user_connect_code, str) else get_user_local_uid(uid)

        if user == sd.ExitCode.FAILED_TO_GET_PLAYER:
            logger.debug(f'User not found: {ctx.author.id} | {user_connect_code}')
            await ctx.send('Not registered please use the \"$reg\" command to register.')
            return

        if not user.assign_data_local() == sd.ExitCode.USER_ASSIGNED_SUCCESSFULLY:
            logger.debug(f'Unable to assign user local: {user}')

        if not user.assign_slippi_data() == sd.ExitCode.USER_ASSIGNED_SUCCESSFULLY:
            logger.debug(f'Unable to assign user: {user}')
            await ctx.send('Was unable to get stats, try again later.')
            return

        user_embed = discord.Embed(title=f'{user.position}. {user.name} [{user.connect_code}]',
                                   url=f'{sa.slippi_url_prefix}{sa.connect_code_to_html(user.connect_code)}')
        user_embed.set_thumbnail(url=user.characters[0])
        user_embed.add_field(name='Elo', value=user.elo)
        user_embed.add_field(name='Rank', value=user.rank)
        user_embed.add_field(name='\u200b', value='\u200b')
        user_embed.add_field(name='Wins', value=user.wins)
        user_embed.add_field(name='Loses', value=user.losses)
        winrate = (user.wins / (user.wins+user.losses))*100
        user_embed.add_field(name='Winrate', value=f'{winrate:.2f}%')

        await ctx.send(embed=user_embed)

    @commands.command(name='reg', help='Registers a user for the bot')
    async def __regUser(self, ctx: commands.Context, name, user_connect_code):

        logger.debug(f'regUser: {ctx.author.name}, {name}, {user_connect_code}')

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
    async def __lb2(self, ctx: commands.Context):
        logger.debug(f'lb2: {ctx.author}')

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

        inital_description = '\n'.join([x for x in leaderboard[0:10]])

        lb_embed = discord.Embed(title='Leaderboard',
                                 description=f'```{inital_description}```', colour=discord.Colour.green())
        lb_embed.set_thumbnail(url='https://avatars.githubusercontent.com/u/45867030?s=200&v=4')
        lb_embed.set_footer(text=string_date)
        lb_view = LeaderboardView(lb_embed, leaderboard, string_date, pages, 0)
        await ctx.send(view=lb_view, embed=lb_embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(UserCog(bot))
