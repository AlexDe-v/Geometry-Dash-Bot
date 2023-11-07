import discord
from discord import Emoji, Forbidden, InputText, LoginFailure, Option, Role
import os
import random
import discord.ext.tasks
import json
from discord import Interaction
import random
from discord.ui import Button, View
import asyncio
import discord.utils
import time
from discord.utils import get

from pyparsing import Opt, empty
import gd

intents = discord.Intents.all()
client = discord.Bot(command_prefix='!', intents=intents)
dash = gd.Client()
servers = [989178425870782514]
token= os.getenv("DEV_TOKEN")

@client.slash_command(name = 'daily', description = 'Gets the daily level')
async def daily(ctx):
    lvl = await dash.get_daily()
    lvl_id = lvl.id
    await level_cmd(ctx, lvl_id)
    #Gets daily Level Id and redirects it to daily function


async def level_cmd(ctx, id: Option(int)):
    await ctx.channel.trigger_typing()
    lvl = await dash.get_level(id, False)
    embed=discord.Embed(title=f"Level: {lvl.name} ({lvl.id})", description=f"\n**Creator**: {lvl.creator.name}\n**Difficulty**: {lvl.difficulty.title} ({lvl.stars} :star:) \n**Song**: {lvl.song} ({lvl.song.id}) \n**Password**: ||{lvl.password}|| \n**Description**: {lvl.description}", color=0xf7e372)
    embed.set_thumbnail(url="https://www.pngitem.com/pimgs/m/198-1982974_insane-icon-geometry-dash-hd-png-download.png")

    button = Button(label="GD Browser", url=f"https://gdbrowser.com/{id}")
    button2 = Button(label="Like", style=discord.ButtonStyle.green, emoji="👍")
    button3 = Button(label="Comment", style=discord.ButtonStyle.blurple, emoji="📝")


    async def likelvl(inter):
        print('button')
        with open('pass.json', 'r') as f:
            passes = json.load(f)
        with open('names.json', 'r') as f:
            names = json.load(f)
        if str(ctx.author.id) in passes:
            user = names[str(ctx.author.id)]
            userpass = passes[str(ctx.author.id)]
            try:
                await dash.login(f'{user}', f'{userpass}')
                await lvl.like()
            except gd.LoginFailure:
                eembed=discord.Embed(title=":warning: | Your password or name is invalid!", color=0xff8080)
                await inter.response.send_message(embed=eembed, ephemeral=True)
                return
            call_embed=discord.Embed(title=":thumbsup: | Liked, it may take up to 5m to update!", color=0x5fff5c)
            await inter.response.send_message(embed=call_embed, ephemeral=True)
        else:
            cembed=discord.Embed(title=":warning: | Account not connected!", description="You need to have your acccount name and pasword linked to like Levels! Run /gdconnect and /connectpass.", color=0xff7070)
            await inter.response.send_message(embed=cembed, ephemeral=True)

    async def comment(inter):
        with open('pass.json', 'r') as f:
            passes = json.load(f)
        if not str(ctx.author.id) in passes:
            cembed=discord.Embed(title=":warning: | Account not connected!", description="You need to have your acccount name and pasword linked to like Levels! Run /gdconnect and /connectpass.", color=0xff7070)
            await inter.response.send_message(embed=cembed, ephemeral=True)
        else:
            userpass = passes[str(ctx.author.id)]
            with open('names.json', 'r') as f:
                users = json.load(f)
            user = users[str(ctx.author.id)]
            try:
                await dash.login(f'{user}', f'{userpass}')
                embed=discord.Embed(title=":pencil: | Write your comment now. Type !exit to cancel", color=0xff8080)
                await inter.response.send_message(embed=embed, ephemeral=True)
                with open('cmode.json', 'r') as f:
                    data = json.load(f)
                data[str(ctx.author.id)] = lvl.id
                with open('cmode.json', 'w') as f:
                    data = json.dump(data, f)
            except gd.LoginFailure:
                eembed=discord.Embed(title=":warning: | Your password or name is invalid!", color=0xff8080)
                await ctx.respond(embed=eembed, ephemeral=True)


    button2.callback = likelvl
    button3.callback = comment
    
    view = View()
    view.add_item(button)
    view.add_item(button2)
    view.add_item(button3)
    await ctx.respond(embed=embed, view=view)



