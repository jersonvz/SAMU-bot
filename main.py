
import os
import json
from datetime import datetime
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

ARCHIVO = "horas.json"

def cargar():
    try:
        with open(ARCHIVO, "r") as f:
            return json.load(f)
    except:
        return {}

def guardar(datos):
    with open(ARCHIVO, "w") as f:
        json.dump(datos, f, indent=4)

def tiempo(segundos):
    h = int(segundos // 3600)
    m = int((segundos % 3600) // 60)
    return f"{h}h {m}m"

class PanelServicio(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🟢 Entrada de Servicio", style=discord.ButtonStyle.success, custom_id="entrada")
    async def entrada(self, interaction: discord.Interaction, button: discord.ui.Button):
        datos = cargar()
        uid = str(interaction.user.id)
        if uid in datos and datos[uid].get("entrada"):
            await interaction.response.send_message("Ya estás en servicio. Primero dale Salida.", ephemeral=True)
            return
        datos[uid] = {"nombre": interaction.user.display_name, "entrada": datetime.now().isoformat(), "total_segundos": datos.get(uid, {}).get("total_segundos", 0)}
        guardar(datos)
        await interaction.response.send_message(f"✅ {interaction.user.mention} Entrada registrada.", ephemeral=True)

    @discord.ui.button(label="🔴 Salida de Servicio", style=discord.ButtonStyle.danger, custom_id="salida")
    async def salida(self, interaction: discord.Interaction, button: discord.ui.Button):
        datos = cargar()
        uid = str(interaction.user.id)
        if uid not in datos or not datos[uid].get("entrada"):
            await interaction.response.send_message("No tienes servicio iniciado. Dale primero Entrada.", ephemeral=True)
            return
        entrada = datetime.fromisoformat(datos[uid]["entrada"])
        segundos = (datetime.now() - entrada).total_seconds()
        datos[uid]["total_segundos"] = datos[uid].get("total_segundos", 0) + segundos
        datos[uid]["entrada"] = None
        guardar(datos)
        await interaction.response.send_message(f"✅ {interaction.user.mention} Salida registrada. Este turno: {tiempo(segundos)}", ephemeral=True)

    @discord.ui.button(label="📊 Mis Horas Acumuladas", style=discord.ButtonStyle.primary, custom_id="horas")
    async def horas(self, interaction: discord.Interaction, button: discord.ui.Button):
        datos = cargar()
        uid = str(interaction.user.id)
        total = datos.get(uid, {}).get("total_segundos", 0)
        await interaction.response.send_message(f"⏱️ {interaction.user.mention} tienes acumulado: {tiempo(total)}", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Se sincronizaron {len(synced)} comandos slash")
    except Exception as e:
        print(f"Error al sincronizar: {e}")

@bot.tree.command(name="panel", description="Manda el panel de servicio de SAMU")
async def panel(interaction: discord.Interaction):
    embed = discord.Embed(title="🚑 SAMU - CONTROL DE SERVICIO", description="Bienvenido a SAMU, usa los botones abajo.", color=0xFF0000)
    await interaction.response.send_message(embed=embed, view=PanelServicio())

@bot.tree.command(name="ping", description="Mira si el bot está vivo")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! Latencia: {round(bot.latency * 1000)}ms")

@bot.command()
async def hola(ctx):
    await ctx.send(f"Hola {ctx.author.mention}")
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
return "SAMU bot vivo"

threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))).start()

bot.run(TOKEN)


