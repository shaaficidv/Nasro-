import discord
from discord.ext import commands
from discord import app_commands
import os
import json
from datetime import timedelta
from typing import Optional

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

# --- 1. DM AUTO-RESPONSE ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if isinstance(message.channel, discord.DMChannel):
        embed = discord.Embed(
            title="Nagti Shaafici Support Center 🛠️",
            description=f"Hi **{message.author.name}**, I'm Bot\nPlease use `/` This I'm Working!",
            color=discord.Color.blue()
        )
        view = discord.ui.View()
        invite_url = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands"
        view.add_item(discord.ui.Button(label="Add Server 🌍", url=invite_url))
        view.add_item(discord.ui.Button(label="Contact Team 👤", url="https://discord.com/users/1388255325345419409"))
        await message.channel.send(embed=embed, view=view)

# --- 2. THE NEW /MSG COMMAND ---
@bot.tree.command(name="msg", description="Fariin Embed ah u dir Channel ama User")
@app_commands.describe(channel="Channel-ka fariinta lagu dirayo", user="User-ka la mention-gareeyo", message="Fariintaada")
async def msg(interaction: discord.Interaction, message: str, channel: Optional[discord.TextChannel] = None, user: Optional[discord.Member] = None):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)

    embed = discord.Embed(description=message, color=discord.Color.random())
    
    if channel:
        await channel.send(embed=embed)
        await interaction.response.send_message(f"✅ Fariintaada waxaa lagu diray {channel.mention}", ephemeral=True)
    elif user:
        await interaction.channel.send(content=f"{user.mention}", embed=embed)
        await interaction.response.send_message(f"✅ Fariintaada waxaa loo tag-gareeyay {user.name}", ephemeral=True)
    else:
        await interaction.response.send_message("Fadlan dooro Channel ama User midkood!", ephemeral=True)

# --- 3. MODERATION COMMANDS (WITH PERMISSION MESSAGE) ---

@bot.tree.command(name="kick", description="User ka saar server-ka")
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = "Lama sheegin"):
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    await user.kick(reason=reason)
    await interaction.response.send_message(f"✅ **{user.name}** waa la kick-gareeyay.", ephemeral=True)

@bot.tree.command(name="ban", description="User ka mamnuuc server-ka")
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "Lama sheegin"):
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    await user.ban(reason=reason)
    await interaction.response.send_message(f"🚫 **{user.name}** waa la ban-gareeyay.", ephemeral=True)

@bot.tree.command(name="lock", description="Xir channel-ka")
async def lock(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    overwrite = channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = False
    await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message(f"🔒 {channel.mention} waa la xiray.", ephemeral=True)

# --- 4. HELP & INVITE ---

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
