import discord
from discord.ext import commands
from discord import app_commands
import os
import json
from datetime import timedelta
from typing import Optional

TOKEN = os.environ.get("DISCORD_TOKEN")
WELCOME_FILE = "welcome_settings.json"

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

# --- 1. XALKA DOUBLE MESSAGE (MUHIIM) ---
@bot.event
async def on_message(message):
    # HADDII FARINTU BOT KA TIMAAD ISKA INDHO-TIR (XALKA LOOP-KA)
    if message.author.bot:
        return

    # DM Response
    if isinstance(message.channel, discord.DMChannel):
        embed = discord.Embed(
            title="Nagti Shaafici Support ℹ️",
            description=f"Hi **{message.author.name}**, How are You Today?\n\nPlease use `/` I'm Working!",
            color=discord.Color.blue()
        )
        view = discord.ui.View()
        invite_url = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands"
        view.add_item(discord.ui.Button(label="Add +", url=invite_url))
        view.add_item(discord.ui.Button(label="Content Team", url="https://discord.com/users/1388255325345419409"))
        
        await message.channel.send(embed=embed, view=view)
        return # Halkan ku jooji DM-ka

    await bot.process_commands(message)

# --- 2. CLEAN COMMAND (AMARKA 11-AAD) ---
@bot.tree.command(name="clean", description="Tirtir fariimaha")
async def clean(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"✅ Waxaa la tirtiray {len(deleted)} fariimood.", ephemeral=True)

# --- 3. MSG COMMAND (AMARKA 12-AAD) ---
@bot.tree.command(name="msg", description="Fariin Embed ah")
async def msg(interaction: discord.Interaction, message: str, channel: Optional[discord.TextChannel] = None, user: Optional[discord.Member] = None):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)

    embed = discord.Embed(description=message, color=discord.Color.blue())
    if channel:
        await channel.send(embed=embed)
    elif user:
        await interaction.channel.send(content=f"{user.mention}", embed=embed)
    await interaction.response.send_message("✅ Fariinta waa la diray.", ephemeral=True)

# --- MODERATION & OTHERS ---
@bot.tree.command(name="kick")
async def kick(interaction: discord.Interaction, user: discord.Member):
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    await user.kick()
    await interaction.response.send_message(f"✅ {user.name} waa la saaray.", ephemeral=True)

@bot.tree.command(name="ban")
async def ban(interaction: discord.Interaction, user: discord.Member):
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    await user.ban()
    await interaction.response.send_message(f"🚫 {user.name} waa la ban-gareeyay.", ephemeral=True)

@bot.tree.command(name="lock")
async def lock(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    await channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message(f"🔒 {channel.mention} waa la xiray.", ephemeral=True)

@bot.tree.command(name="unlock")
async def unlock(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    await channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message(f"🔓 {channel.mention} waa la furay.", ephemeral=True)

@bot.tree.command(name="timeout")
async def timeout(interaction: discord.Interaction, user: discord.Member, minutes: int):
    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    await user.timeout(timedelta(minutes=minutes))
    await interaction.response.send_message(f"⏳ {user.name} timeout {minutes} min.", ephemeral=True)

@bot.tree.command(name="slowmode")
async def slowmode(interaction: discord.Interaction, seconds: int):
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"⏲️ Slowmode set: {seconds}s", ephemeral=True)

@bot.tree.command(name="slowmodeoff")
async def slowmodeoff(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    await interaction.channel.edit(slowmode_delay=0)
    await interaction.response.send_message("✅ Slowmode off.", ephemeral=True)

@bot.tree.command(name="setwelcome")
async def setwelcome(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    data = load_welcome()
    data[str(interaction.guild.id)] = {"channel": channel.id, "message": message}
    save_welcome(data)
    await interaction.response.send_message(f"✅ Welcome lagu dhigay {channel.mention}", ephemeral=True)

@bot.tree.command(name="invite")
async def invite(interaction: discord.Interaction):
    url = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands"
    await interaction.response.send_message(f"🌍 Casuun bot-ka: {url}", ephemeral=True)

@bot.tree.command(name="help")
async def help_cmd(interaction: discord.Interaction):
    await interaction.response.send_message("📜 Isticmaal `/` si aad u aragto 12-ka amar ee bot-ka.", ephemeral=True)

@bot.event
async def on_member_join(member):
    data = load_welcome()
    g_data = data.get(str(member.guild.id))
    if g_data:
        channel = bot.get_channel(g_data["channel"])
        if channel:
            msg_content = g_data["message"].replace("{user}", member.mention).replace("{server}", member.guild.name)
            embed = discord.Embed(title="Welcome! 🎉", description=msg_content, color=discord.Color.green())
            await channel.send(embed=embed)

bot.run(TOKEN)