@client.event
async def on_message(message):
    with open('cmode.json', 'r') as f:
        data = json.load(f)
    if '!exi' in message.content or '!cancel' in message.content:
        embed=discord.Embed(title=":warning: | Comment has not been send!", color=0x5cff8d)
        await message.reply(embed=embed, delete_after=4)
        await message.delete()
        data.pop(str(message.author.id))
        with open('cmode.json', 'w') as f:
            data = json.dump(data, f)
    else:
        with open('cmode.json') as f:
            data = json.load(f)
        if not str(message.author.id) in data:
            pass
        else:
            #Code if user is writing a comment
            with open('pass.json', 'r') as f:
                passes = json.load(f)
            userpass = passes[str(message.author.id)]
            with open('names.json', 'r') as f:
                users = json.load(f)
            user = users[str(message.author.id)]
            try:
                #Code if everything is right
                await dash.login(f'{user}', f'{userpass}')
                lvl_id = data[str(message.author.id)]
                level = await dash.get_level(lvl_id)
                try:
                    await level.comment(f'{message.content}')
                    data.pop(str(message.author.id))
                    with open('cmode.json', 'w') as f:
                        data = json.dump(data, f)
                    #embed here
                    embed=discord.Embed(title=":white_check_mark: | Send comment!", color=0x5cff8d)
                    await message.reply(embed=embed, delete_after=2)
                    await message.delete()
                except gd.HTTPError:
                    data.pop(str(message.author.id))
                    embed=discord.Embed(title=":warning: | Comment cooldown!", color=0x5cff8d)
                    await message.reply(embed=embed, delete_after=2)
                    await message.delete()
                    return
                    
            except gd.LoginFailure:
                await message.reply('error: Logginfailure')





@client.slash_command(name = 'connectpass', description = 'connect your GD password!')
async def passcon(ctx, gd_pass: Option(str)):
    with open('names.json', 'r') as f:
        names = json.load(f)
    if str(ctx.author.id) in names:
        user = names[str(ctx.author.id)]
        with open('pass.json', 'r') as f:
            data = json.load(f)
        data[str(ctx.author.id)] = gd_pass
        with open('pass.json', 'w') as f:
            data = json.dump(data, f)
        embed=discord.Embed(title=":white_check_mark: | Password linked!", description=f"Linked your password (||{gd_pass}||) with ({user})! This allows you to comment, like levels and more! To remove everything we know about you run **/resetconnect!**", color=0xa9ff70)
        await ctx.respond(embed=embed, ephemeral=True)
    else:
        embed=discord.Embed(title=":warning: | You need to link your name first! /gdconnect", color=0xffd270)
        await ctx.respond(embed=embed, ephemeral=True)

@client.slash_command(name = 'resetconnect', description = 'removes your GD name and password')
async def resetcon(ctx):
    embed=discord.Embed(title=":warning: | Warning", description="This will unlink your username and password from your discord!", color=0xffda24)
    button = Button(label="Yes do it!", style=discord.ButtonStyle.red)
    view = View()
    async def confirmremove(inter):
        call_embed=discord.Embed(title=":white_check_mark: | Done! Unlinked everything.", color=0x5fff5c)
        await inter.response.send_message(embed=call_embed, ephemeral=True)
        with open('names.json', 'r') as f:
            names = json.load(f)
        names.pop(str(ctx.author.id))
        with open('names.json', 'w') as f:
            names = json.dump(names, f)
        with open('pass.json', 'r') as f:
            names = json.load(f)
        names.pop(str(ctx.author.id))
        with open('pass.json', 'w') as f:
            names = json.dump(names, f)
    button.callback = confirmremove
    view.add_item(button)
    await ctx.respond(embed=embed, view=view, ephemeral=True)


