import discord
from discord.ext import commands
from discord import app_commands
import os
import psycopg2
from datetime import timedelta
from typing import Optional

# 1. TOKEN & DATABASE_URL (Ka soo qaad Secrets-ka Railway)
TOKEN = os.environ.get("DISCORD_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")

# --- DATABASE SETUP (Persistent Storage) ---
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS welcome 
                 (guild_id TEXT PRIMARY KEY, channel_id BIGINT, message TEXT)''')
    conn.commit()
    c.close()
    conn.close()

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

# --- EVENTS ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    if isinstance(message.channel, discord.DMChannel):
        embed = discord.Embed(
            title="S̶H̶A̶A̶F̶I̶C̶I̶ 🧞 Support ℹ️",
            description=f"Hi **{message.author.name}**, How are You?\nPlease use `/` I'm Working!",
            color=discord.Color.blue()
        )
        await message.channel.send(embed=embed)
        return
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT channel_id, message FROM welcome WHERE guild_id = %s', (str(member.guild.id),))
    data = c.fetchone()
    c.close()
    conn.close()
    if data:
        channel = bot.get_channel(data[0])
        if channel:
            msg = data[1].replace("{user}", member.mention).replace("{server}", member.guild.name)
            embed = discord.Embed(title="Welcome! 🎉", description=msg, color=discord.Color.green())
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)

# --- 12 SLASH COMMANDS (PRIVATE/EPHEMERAL) ---

# 1. Help (With GitHub & More Buttons)
@bot.tree.command(name="help", description="Liiska amarrada bot-ka")
async def help_cmd(interaction: discord.Interaction):
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="GitHub 📂", url="https://github.com/shaaficidv/Nasro-.git", style=discord.ButtonStyle.link))
    view.add_item(discord.ui.Button(label="More... ✨", url="https://github.com/shaaficidv/Nasro-.git", style=discord.ButtonStyle.link))
    
    help_text = "📜 **Shaafici Bot Menu**\nModeration: `/kick`, `/ban`, `/timeout`, `/clean` \nControl: `/lock`, `/unlock`, `/slowmode`, `/slowmodeoff` \nTools: `/setwelcome`, `/msg`, `/add`, `/help`"
    await interaction.response.send_message(help_text, view=view, ephemeral=True)

# 2. Add (With Invite Button)
@bot.tree.command(name="add", description="Ku dar bot-ka server-kaaga")
async def add(interaction: discord.Interaction):
    url = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands"
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Add Bot +", url=url, style=discord.ButtonStyle.link))
    await interaction.response.send_message("Guji badanka hoose:", view=view, ephemeral=True)

# 3. Clean
@bot.tree.command(name="clean", description="Nadiifi fariimaha")
async def clean(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("❌ **Admin Kaliya!**", ephemeral=True)
    await interaction.response.defer(ephemeral=True)
    await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"✅ Waxaa la tirtiray {amount} fariimood.", ephemeral=True)

# 4. Setwelcome
@bot.tree.command(name="setwelcome", description="Keydi welcome message")
async def setwelcome(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ **Admin Kaliya!**", ephemeral=True)
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO welcome (guild_id, channel_id, message) VALUES (%s, %s, %s) ON CONFLICT (guild_id) DO UPDATE SET channel_id = EXCLUDED.channel_id, message = EXCLUDED.message', (str(interaction.guild.id), channel.id, message))
    conn.commit()
    c.close()
    conn.close()
    await interaction.response.send_message(f"✅ Xogta waa lagu keydiyey Database-ka!", ephemeral=True)

# 5. Kick
@bot.tree.command(name="kick", description="User saar")
async def kick(interaction: discord.Interaction, user: discord.Member):
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ Admin Kaliya!", ephemeral=True)
    await user.kick()
    await interaction.response.send_message(f"✅ {user.name} waa la saaray.", ephemeral=True)

# 6. Ban
@bot.tree.command(name="ban", description="User mamnuuc")
async def ban(interaction: discord.Interaction, user: discord.Member):
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ Admin Kaliya!", ephemeral=True)
    await user.ban()
    await interaction.response.send_message(f"🚫 {user.name} waa la ban-gareeyay.", ephemeral=True)

# 7. Timeout
@bot.tree.command(name="timeout", description="User-ka aamusii")
async def timeout(interaction: discord.Interaction, user: discord.Member, minutes: int):
    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message("❌ Admin Kaliya!", ephemeral=True)
    await user.timeout(timedelta(minutes=minutes))
    await interaction.response.send_message(f"⏳ {user.name} aamusan {minutes} min.", ephemeral=True)

# 8. Lock
@bot.tree.command(name="lock", description="Xir channel")
async def lock(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ Admin Kaliya!", ephemeral=True)
    await channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message(f"🔒 {channel.mention} waa la xiray.", ephemeral=True)

# 9. Unlock
@bot.tree.command(name="unlock", description="Fur channel")
async def unlock(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ Admin Kaliya!", ephemeral=True)
    await channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message(f"🔓 {channel.mention} waa la furay.", ephemeral=True)

# 10. Msg
@bot.tree.command(name="msg", description="Embed message dir")
async def msg(interaction: discord.Interaction, message: str, channel: Optional[discord.TextChannel] = None):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Admin Kaliya!", ephemeral=True)
    target = channel or interaction.channel
    embed = discord.Embed(description=message, color=discord.Color.blue())
    await target.send(embed=embed)
    await interaction.response.send_message("✅ Diris waa la sameeyey.", ephemeral=True)

# 11. Slowmode
@bot.tree.command(name="slowmode", description="Set slowmode")
async def slowmode(interaction: discord.Interaction, seconds: int):
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ Admin Kaliya!", ephemeral=True)
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"⏲️ Slowmode: {seconds}s", ephemeral=True)

# 12. Slowmodeoff
@bot.tree.command(name="slowmodeoff", description="Ka qaad slowmode")
async def slowmodeoff(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ Admin Kaliya!", ephemeral=True)
    await interaction.channel.edit(slowmode_delay=0)
    await interaction.response.send_message("✅ Slowmode off.", ephemeral=True)

bot.run(TOKEN)
