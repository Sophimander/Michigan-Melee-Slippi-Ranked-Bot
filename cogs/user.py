import datetime

import discord
from discord.ext import commands
from typing import Union

import math
import asyncio
from zoneinfo import ZoneInfo

import slippi.slippi_ranked as sr
import slippi.slippi_data as sd
import database.database_operations as do

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
        embed_text = ''.join([x for x in self.leaderboard[page_start:page_end]])

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
        embed_text = ''.join([x for x in self.leaderboard[page_start:page_end]])

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

            if not sr.is_valid_connect_code(user_connect_code):
                logger.debug(f'Invalid connect code: {user_connect_code}')
                await ctx.send('Invalid connect code.')
                return

            player_stats = sr.get_player_ranked_data_fast(user_connect_code)
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

            if not sr.is_valid_connect_code(user_connect_code):
                logger.debug(f'Invalid connect code: {user_connect_code}')
                await ctx.send('Invalid connect code.')
                return

            user_info = do.get_user_by_connect_code(conn, user_connect_code)

        player_stats_extended = sr.get_player_ranked_data_extra(user_info)
        logger.debug(f'player_stats_extended: {player_stats_extended}')
        if not player_stats_extended:
            logger.debug(f'Issue getting player stats')
            await ctx.send(f'Issue getting player stats')
            return

        with do.create_con(do.db_path) as conn:
            player_local_stats = do.get_user_stats_by_date(conn, player_stats_extended[0], do.get_latest_date(conn))
            logger.debug(f'player_local_stats: {player_local_stats}')

        if not player_local_stats:
            logger.debug(f'Issue getting player local stats')
            await ctx.send(f'Issue getting player local stats')
            return

        user_embed = discord.Embed(title=f'{player_local_stats[3]}. {player_local_stats[1]} [{player_local_stats[2]}]',
                                   url=f'{sr.slippi_url_prefix}{sr.connect_code_to_html(player_local_stats[2])}')
        user_embed.set_thumbnail(url=player_stats_extended[7])
        user_embed.add_field(name='Elo', value=player_stats_extended[4])
        user_embed.add_field(name='Rank', value=player_stats_extended[3])
        user_embed.add_field(name='\u200b',value='\u200b')
        user_embed.add_field(name='Wins', value=player_stats_extended[5])
        user_embed.add_field(name='Loses', value=player_stats_extended[6])
        winrate = (player_stats_extended[5] / (player_stats_extended[5]+player_stats_extended[6]))*100
        user_embed.add_field(name='Winrate', value=f'{winrate:.2f}%')

        await ctx.send(embed=user_embed)

    @commands.command(name='reg', help='Registers a user for the bot')
    async def __regUser(self, ctx: commands.Context, name, user_connect_code):

        logger.debug(f'regUser: {ctx.author.name}, {name}, {user_connect_code}')
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

        inital_description = "".join([x for x in leaderboard[0:10]])

        lb_embed = discord.Embed(title='Leaderboard',
                                 description=f'```{inital_description}```', colour=discord.Colour.green())
        lb_embed.set_thumbnail(url='https://avatars.githubusercontent.com/u/45867030?s=200&v=4')
        lb_embed.set_footer(text=string_date)
        lb_view = LeaderboardView(lb_embed, leaderboard, string_date, pages, 0)
        await ctx.send(view=lb_view, embed=lb_embed)

'''
    @commands.command(name='leaderboard', help='Prints a pagified leaderboard') 
    async def __getLeaderboard(self, ctx: commands.Context):
        logger.debug(f'getLeaderboard: {ctx.author.name}')
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

        # Set pages to amount of match_list/10 in an even amount, cur_page to last page, and active to true
        text = ''
        pages = math.ceil(len(leaderboard) / 10)
        cur_page = 0
        # Used to loop waiting for a react
        active = True

        # Generate page from match_list
        for i in range(cur_page * 10, (cur_page * 10) + 10):
            if i < len(leaderboard):
                text += leaderboard[i]  # text += str(match_list[i])

        # If pages is greater than one, add a page counter, if not set active to False
        if pages > 1:
            text += f'Page {cur_page + 1} of {pages}\t{string_date}\n'
        else:
            active = False

        # Create message with return of du.code_message
        message = await ctx.send(f"```{text}```")

        # If pages greater than one, add reaction controls
        if pages > 1:
            await message.add_reaction('\U00002B05')  # ⬅️
            await message.add_reaction('\U000027A1')  # ➡️

        # Method to check if react is the correction with the correct user
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['\U00002B05', '\U000027A1']

        # While loop
        while active:
            try:
                # page set to start of codeblock
                page = '```\n'
                # wait till we get a reaction, fill reaction, user with output of 'reaction_add'
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)
                # If reaction is left and cur_page is greater than 0
                if str(reaction.emoji) == '\U00002B05' and cur_page > 0:  # ⬅️️
                    # Set current page to one less than current
                    cur_page -= 1

                    # For range of pages for current list append match_list to page
                    for i in range(cur_page * 10, cur_page * 10 + 10):
                        page += leaderboard[i]  # match_list[i]

                    # Add page counter and edit message with page
                    page += f'Page {cur_page + 1} of {pages}\t{string_date}\n```'
                    await message.edit(content=page)

                    # Remove users reaction
                    await message.remove_reaction(reaction, user)

                # If reaction is right and cur_page is less than pages-1
                elif str(reaction.emoji) == '\U000027A1' and cur_page < pages - 1:  # ➡️
                    # Set current page to one more than current
                    cur_page += 1

                    # For range of pages for current list append match_list to page
                    for i in range(cur_page * 10, cur_page * 10 + 10):
                        if i < len(leaderboard):
                            page += leaderboard[i]  # match_list[i]

                    # Add page counter and edit message with page
                    page += f'Page {cur_page + 1} of {pages}\t{string_date}\n```'
                    await message.edit(content=page)

                    # Remove users reaction
                    await message.remove_reaction(reaction, user)
                else:
                    # Remove reaction if it's anything else
                    await message.remove_reaction(reaction, user)
            except asyncio.TimeoutError:
                # When 'reaction_add' throws exception, set active to False to end loop
                active = False
                # Get cached message to remove reactions
                cached_msg = discord.utils.get(self.bot.cached_messages, id=message.id)
                for reactions in cached_msg.reactions:
                    await reactions.remove(self.bot.user)
'''


async def setup(bot: commands.Bot):
    await bot.add_cog(UserCog(bot))