@client.slash_command(name = 'stats', description = 'Gets GD stats of user')
async def stats(ctx, user: Option(discord.Member)):
    with open('names.json', 'r') as f:
        data = json.load(f)
    if not str(user.id) in data:
        no_acc=discord.Embed(title=":warning: | User is not connected with a name!", color=0xffa66b)
        await ctx.respond(embed=no_acc, ephemeral=True)
    else:
        name = data[str(user.id)]
        target = await dash.search_user(f'{name}')
        lvls = await target.get_levels()
        embed=discord.Embed(title=f"{user}'s stats", description=f"**GD Name:** {target.name}\n:star: {target.stars} - Stars\n:smiling_imp: {target.demons} - Demons\n:hammer_pick: {target.cp} - CPs\n:second_place: {target.user_coins} - User Coins\n:medal: {target.coins} - Secret Coins\n:gem: {target.diamonds} - Diamonds \n:house: {len(lvls)} - Levels \n:trophy: #{target.rank} - Leaderboard Place", color=0x9f85ff)
        await ctx.respond(embed=embed)
        embed=discord.Embed(title=f"{user}'s GD Socials", description=f"[Twitch]({target.twitch_link}) [YouTube]({target.youtube_link}) [Twitter]({target.twitter_link})", color=0xff8585)
        await ctx.send(embed=embed)

@client.slash_command(name = 'friend', description = 'Friend a discords user GD accout')
async def friend(ctx, user: Option(discord.Member), text: Option(str)):
    dc_user = user
    with open('names.json', 'r') as f:
        users = json.load(f)
    if not str(user.id) in users:
        no_acc=discord.Embed(title=":warning: | User is not connected with a name!", color=0xffa66b)
        await ctx.respond(embed=no_acc, ephemeral=True)
    else:
        gd_user_name = users[str(user.id)]
        try:
            gd_user = await dash.find_user(f'{gd_user_name}')
        except gd.MissingAccess:
            invalid=discord.Embed(title=":warning: | User is connected with an invalid name or he has friend req off!", color=0xffa66b)
            await ctx.respond(embed=invalid, ephemeral=True)
        with open('pass.json', 'r') as f:
            passes = json.load(f)
        if not str(ctx.author.id) in passes:
            cembed=discord.Embed(title=":warning: | Account not connected!", description="You need to link your pass to send Frind Requests! Run **/gdconnect** and **/connectpass**.", color=0xff7070)
            await ctx.respond(embed=cembed, ephemeral=True)
        else:
            user = users[str(ctx.author.id)]
            userpass = passes[str(ctx.author.id)]
            try:
                #Real without errors
                await dash.login(f'{user}', f'{userpass}')
                await dash.send_friend_request(gd_user, f'{text}')
                embed=discord.Embed(title=":white_check_mark: | Send! User recived a DM.", color=0x6bff89)
                uembed=discord.Embed(title=f":fire: | Friend Request", description=f"You have recived a friend request in Geometry Dash from **{ctx.author}**, his GD name is **{user}**", color=0x9b80ff)
                try:
                    await dc_user.send(embed=uembed)
                    await ctx.respond(embed=embed)
                except Forbidden:
                    embed=discord.Embed(title=":white_check_mark: | Send! But user could not recived a DM.", color=0x6bff89)
                    await ctx.respond(embed=embed)

                
            except gd.LoginFailure:
                eembed=discord.Embed(title=":warning: | Your password or name is invalid!", color=0xff8080)
                await ctx.respond(embed=eembed, ephemeral=True)
                return



