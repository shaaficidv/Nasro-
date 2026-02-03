import discord
from discord.ext import commands
from discord import app_commands
import os
import json
from datetime import timedelta
from typing import Optional

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

# --- 1. THE /MSG COMMAND (ADMIN ONLY) ---
@bot.tree.command(name="msg", description="Fariin Embed ah u dir Channel ama User")
@app_commands.describe(channel="Channel-ka fariinta lagu dirayo", user="User-ka la mention-gareeyo", message="Fariintaada")
async def msg(interaction: discord.Interaction, message: str, channel: Optional[discord.TextChannel] = None, user: Optional[discord.Member] = None):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)

    embed = discord.Embed(description=message, color=discord.Color.blue())
    
    if channel:
        await channel.send(embed=embed)
        await interaction.response.send_message(f"✅ Fariintaada waxaa lagu diray {channel.mention}", ephemeral=True)
    elif user:
        await interaction.channel.send(content=f"{user.mention}", embed=embed)
        await interaction.response.send_message(f"✅ Fariintaada waxaa loo tag-gareeyay {user.name}", ephemeral=True)
    else:
        await interaction.response.send_message("Fadlan dooro Channel ama User midkood!", ephemeral=True)

# --- 2. MODERATION COMMANDS ---

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

@bot.tree.command(name="timeout", description="User-ka aamusii")
async def timeout(interaction: discord.Interaction, user: discord.Member, minutes: int):
    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    await user.timeout(timedelta(minutes=minutes))
    await interaction.response.send_message(f"⏳ **{user.name}** timeout {minutes} min.", ephemeral=True)

# --- 3. CHANNEL CONTROL ---

@bot.tree.command(name="lock", description="Xir channel-ka")
async def lock(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    overwrite = channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = False
    await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message(f"🔒 {channel.mention} waa la xiray.", ephemeral=True)

@bot.tree.command(name="unlock", description="Fur channel-ka")
async def unlock(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    overwrite = channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = True
    await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message(f"🔓 {channel.mention} waa la furay.", ephemeral=True)

@bot.tree.command(name="slowmode", description="Saar slowmode")
async def slowmode(interaction: discord.Interaction, seconds: int):
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"⏲️ Slowmode: {seconds}s", ephemeral=True)

@bot.tree.command(name="slowmodeoff", description="Ka qaad slowmode")
async def slowmodeoff(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ **Fadlan @administor Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    await interaction.channel.edit(slowmode_delay=0)
    await interaction.response.send_message("✅ Slowmode off.", ephemeral=True)

# --- 4. WELCOME & EVENTS ---

@bot.event
async def on_member_join(member):
    data = load_welcome()
    g_data = data.get(str(member.guild.id))
    if g_data:
        channel = bot.get_channel(g_data["channel"])
        if channel:
            msg_content = g_data["message"].replace("{user}", member.mention).replace("{server}", member.guild.name)
            embed = discord.Embed(title="Welcome! 🎉", description=msg_content, color=discord.Color.green())
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)

@bot.tree.command(name="setwelcome", description="Habee welcome embed ah")
async def setwelcome(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ **Fadlan @administor Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    data = load_welcome()
    data[str(interaction.guild.id)] = {"channel": channel.id, "message": message}
    save_welcome(data)
    await interaction.response.send_message(f"✅ Welcome Embed-ka waa la dhigay {channel.mention}", ephemeral=True)

# --- 5. HELP & UTILITY ---

@bot.tree.command(name="invite", description="Casuun bot-ka")
async def invite(interaction: discord.Interaction):
    url = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands"
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Add Server 🌍", url=url))
    await interaction.response.send_message("Guji badanka hoose:", view=view, ephemeral=True)

@bot.tree.command(name="help", description="Help menu")
async def help_cmd(interaction: discord.Interaction):
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="GitHub 📂", url="https://github.com/shaaficidv/Nasro-.git"))
    await interaction.response.send_message("comatis /help menu /setwelcom Set up Bot /kick kick User /lock Lock Chnala /unlock Unlock Chnala / Msg Send Meseeg User or Chnala /slowmode Set slowmode /Slowmodeoff Off slowmode  /timeout user timeout /invite add Bot Your Sever /ban Ban User one Sever isticmala Ruleka @ administor Si aan Kugu shaqeyo ? 🇸🇴.", view=view, ephemeral=True)

bot.run(TOKEN)
