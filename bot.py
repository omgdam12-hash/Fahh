import discord
from discord.ext import commands
import random
import json
import os
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Admin user ID
ADMIN_ID = 1018004252930605057

# Data storage
data = {
    'enabled_servers': [],
    'cooldowns': {},
    'stock_available': True
}

def load_data():
    global data
    if os.path.exists('data.json'):
        with open('data.json', 'r') as f:
            data = json.load(f)

def save_data():
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

load_data()

def generate_card():
    card_number = ''.join([str(random.randint(0, 9)) for _ in range(16)])
    formatted_number = ' '.join([card_number[i:i+4] for i in range(0, 16, 4)])
    month = str(random.randint(1, 12)).zfill(2)
    year = str(random.randint(2026, 2032))
    cvc = ''.join([str(random.randint(0, 9)) for _ in range(3)])
    return {
        'number': formatted_number,
        'month': month,
        'year': year,
        'cvc': cvc
    }

@bot.event
async def on_ready():
    print(f'✅ {bot.user} has connected to Discord!')
    print(f'📊 Bot is in {len(bot.guilds)} servers')
    print(f'📦 Stock Status: {"Available" if data["stock_available"] else "Out of Stock"}')
    print('-' * 50)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if isinstance(message.channel, discord.DMChannel):
        await handle_dm(message)
        return
    
    if not message.content.startswith('!'):
        return
    
    await bot.process_commands(message)

async def handle_dm(message):
    content = message.content.lower()
    
    if message.author.id != ADMIN_ID:
        await message.channel.send("❌ You don't have permission to use commands in DMs!")
        return
    
    if content == '!outofstock':
        data['stock_available'] = False
        save_data()
        embed = discord.Embed(
            title="📦 **Stock Updated**",
            description="❌ Stock is now **Out of Stock**!",
            color=0xFF0000
        )
        embed.set_footer(text="Made by DevilClouds")
        await message.channel.send(embed=embed)
    
    elif content == '!instock':
        data['stock_available'] = True
        save_data()
        embed = discord.Embed(
            title="📦 **Stock Updated**",
            description="✅ Stock is now **Available**!",
            color=0x00FF00
        )
        embed.set_footer(text="Made by DevilClouds")
        await message.channel.send(embed=embed)
    
    elif content == '!stockstatus':
        status = "✅ Available" if data['stock_available'] else "❌ Out of Stock"
        embed = discord.Embed(
            title="📦 **Stock Status**",
            description=f"Current stock: **{status}**",
            color=0x3498db
        )
        embed.set_footer(text="Made by DevilClouds")
        await message.channel.send(embed=embed)
    
    else:
        await message.channel.send("❌ Unknown command! Available: `!outofstock`, `!instock`, `!stockstatus`")

@bot.command(name='activech')
@commands.has_permissions(administrator=True)
async def active_channel(ctx):
    if ctx.author.id != ADMIN_ID:
        await ctx.send("❌ You don't have permission!")
        return
    
    server_id = str(ctx.guild.id)
    if server_id not in data['enabled_servers']:
        data['enabled_servers'].append(server_id)
        save_data()
        await ctx.send(f"✅ CC generation **enabled** in this server!")
    else:
        await ctx.send(f"ℹ️ CC generation already enabled!")

@bot.command(name='deactivech')
@commands.has_permissions(administrator=True)
async def deactive_channel(ctx):
    if ctx.author.id != ADMIN_ID:
        await ctx.send("❌ You don't have permission!")
        return
    
    server_id = str(ctx.guild.id)
    if server_id in data['enabled_servers']:
        data['enabled_servers'].remove(server_id)
        save_data()
        await ctx.send(f"❌ CC generation **disabled** in this server!")
    else:
        await ctx.send(f"ℹ️ CC generation already disabled!")

@bot.command(name='cc')
async def generate_cc(ctx):
    if not data['stock_available']:
        embed = discord.Embed(
            title="📦 **DevilClouds**",
            description="❌ **Out of Stock!**\nNo cards available right now. Please try again later.",
            color=0xFF0000
        )
        embed.set_footer(text="Made by DevilClouds")
        await ctx.send(embed=embed)
        return
    
    server_id = str(ctx.guild.id)
    if server_id not in data['enabled_servers']:
        await ctx.send("❌ CC generation is not enabled in this server!")
        return
    
    user_id = str(ctx.author.id)
    current_time = datetime.now()
    
    if user_id in data['cooldowns']:
        last_used = datetime.fromisoformat(data['cooldowns'][user_id])
        time_diff = (current_time - last_used).total_seconds()
        if time_diff < 30:
            remaining = 30 - int(time_diff)
            await ctx.send(f"⚠️ Cooldown! Wait {remaining}s")
            return
    
    card = generate_card()
    embed = discord.Embed(
        title="💳 **DevilClouds**",
        description="**Here is your card!**",
        color=0x00ff00
    )
    embed.add_field(name="**Number**", value=f"`{card['number']}`", inline=False)
    embed.add_field(name="**Month**", value=f"`{card['month']}`", inline=True)
    embed.add_field(name="**Year**", value=f"`{card['year']}`", inline=True)
    embed.add_field(name="**CVC**", value=f"`{card['cvc']}`", inline=True)
    embed.set_footer(text="Made by DevilClouds")
    
    try:
        await ctx.author.send(embed=embed)
        await ctx.send(f"✅ Card sent to your DMs! <@{ctx.author.id}>")
        data['cooldowns'][user_id] = current_time.isoformat()
        save_data()
    except discord.Forbidden:
        await ctx.send("❌ Can't send DM! Please enable DMs.")

@bot.command(name='vps')
async def check_vps(ctx):
    status = "✅ Available" if data['stock_available'] else "❌ Out of Stock"
    embed = discord.Embed(
        title="✅ **DevilClouds** is online!",
        description=f"📦 Stock: **{status}**",
        color=0x00ff00
    )
    embed.set_footer(text="Made by DevilClouds")
    await ctx.send(embed=embed)

@bot.command(name='helpcc')
async def help_command(ctx):
    embed = discord.Embed(
        title="📋 **DevilClouds Commands**",
        color=0x3498db
    )
    embed.add_field(
        name="**User Commands**",
        value="`!cc` - Generate card\n`!vps` - Bot status\n`!helpcc` - This menu",
        inline=False
    )
    embed.add_field(
        name="**Admin Commands** (Server)",
        value="`!activech` - Enable server\n`!deactivech` - Disable server",
        inline=False
    )
    embed.add_field(
        name="**Admin Commands** (DM Only)",
        value="`!outofstock` - Set Out of Stock\n`!instock` - Set Available\n`!stockstatus` - Check stock",
        inline=False
    )
    embed.set_footer(text="Made by DevilClouds")
    await ctx.send(embed=embed)

if __name__ == "__main__":
    # Replace with your token or use environment variable
    TOKEN = os.getenv('DISCORD_TOKEN', 'YOUR_BOT_TOKEN_HERE')
    bot.run(TOKEN)