@client.slash_command(name = 'search', description = 'searches for a level')
async def search(ctx, id_or_name: Option(str)):
    try:
        inter = int(id_or_name)
        await level_cmd(ctx, id_or_name)
    except ValueError:
        lvls = await dash.search_levels(id_or_name)
        i = 0
        embed=discord.Embed(title="Search:", description=f"Levels for the search {id_or_name}. To get Info on a Level click the buttons bellow!", color=0x8c75ff)
        for level in lvls:
            if i < 4:
                embed.add_field(name=f"{level.name}", value=f"by: {level.creator}, {level.difficulty.name}", inline=False)
                i = i +1
            else:
                lvl1 = Button(label="1")
                lvl2 = Button(label="2")
                lvl3 = Button(label="3")
                lvl4 = Button(label="4")

                view = View()
                view.add_item(lvl1)
                view.add_item(lvl2)
                view.add_item(lvl3)
                view.add_item(lvl4)

                async def callback1(inter):
                    level_id = lvls[0].id
                    lvl = await dash.get_level(level_id, False)
                    await getlvlembed(inter, level_id)

                async def callback2(inter):
                    level_id = lvls[1].id
                    lvl = await dash.get_level(level_id, False)
                    await getlvlembed(inter, level_id)

                async def callback3(inter):
                    level_id = lvls[2].id
                    lvl = await dash.get_level(level_id, False)
                    await getlvlembed(inter, level_id)

                async def callback4(inter):
                    level_id = lvls[3].id
                    lvl = await dash.get_level(level_id, False)
                    await getlvlembed(inter, level_id)

                lvl1.callback = callback1
                lvl2.callback = callback2
                lvl3.callback = callback3
                lvl4.callback = callback4
                await ctx.respond(embed=embed, view=view)
                break
    


async def getlvlembed(ctx, id: Option(int)):
    lvl = await dash.get_level(id, False)
    embed=discord.Embed(title=f"Level: {lvl.name} ({lvl.id})", description=f"\n**Creator**: {lvl.creator.name}\n**Difficulty**: {lvl.difficulty.title} ({lvl.stars} :star:) \n**Song**: {lvl.song} ({lvl.song.id}) \n**Password**: ||{lvl.password}|| \n**Description**: {lvl.description}", color=0xf7e372)
    embed.set_thumbnail(url="https://www.pngitem.com/pimgs/m/198-1982974_insane-icon-geometry-dash-hd-png-download.png")

    button = Button(label="GD Browser", url=f"https://gdbrowser.com/{id}")
    button2 = Button(label="Like", style=discord.ButtonStyle.green, emoji="👍")
    button3 = Button(label="Comment", style=discord.ButtonStyle.blurple, emoji="📝")


    async def likelvl(inter):
        print('button')
        with open('pass.json', 'r') as f:
            passes = json.load(f)
        with open('names.json', 'r') as f:
            names = json.load(f)
        if str(ctx.user.id) in passes:
            user = names[str(ctx.user.id)]
            userpass = passes[str(ctx.user.id)]
            try:
                await dash.login(f'{user}', f'{userpass}')
                await lvl.like()
            except gd.LoginFailure:
                eembed=discord.Embed(title=":warning: | Your password or name is invalid!", color=0xff8080)
                await inter.response.send_message(embed=eembed, ephemeral=True)
                return
            call_embed=discord.Embed(title=":thumbsup: | Liked, it may take up to 5m to update!", color=0x5fff5c)
            await inter.response.send_message(embed=call_embed, ephemeral=True)
        else:
            cembed=discord.Embed(title=":warning: | Account not connected!", description="You need to have your acccount name and pasword linked to like Levels! Run /gdconnect and /connectpass.", color=0xff7070)
            await inter.response.send_message(embed=cembed, ephemeral=True)

    async def comment(inter):
        with open('pass.json', 'r') as f:
            passes = json.load(f)
        if not str(ctx.user.id) in passes:
            cembed=discord.Embed(title=":warning: | Account not connected!", description="You need to have your acccount name and pasword linked to like Levels! Run /gdconnect and /connectpass.", color=0xff7070)
            await inter.response.send_message(embed=cembed, ephemeral=True)
        else:
            userpass = passes[str(ctx.user.id)]
            with open('names.json', 'r') as f:
                users = json.load(f)
            user = users[str(ctx.user.id)]
            try:
                await dash.login(f'{user}', f'{userpass}')
                embed=discord.Embed(title=":pencil: | Write your comment now. Type !exit to cancel", color=0xff8080)
                await inter.response.send_message(embed=embed, ephemeral=True)
                with open('cmode.json', 'r') as f:
                    data = json.load(f)
                data[str(ctx.user.id)] = lvl.id
                with open('cmode.json', 'w') as f:
                    data = json.dump(data, f)
            except gd.LoginFailure:
                eembed=discord.Embed(title=":warning: | Your password or name is invalid!", color=0xff8080)
                await ctx.response.send_message(embed=eembed, ephemeral=True)



    button2.callback = likelvl
    button3.callback = comment
    
    view = View()
    view.add_item(button)
    view.add_item(button2)
    view.add_item(button3)
    await ctx.response.edit_message(embed=embed, view=view)


