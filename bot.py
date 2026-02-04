import discord
from discord.ext import commands
from discord import app_commands
import os
import sqlite3
from datetime import timedelta
from typing import Optional

# Token-ka waxaa laga akhrinayaa Secrets-ka Kinesis/Cloud
TOKEN = os.environ.get("DISCORD_TOKEN")

# --- 1. DATABASE LOGIC (SQLite) ---
def init_db():
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS welcome 
                 (guild_id TEXT PRIMARY KEY, channel_id INTEGER, message TEXT)''')
    conn.commit()
    conn.close()

def save_welcome_db(guild_id, channel_id, message):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO welcome (guild_id, channel_id, message) VALUES (?, ?, ?)', 
              (str(guild_id), channel_id, message))
    conn.commit()
    conn.close()

def load_welcome_db(guild_id):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('SELECT channel_id, message FROM welcome WHERE guild_id = ?', (str(guild_id),))
    data = c.fetchone()
    conn.close()
    return data

# Bilow Database-ka
init_db()

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

# --- 2. EVENTS (DM & DOUBLE MSG FIX) ---

@bot.event
async def on_message(message):
    # JOOJI: In bot-ku uu isagu isu jawaabo (Xalka Double Message)
    if message.author.bot:
        return

    # DM Auto-Response
    if isinstance(message.channel, discord.DMChannel):
        embed = discord.Embed(
            title="S̶H̶A̶A̶F̶I̶C̶I̶ 🧞 Support ℹ️",
            description=f"Hi **{message.author.name}**, How are You Today?\n\nPlease use `/` I'm Working!",
            color=discord.Color.blue()
        )
        view = discord.ui.View()
        invite_url = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands"
        view.add_item(discord.ui.Button(label="Add +", url=invite_url))
        view.add_item(discord.ui.Button(label="Content Team", url="https://discord.com/users/1388255325345419409"))
        
        await message.channel.send(embed=embed, view=view)
        return

    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    data = load_welcome_db(member.guild.id)
    if data:
        channel_id, msg_content = data
        channel = bot.get_channel(channel_id)
        if channel:
            final_msg = msg_content.replace("{user}", member.mention).replace("{server}", member.guild.name)
            embed = discord.Embed(title="Welcome! 🎉", description=final_msg, color=discord.Color.green())
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)

# --- 3. SLASH COMMANDS (12 COMMANDS) ---

# 1. Clean
@bot.tree.command(name="clean", description="Tirtir fariimaha channel-ka")
async def clean(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"✅ Waxaa la tirtiray {len(deleted)} fariimood.", ephemeral=True)

# 2. Msg
@bot.tree.command(name="msg", description="Fariin Embed ah u dir Channel ama User")
async def msg(interaction: discord.Interaction, message: str, channel: Optional[discord.TextChannel] = None, user: Optional[discord.Member] = None):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    embed = discord.Embed(description=message, color=discord.Color.blue())
    if channel: await channel.send(embed=embed)
    elif user: await interaction.channel.send(content=f"{user.mention}", embed=embed)
    await interaction.response.send_message("✅ Fariinta waa la diray.", ephemeral=True)

# 3. Kick
@bot.tree.command(name="kick", description="User-ka saar server-ka")
async def kick(interaction: discord.Interaction, user: discord.Member):
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    await user.kick()
    await interaction.response.send_message(f"✅ {user.name} waa la saaray.", ephemeral=True)

# 4. Ban
@bot.tree.command(name="ban", description="User-ka mamnuuc")
async def ban(interaction: discord.Interaction, user: discord.Member):
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    await user.ban()
    await interaction.response.send_message(f"🚫 {user.name} waa la mamnuucay.", ephemeral=True)

# 5. Timeout
@bot.tree.command(name="timeout", description="User-ka aamusii")
async def timeout(interaction: discord.Interaction, user: discord.Member, minutes: int):
    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    await user.timeout(timedelta(minutes=minutes))
    await interaction.response.send_message(f"⏳ {user.name} waa la aamusiiyey {minutes} min.", ephemeral=True)

# 6. Lock
@bot.tree.command(name="lock", description="Xir channel-ka")
async def lock(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    await channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message(f"🔒 {channel.mention} waa la xiray.", ephemeral=True)

# 7. Unlock
@bot.tree.command(name="unlock", description="Fur channel-ka")
async def unlock(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    await channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message(f"🔓 {channel.mention} waa la furay.", ephemeral=True)

# 8. Slowmode
@bot.tree.command(name="slowmode", description="Saar slowmode")
async def slowmode(interaction: discord.Interaction, seconds: int):
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"⏲️ Slowmode: {seconds}s", ephemeral=True)

# 9. Slowmodeoff
@bot.tree.command(name="slowmodeoff", description="Ka qaad slowmode")
async def slowmodeoff(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    await interaction.channel.edit(slowmode_delay=0)
    await interaction.response.send_message("✅ Slowmode waa laga qaaday.", ephemeral=True)

# 10. Setwelcome
@bot.tree.command(name="setwelcome", description="Setup welcome message")
async def setwelcome(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ **Fadlan @administrator Kaliya Aya I Mamuli Karo Mahdsanid ℹ️**", ephemeral=True)
    save_welcome_db(interaction.guild.id, channel.id, message)
    await interaction.response.send_message(f"✅ Welcome lagu keydiyey {channel.mention}", ephemeral=True)

# 11. Invite
@bot.tree.command(name="invite", description="Casuun bot-ka")
async def invite(interaction: discord.Interaction):
    url = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands"
    await interaction.response.send_message(f"🌍 Add Bot: {url}", ephemeral=True)

# 12. Help
@bot.tree.command(name="help", description="Help menu")
async def help_cmd(interaction: discord.Interaction):
    msg = "📜 **Bot Commands:** /clean, /msg, /kick, /ban, /timeout, /lock, /unlock, /slowmode, /slowmodeoff, /setwelcome, /invite, /help"
    await interaction.response.send_message(msg, ephemeral=True)

bot.run(TOKEN)
    
