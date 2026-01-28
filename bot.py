import discord
from discord.ext import commands
from discord import app_commands
import os
import json
from datetime import timedelta

# Token-ka waxaa laga akhrinayaa Environment Variables
TOKEN = os.environ.get("DISCORD_TOKEN")
WELCOME_FILE = "welcome_settings.json"

# --- DATABASE LOGIC ---
def load_welcome():
    if os.path.exists(WELCOME_FILE):
        with open(WELCOME_FILE, "r") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_welcome(data):
    with open(WELCOME_FILE, "w") as f:
        json.dump(data, f)

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

# --- 1. DM AUTO-RESPONSE (EMBED) ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    if isinstance(message.channel, discord.DMChannel):
        embed = discord.Embed(
            title="Nagti Shaafici Support Center 🛠️",
            description=f"Hi **{message.author.name}**, I'm Bot\nPlease use / This I'm Working!",
            color=discord.Color.blue()
        )
        view = discord.ui.View()
        invite_url = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands"
        view.add_item(discord.ui.Button(label="Add Server 🌍", url=invite_url))
        view.add_item(discord.ui.Button(label="Contact Team 👤", url="https://discord.com/users/1388255325345419409"))
        
        await message.channel.send(embed=embed, view=view)

# --- 2. WELCOME SYSTEM (EMBED) ---
@bot.event
async def on_member_join(member):
    data = load_welcome()
    g_data = data.get(str(member.guild.id))
    if g_data:
        channel = bot.get_channel(g_data["channel"])
        if channel:
            msg_content = g_data["message"].replace("{user}", member.mention).replace("{server}", member.guild.name)
            embed = discord.Embed(
                title="Welcome to the Server! 🎉",
                description=msg_content,
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"Member #{member.guild.member_count}")
            await channel.send(embed=embed)

# --- 3. MODERATION COMMANDS (EPHEMERAL) ---

@bot.tree.command(name="kick", description="User ka saar server-ka")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = "Lama sheegin"):
    await user.kick(reason=reason)
    await interaction.response.send_message(f"✅ **{user.name}** waa la kick-gareeyay.", ephemeral=True)

@bot.tree.command(name="ban", description="User ka mamnuuc server-ka")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "Lama sheegin"):
    await user.ban(reason=reason)
    await interaction.response.send_message(f"🚫 **{user.name}** waa la ban-gareeyay.", ephemeral=True)

@bot.tree.command(name="timeout", description="User-ka aamusii")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, user: discord.Member, minutes: int):
    await user.timeout(timedelta(minutes=minutes))
    await interaction.response.send_message(f"⏳ **{user.name}** timeout {minutes} min.", ephemeral=True)

# --- 4. CHANNEL CONTROL (EPHEMERAL) ---

@bot.tree.command(name="lock", description="Xir channel-ka")
@app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction, channel: discord.TextChannel):
    overwrite = channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = False
    await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message(f"🔒 {channel.mention} waa la xiray.", ephemeral=True)

@bot.tree.command(name="unlock", description="Fur channel-ka")
@app_commands.checks.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction, channel: discord.TextChannel):
    overwrite = channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = True
    await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message(f"🔓 {channel.mention} waa la furay.", ephemeral=True)

@bot.tree.command(name="slowmode", description="Saar slowmode")
async def slowmode(interaction: discord.Interaction, seconds: int):
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"⏲️ Slowmode: {seconds}s", ephemeral=True)

@bot.tree.command(name="slowmodeoff", description="Ka qaad slowmode")
async def slowmodeoff(interaction: discord.Interaction):
    await interaction.channel.edit(slowmode_delay=0)
    await interaction.response.send_message("✅ Slowmode off.", ephemeral=True)

# --- 5. SETUP & HELP ---

@bot.tree.command(name="setwelcome", description="Habee welcome embed ah")
@app_commands.checks.has_permissions(administrator=True)
async def setwelcome(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
    data = load_welcome()
    data[str(interaction.guild.id)] = {"channel": channel.id, "message": message}
    save_welcome(data)
    await interaction.response.send_message(f"✅ Welcome Embed-ka waa la dhigay {channel.mention}", ephemeral=True)

@bot.tree.command(name="invite", description="Casuun bot-ka")
async def invite(interaction: discord.Interaction):
    url = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands"
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Add Your Server 🌍", url=url))
    await interaction.response.send_message("Guji badanka hoose:", view=view, ephemeral=True)

@bot.tree.command(name="help", description="Help menu")
async def help_cmd(interaction: discord.Interaction):
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="GitHub More.. 📂", url="https://github.com/shaaficidv/Nasro-.git"))
    await interaction.response.send_message("Isticmaal `/` si aad u aragto amarrada qarsoodiga ah.", view=view, ephemeral=True)

bot.run(TOKEN)
