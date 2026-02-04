import discord
from discord.ext import commands
from discord import app_commands
import os, json
from datetime import timedelta
from typing import Optional

TOKEN = os.environ.get("DISCORD_TOKEN")
DATA_FILE = "data.json"

# =========================
# DATA PERSISTENCE
# =========================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"guilds": {}}
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {"guilds": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# =========================
# BOT SETUP
# =========================
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# =========================
# HELPER: LOG COMMAND
# =========================
def log_command(guild_id, user_id, cmd):
    g = data["guilds"].setdefault(str(guild_id), {"users": {}, "settings": {}})
    u = g["users"].setdefault(str(user_id), {"commands": {}, "dm_sent": 0})
    u["commands"][cmd] = u["commands"].get(cmd, 0) + 1
    save_data(data)

# =========================
# 1️⃣ /msg (DM KALIYA)
# =========================
@bot.tree.command(name="msg", description="Send DM to user")
async def msg(interaction: discord.Interaction, user: discord.Member):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Admin kaliya", ephemeral=True)

    log_command(interaction.guild.id, interaction.user.id, "msg")

    try:
        await user.send(f"👋 Hi **{user.name}**, use this `/` !")

        g = data["guilds"][str(interaction.guild.id)]
        u = g["users"].setdefault(str(user.id), {"commands": {}, "dm_sent": 0})
        u["dm_sent"] += 1
        save_data(data)

        await interaction.response.send_message(
            f"✅ DM ayaa loo diray {user.mention}", ephemeral=True
        )
    except:
        await interaction.response.send_message("❌ DM-ga user-ka waa xiran", ephemeral=True)

# =========================
# 2️⃣ /clean
# =========================
@bot.tree.command(name="clean")
async def clean(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("❌ Admin kaliya", ephemeral=True)

    log_command(interaction.guild.id, interaction.user.id, "clean")
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(
        f"✅ {len(deleted)} fariimood waa la tirtiray", ephemeral=True
    )

# =========================
# 3️⃣ /kick
# =========================
@bot.tree.command(name="kick")
async def kick(interaction: discord.Interaction, user: discord.Member):
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ Admin kaliya", ephemeral=True)

    log_command(interaction.guild.id, interaction.user.id, "kick")
    await user.kick()
    await interaction.response.send_message("✅ User kicked", ephemeral=True)

# =========================
# 4️⃣ /ban
# =========================
@bot.tree.command(name="ban")
async def ban(interaction: discord.Interaction, user: discord.Member):
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ Admin kaliya", ephemeral=True)

    log_command(interaction.guild.id, interaction.user.id, "ban")
    await user.ban()
    await interaction.response.send_message("🚫 User banned", ephemeral=True)

# =========================
# 5️⃣ /lock
# =========================
@bot.tree.command(name="lock")
async def lock(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ Admin kaliya", ephemeral=True)

    log_command(interaction.guild.id, interaction.user.id, "lock")
    await channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 Channel locked", ephemeral=True)

# =========================
# 6️⃣ /unlock
# =========================
@bot.tree.command(name="unlock")
async def unlock(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ Admin kaliya", ephemeral=True)

    log_command(interaction.guild.id, interaction.user.id, "unlock")
    await channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("🔓 Channel unlocked", ephemeral=True)

# =========================
# 7️⃣ /timeout
# =========================
@bot.tree.command(name="timeout")
async def timeout(interaction: discord.Interaction, user: discord.Member, minutes: int):
    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message("❌ Admin kaliya", ephemeral=True)

    log_command(interaction.guild.id, interaction.user.id, "timeout")
    await user.timeout(timedelta(minutes=minutes))
    await interaction.response.send_message("⏳ Timeout set", ephemeral=True)

# =========================
# 8️⃣ /slowmode
# =========================
@bot.tree.command(name="slowmode")
async def slowmode(interaction: discord.Interaction, seconds: int):
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ Admin kaliya", ephemeral=True)

    log_command(interaction.guild.id, interaction.user.id, "slowmode")
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message("⏲️ Slowmode set", ephemeral=True)

# =========================
# 9️⃣ /slowmodeoff
# =========================
@bot.tree.command(name="slowmodeoff")
async def slowmodeoff(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("❌ Admin kaliya", ephemeral=True)

    log_command(interaction.guild.id, interaction.user.id, "slowmodeoff")
    await interaction.channel.edit(slowmode_delay=0)
    await interaction.response.send_message("✅ Slowmode off", ephemeral=True)

# =========================
# 🔟 /setwelcome (PERSISTENT)
# =========================
@bot.tree.command(name="setwelcome")
async def setwelcome(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Admin kaliya", ephemeral=True)

    g = data["guilds"].setdefault(str(interaction.guild.id), {"users": {}, "settings": {}})
    g["settings"]["welcome"] = {
        "channel": channel.id,
        "message": message
    }
    save_data(data)

    await interaction.response.send_message(
        f"✅ Welcome lagu dhigay {channel.mention}", ephemeral=True
    )

# =========================
# 1️⃣1️⃣ /invite
# =========================
@bot.tree.command(name="invite")
async def invite(interaction: discord.Interaction):
    url = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands"
    await interaction.response.send_message(url, ephemeral=True)

# =========================
# 1️⃣2️⃣ /help
# =========================
@bot.tree.command(name="help")
async def help_cmd(interaction: discord.Interaction):
    await interaction.response.send_message(
        "📜 Isticmaal `/` si aad u aragto dhammaan amarada bot-ka",
        ephemeral=True
    )

# =========================
# WELCOME EVENT
# =========================
@bot.event
async def on_member_join(member):
    g = data["guilds"].get(str(member.guild.id))
    if not g:
        return

    welcome = g.get("settings", {}).get("welcome")
    if not welcome:
        return

    channel = member.guild.get_channel(welcome["channel"])
    if not channel:
        return

    msg = welcome["message"] \
        .replace("{user}", member.mention) \
        .replace("{server}", member.guild.name)

    embed = discord.Embed(
        title="🎉 Welcome!",
        description=msg,
        color=discord.Color.green()
    )

    await channel.send(embed=embed)

bot.run(TOKEN)
