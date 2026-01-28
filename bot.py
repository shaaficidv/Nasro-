import discord
from discord.ext import commands
from discord import app_commands
import os
import json
from datetime import timedelta

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

# --- 1. MODERATION COMMANDS ---

@bot.tree.command(name="kick", description="User ka saar server-ka")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = "Sabab lama sheegin"):
    await user.kick(reason=reason)
    await interaction.response.send_message(f"✅ **{user.name}** waa la kick-gareeyay. Sababta: {reason}")

@bot.tree.command(name="ban", description="User ka mamnuuc server-ka")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "Sabab lama sheegin"):
    await user.ban(reason=reason)
    await interaction.response.send_message(f"🚫 **{user.name}** waa la ban-gareeyay. Sababta: {reason}")

@bot.tree.command(name="timeout", description="User-ka aamusii (Mute)")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, user: discord.Member, minutes: int):
    if user.is_timed_out():
        return await interaction.response.send_message(f"⚠️ **{user.name}** horey ayuu ugu saarnaa timeout!", ephemeral=True)
    
    duration = timedelta(minutes=minutes)
    await user.timeout(duration)
    await interaction.response.send_message(f"⏳ **{user.name}** waxaa la saaray timeout muddo {minutes} daqiiqo ah.")

# --- 2. CHANNEL CONTROL ---

@bot.tree.command(name="slowmode", description="Channel-ka saar slowmode")
@app_commands.checks.has_permissions(manage_channels=True)
async def slowmode(interaction: discord.Interaction, channel: discord.TextChannel, seconds: int):
    if channel.slowmode_delay == seconds:
        return await interaction.response.send_message(f"⚠️ Channel-ka {channel.mention} horey ayuu u lahaa slowmode-kan.", ephemeral=True)
    
    await channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"⏲️ Slowmode-ka {channel.mention} waxaa laga dhigay {seconds} ilbiriqsi.")

@bot.tree.command(name="slowmodeoff", description="Ka qaad slowmode-ka")
@app_commands.checks.has_permissions(manage_channels=True)
async def slowmodeoff(interaction: discord.Interaction, channel: discord.TextChannel):
    if channel.slowmode_delay == 0:
        return await interaction.response.send_message(f"⚠️ Channel-ku ma laha wax slowmode ah.", ephemeral=True)
    
    await channel.edit(slowmode_delay=0)
    await interaction.response.send_message(f"✅ Slowmode-kii waa laga qaaday {channel.mention}.")

@bot.tree.command(name="lock", description="Xir channel-ka")
@app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction, channel: discord.TextChannel):
    overwrite = channel.overwrites_for(interaction.guild.default_role)
    if overwrite.send_messages is False:
        return await interaction.response.send_message(f"⚠️ Channel-ka {channel.mention} mar hore ayuu xirnaa!", ephemeral=True)
    
    overwrite.send_messages = False
    await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message(f"🔒 Channel-ka {channel.mention} waa la xiray.")

@bot.tree.command(name="unlock", description="Fur channel-ka")
@app_commands.checks.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction, channel: discord.TextChannel):
    overwrite = channel.overwrites_for(interaction.guild.default_role)
    if overwrite.send_messages is True or overwrite.send_messages is None:
        return await interaction.response.send_message(f"⚠️ Channel-ku ma xirna!", ephemeral=True)
    
    overwrite.send_messages = True
    await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message(f"🔓 Channel-ka {channel.mention} waa la furay.")

# --- 3. WELCOME SYSTEM ---

@bot.tree.command(name="setwelcome", description="Habee fariinta soo dhawaynta")
@app_commands.checks.has_permissions(administrator=True)
async def setwelcome(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
    data = load_welcome()
    data[str(interaction.guild.id)] = {"channel": channel.id, "message": message}
    save_welcome(data)
    await interaction.response.send_message(f"✅ Welcome-ka waxaa lagu daray {channel.mention}")

@bot.event
async def on_member_join(member):
    data = load_welcome()
    guild_data = data.get(str(member.guild.id))
    if guild_data:
        channel = bot.get_channel(guild_data["channel"])
        msg = guild_data["message"].replace("{user}", member.mention).replace("{server}", member.guild.name)
        if channel:
            await channel.send(msg)

# --- 4. LINKS & HELP ---

@bot.tree.command(name="invite", description="Casuun bot-ka")
async def invite(interaction: discord.Interaction):
    link = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands"
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Add Your Server 🌍", url=link))
    await interaction.response.send_message("Guji badanka si aad bot-ka u casuunto:", view=view)

@bot.tree.command(name="help", description="Sida bot-ka loo isticmaalo")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="Bot Help Menu 📖", color=discord.Color.blue())
    embed.description = "Isticmaal `/` si aad u aragto dhammaan amarrada.\n\n[GitHub Repo](https://github.com/shaaficidv/Nasro-.git)"
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="GitHub More.. 📂", url="https://github.com/shaaficidv/Nasro-.git"))
    await interaction.response.send_message(embed=embed, view=view)

bot.run(TOKEN)
  