@client.slash_command(name = 'check', description = 'does stuff')
async def check(ctx, name):
    target = await dash.search_user(f'{name}')
    comments = await target.get_comments()
    latest = comments[0]
    if f'gdcon' in latest.body:
        await ctx.respond('Yes!')
    else:
        await ctx.respond('No!')

@client.slash_command(name = 'gdconnect', description = 'connect your GD account!')
async def conect(ctx, gd_name: Option(str)):
    try:
        target = await dash.search_user(f'{gd_name}')
        comments = await target.get_comments()
        latest = comments[0]
        if f'gdcon' in latest.body:
            with open('names.json', 'r') as f:
                data = json.load(f)
            data[str(ctx.author.id)] = gd_name
            with open('names.json', 'w') as f:
                data = json.dump(data, f)
            embed=discord.Embed(title=":white_check_mark: | Name linked", description=f"Hi **{gd_name}**! If you want to comment, like or manage friend requests you need to **/connectpass**. You can alaways delete it with **/resetconnect** \n\n:warning: | We highly recommend you to delete the gdcon message!", color=0x70ff8d)
            await ctx.respond(embed=embed)
        else:
            embed=discord.Embed(title=":warning: | Verification started", description="You need to make a **profile comment** and put **'gdcon'** in it. Then use the **command again**.", color=0xffd642)
            await ctx.respond(embed=embed, ephemeral=True)
    except gd.MissingAccess:
        embed=discord.Embed(title=":warning: | User not found!", color=0xffd642)
        await ctx.respond(embed=embed, ephemeral=True)


@dash.event
async def on_level_comment(level: gd.Level, comment: gd.Comment) -> None:
    print(comment.body)

@client.slash_command(name = 'mail', description = 'checks your GD mailbox')
async def mail(ctx):
    with open('pass.json', 'r') as f:
        passes = json.load(f)
    if not str(ctx.author.id) in passes:
        cembed=discord.Embed(title=":warning: | Account not connected!", description="You need to have your acccount name and pasword linked to like Levels! Run /gdconnect and /connectpass.", color=0xff7070)
        await ctx.respond(embed=cembed, ephemeral=True)
    with open('names.json', 'r') as f:
        names = json.load(f)
    user = names[str(ctx.author.id)]
    userpass = passes[str(ctx.author.id)]
    try:
        #Real code
        await dash.login(f'{user}', f'{userpass}')
        msgs = await dash.get_messages('inbox')
        if msgs is empty:
            cembed=discord.Embed(title=":warning: | You do not have any messages!", color=0xff7070)
            await ctx.respond(embed=cembed, ephemeral=True)
        else:
            embed=discord.Embed(title=":inbox_tray: | Messages", color=0x83ff7a)
            i = 0
            for message in msgs:
                if i < 5:
                        await message.read()
                        embed.add_field(name=f"**{message.subject}** by: **{message.author}**", value=f"> {message.body}", inline=False)
                        i = i +1
                else:
                    break
            await ctx.respond(embed=embed, ephemeral=True)
                



    except LoginFailure:
        cembed=discord.Embed(title=":warning: | Account data invalid!", color=0xff7070)
        await ctx.respond(embed=cembed, ephemeral=True)



@client.slash_command(name = 'recent', description = 'check da recent tab for content')
async def recent(ctx):
    recent_filter = gd.Filters 
    dash.search_levels


client.run(token)