import os
import addjson
import discord
from discord import default_permissions
from discord.ext import commands
from discord.ui import Button, View
import config
import logging
import keep_alive

logging.basicConfig(filename='logs.log',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

TOKEN = config.get_token()

## start bot, declare intents, create slash command group ##
bot = discord.Bot(intents=discord.Intents.default())


## print to terminal bot online status ##
@bot.event
async def on_ready():
  print(f"{bot.user} is ready and online!")
  logger.info('WENT ONLINE')
  #await ctx.send("Hey I'm online!")


## error handling ##
@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext,
                                       error: discord.DiscordException):
  errortype = error.original.__class__
  print(errortype)
  if errortype == KeyError:
    await ctx.respond("Whoops! Couldn't find that key!", ephemeral=True)
  elif errortype == FileNotFoundError:
    await ctx.respond(
      "Looks like you don't have any notes! Try adding a note first with /note add first!",
      ephemeral=True)
    logger.error(error)
  elif errortype == addjson.MaxNotesError:
    await ctx.respond("Too many notes! Max notes per server is 100!",
                      ephemeral=True)
    logger.error(error)
  elif errortype == addjson.SameKeyError:
    await ctx.respond(
      "There is already a note with that name! Try a different name!",
      ephemeral=True)
    logger.error(error)
  else:
    await ctx.respond(
      "Something went wrong. Try using the help command or contacting the devs.",
      ephemeral=True)
    logger.error(error)
    raise error


@bot.event
async def on_guild_join(ctx: commands.Context):
  ID = ctx.id
  addjson.create_file(ID)
  logger.info('joined ' + str(ID))


@bot.event
async def on_guild_remove(ctx: commands.Context):
  ID = ctx.id
  addjson.remove_file(ID)
  logger.info('lEFT ' + str(ID))


## add a note to the list
@bot.command(description='Add a note!')
async def addnote(ctx: commands.Context, name: str, content: str):
  key = name.lower()
  ID = ctx.guild.id
  addjson.append(ID, key, content)
  await ctx.respond("You have created a new note called " + key)


## retrieve and display note via slash command
@bot.command(description='Get a note!')
async def getnote(ctx: commands.Context, key: str):
  ID = ctx.guild.id
  content = addjson.get_content(ID, key.lower())
  await ctx.respond(content)


## Delete note
@bot.command(description='Delete a note!')
async def deletenote(ctx: commands.Context, name: str):
  ID = ctx.guild.id
  addjson.deletename(ID, name.lower())
  await ctx.respond("Deleted!")


## edit note key
@bot.command(description='Rename a note!')
async def renamenote(ctx: commands.Context, name: str, rename: str):
  name = name.lower()
  rename = rename.lower()
  ID = ctx.guild.id
  addjson.renamekey(ID, name, rename)
  await ctx.respond("Note " + name + " has been renamed to " + rename + " !")


## edit note value
@bot.command(description='Edit a note!')
async def editnote(ctx: commands.Context, name: str, content: str):
  ID = ctx.guild.id
  name = name.lower()
  addjson.editvalue(ID, name, content)
  await ctx.respond("Note " + name + " has been changed!")


@bot.command(description='Help')
async def noteshelp(ctx: commands.Context):
  embed = discord.Embed(title="By WhoZom and Ikki",
                        description="Help screen",
                        color=0x02f7a6)
  embed.set_author(name="Noteorious")
  embed.add_field(name="/notes",
                  value="See all notes on the server.",
                  inline=False)
  embed.add_field(name="/addnote", value="Add a note.", inline=True)
  embed.add_field(name="/getnote",
                  value="Get a note by giving the note name.",
                  inline=True)
  embed.add_field(name="/renamenote",
                  value="Rename an existing note.",
                  inline=True)
  embed.add_field(name="/editnote",
                  value="Edit a note by giving the note name.",
                  inline=True)
  embed.add_field(name="/deletenote",
                  value="Deletes a note by giving the note name.",
                  inline=True)
  embed.add_field(
    name="permission management",
    value=
    "To change individual command permissions, Server settings -> Integrations -> Noteorious -> Manage permissions. ",
    inline=True)
  embed.set_footer(text="@whozum_ and @ikkistan")
  await ctx.respond(embed=embed)


## pycord button subclass
class NoteButton(Button):

  def __init__(self, id, key):
    super().__init__(label=str(key), style=discord.ButtonStyle.primary)
    self.id = id

  async def callback(
      self, interaction: discord.Interaction):  #defines button behavior
    content = addjson.get_content(self.id, self.label)
    await interaction.response.edit_message(content="**" + self.label +
                                            " contains**:",
                                            view=None)
    await interaction.followup.send(content)


## pycord View subclass
class MyView(View):

  def __init__(self, ctx, keylist, id):
    super().__init__(timeout=60)
    self.id = id
    self.ctx = ctx
    for key in keylist:  #add button for every note
      self.add_item(NoteButton(self.id, key))

  async def on_timeout(self):
    for child in self.children:
      child.disabled = True
    await self.message.edit(
      content="Buttons are available for 60 seconds after you get the list!",
      view=self)

  async def interaction_check(self, interaction) -> bool:
    if interaction.user != self.ctx.author:
      await interaction.response.send_message(
        "Only the person who used the command can do that!", ephemeral=True)
      return False
    else:
      return True


## list notes as interactive buttons
@bot.command(description="Show all notes!")
async def notes(ctx):
  ID = ctx.guild.id
  keylist = addjson.listkeys(ID)

  kl_len = len(keylist)
  kl_list = [keylist[i:i + 25] for i in range(0, kl_len, 25)
             ]  #split keys into groups of 25 for pagination

  if kl_len == 0:
    await ctx.respond(
      "There aren't any notes! Try creating a note first with /note add!")
  else:
    page = 1
    for sublist in kl_list:
      view = MyView(ctx, sublist,
                    ID)  #creates custom view of up to 25 NoteButton buttons
      if page == 1:
        await ctx.respond("**These are the available notes!**", view=view)
      else:
        await ctx.respond("**Notes page " + str(page) + ":**", view=view)
      page += 1


keep_alive.keep_alive()
try:
  bot.run(TOKEN)
except:
  os.system("kill 1")
