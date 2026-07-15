import os
import yt_dlp
import asyncio
import logging
import random
import requests
import time
import tempfile
import shutil
import re
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters, ConversationHandler

# ============ CONFIGURACIÓN ============
TOKEN = "8546862851:AAE25jmlZ2dskHBDRO9UcOz2F41K8lPXJ2U" # Cambia esto
OWNER_NUMBER = "929 207 065"
MAX_SIZE = 50 * 1024 * 1024 # 50MB
START_TIME = time.time()

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

usuarios_verificados = set()
categorias_disponibles = ["random", "waifu", "hentai", "neko", "blowjob","trap", "femdom", "boobs", "hentai_api", "anal", "cum", "pussy"]
search_results = {}
HABLANDO = 1

# ============ OPCIONES YT-DLP ============
YDL_OPTS_AUDIO = {
    'format': 'bestaudio/best',
    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
    'quiet': True,
    'noplaylist': True,
    'nocheckcertificate': True,
}

YDL_OPTS_VIDEO = {
    'format': 'best[ext=mp4][filesize<50M]/best[ext=mp4]/best',
    'quiet': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    # TikTok sin marca de agua viene por defecto
}

URL_REGEX = re.compile(r'https?://\S+')

# ============ FUNCIONES AUXILIARES ============
async def mostrar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔞 Verificar Edad", callback_data="menu_verify")],
        [InlineKeyboardButton("🎲 NSFW Random", callback_data="menu_nsfw_random")],
        [InlineKeyboardButton("📂 Ver Categorías", callback_data="menu_categorias")],
        [InlineKeyboardButton("⬇️ Descargas", callback_data="menu_descargas")],
        [InlineKeyboardButton("❓ Ayuda", callback_data="menu_help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    texto = "👋 **Menú de Comandos**\n\nElige una opción:"
    if update.callback_query: await update.callback_query.edit_message_text(texto, reply_markup=reply_markup, parse_mode='Markdown')
    else: await update.message.reply_text(texto, reply_markup=reply_markup, parse_mode='Markdown')

async def verificar_edad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    if user_id not in usuarios_verificados:
        keyboard = [[InlineKeyboardButton("✅ Soy mayor de 18", callback_data="verify_yes")],[InlineKeyboardButton("❌ No soy mayor", callback_data="verify_no")],[InlineKeyboardButton("⬅️ Volver al menú", callback_data="back_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        msg = "🔞 Este bot contiene contenido NSFW.\nDebes confirmar que eres mayor de 18 años para continuar."
        if update.message: await update.message.reply_text(msg, reply_markup=reply_markup)
        elif update.callback_query: await update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
        return False
    return True

def obtener_imagen_nsfw(categoria: str = "random"):
    apis = {"random": "https://api.waifu.im/search/?is_nsfw=true","waifu": "https://api.waifu.im/search/?is_nsfw=true&included_tags=waifu","hentai": "https://api.waifu.im/search/?is_nsfw=true&included_tags=hentai","neko": "https://nekos.life/api/v2/img/lewd","blowjob": "https://nekos.life/api/v2/img/blowjob","trap": "https://nekos.life/api/v2/img/trap","femdom": "https://nekos.life/api/v2/img/femdom","boobs": "https://nekos.life/api/v2/img/boobs","hentai_api": "https://nekos.life/api/v2/img/hentai","anal": "https://nekos.life/api/v2/img/anal","cum": "https://nekos.life/api/v2/img/cum","pussy": "https://nekos.life/api/v2/img/pussy"}
    try:
        url_api = apis.get(categoria, apis["random"])
        response = requests.get(url_api, timeout=10)
        data = response.json()
        if "url" in data: return data["url"]
        elif "images" in data and len(data["images"]) > 0: return data["images"][0]["url"]
        return None
    except: return None

# ============ HANDLERS GENERALES ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await mostrar_menu(update, context)
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE): await mostrar_menu(update, context)
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = ("🤖 **INFO DEL BOT v2.8**\n\n**Versión:** TikTok Sin Logo\n**Fix:** Búsqueda sin Cookies\n**Host:** 24/7 Railway")
    await update.message.reply_text(texto, parse_mode='Markdown')
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = int(time.time() - START_TIME); horas, resto = divmod(uptime, 3600); minutos, segundos = divmod(resto, 60)
    await update.message.reply_text(f"🏓 Pong!\nBot activo: {horas}h {minutos}m {segundos}s")

# ============ HANDLERS DESCARGAS ============
async def download_and_send_audio(update, url, title_msg="Audio"):
    temp_dir = tempfile.mkdtemp()
    try:
        status_msg = await update.message.reply_text("⏳ Descargando audio...")
        ydl_opts = YDL_OPTS_AUDIO.copy()
        ydl_opts['outtmpl'] = os.path.join(temp_dir, '%(id)s.%(ext)s')
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True))
        filename = yt_dlp.YoutubeDL(ydl_opts).prepare_filename(info)
        mp3_file = os.path.splitext(filename)[0] + '.mp3'
        title = info.get('title', title_msg)
        await status_msg.delete()
        await update.message.reply_audio(audio=open(mp3_file, 'rb'), title=title, caption=f"🎵 {title}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

async def download_and_send_video(update, url, title_msg="Video"):
    temp_dir = tempfile.mkdtemp()
    try:
        status_msg = await update.message.reply_text("⏳ Descargando video sin logo...")
        ydl_opts = YDL_OPTS_VIDEO.copy()
        ydl_opts['outtmpl'] = os.path.join(temp_dir, '%(id)s.%(ext)s')
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True))
        filename = yt_dlp.YoutubeDL(ydl_opts).prepare_filename(info)
        title = info.get('title', title_msg)
        await status_msg.delete()
        await update.message.reply_video(video=open(filename, 'rb'), caption=f"🎬 {title}", supports_streaming=True)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

async def playaudio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usa así:\n`/playaudio nombre de la cancion`\n`/playaudio link`");
        return
    query = " ".join(context.args); user_id = update.effective_user.id
    if URL_REGEX.match(query):
        await download_and_send_audio(update, query, "Audio"); return
    await update.message.reply_text(f"🔍 Buscando en YouTube: {query}...")
    try:
        search_url = f"https://api.invidious.io/api/v1/search?q={query}&type=video"
        response = requests.get(search_url, timeout=10).json()
        results = response[:5]; search_results[user_id] = results
        msg = f"✅ Encontré 5 opciones:\n\n"
        for i, entry in enumerate(results, 1):
            title = entry.get('title', 'Sin título'); duration = entry.get('lengthSeconds', 0)
            mins, secs = divmod(duration, 60); msg += f"`{i}`. {title} - {mins}:{secs:02d}\n"
        msg += "\nResponde con un número del `1` al `5`"
        await update.message.reply_text(msg, reply_markup=ForceReply(selective=True))
    except Exception as e:
        await update.message.reply_text(f"❌ Error buscando: {str(e)}")

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in search_results or not update.message.text.isdigit(): return
    choice = int(update.message.text)
    if choice < 1 or choice > 5: await update.message.reply_text("❌ Elige del 1 al 5"); return
    results = search_results.pop(user_id); selected = results[choice-1]
    video_id = selected['videoId']
    url = f"https://www.youtube.com/watch?v={video_id}"
    await download_and_send_audio(update, url, selected['title'])

async def ttmp3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: await update.message.reply_text("❌ Usa: `/ttmp3 link_de_tiktok`"); return
    url = context.args[0]
    await download_and_send_audio(update, url, "Audio de TikTok") # Sigue igual, solo extrae audio

async def tt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: await update.message.reply_text("❌ Usa: `/tt link_de_tiktok`"); return
    url = context.args[0]
    await download_and_send_video(update, url, "Video de TikTok") # Ahora sin logo

# ============ HANDLERS NSFW ============
async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id; usuarios_verificados.add(user_id)
    await update.message.reply_text("✅ Verificado"); await mostrar_menu(update, context)
async def nsfw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await verificar_edad(update, context): return
    categoria = context.args[0].lower() if context.args else "random"
    await update.message.reply_text("🔄 Buscando imagen...")
    imagen_url = await asyncio.to_thread(obtener_imagen_nsfw, categoria)
    if imagen_url: await update.message.reply_photo(photo=imagen_url, caption=f"Categoría: {categoria}")
    else: await update.message.reply_text("❌ No se pudo obtener la imagen.")
async def categorias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await verificar_edad(update, context): return
    texto = "**Categorías:**\n\n"
    for cat in categorias_disponibles: texto += f"• `/nsfw {cat}`\n"
    await update.message.reply_text(texto, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = ("**COMANDOS v2.8:**\n\n**Descargas:**\n/playaudio nombre/link - Audio de cualquier plataforma\n/tt link - Video TikTok SIN LOGO\n/ttmp3 link - Audio TikTok\n**Otros:**\n/start /menu /info /ping /verify /nsfw")
    await update.message.reply_text(texto, parse_mode='Markdown')

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer(); data = query.data
    if data == "verify_yes": usuarios_verificados.add(query.from_user.id); await query.edit_message_text("✅ Verificado."); await asyncio.sleep(1); await mostrar_menu(update, context)
    elif data == "menu_verify": await verificar_edad(update, context)
    elif data == "menu_nsfw_random":
        if not await verificar_edad(update, context): return
        await query.edit_message_text("🔄 Buscando..."); imagen_url = await asyncio.to_thread(obtener_imagen_nsfw, "random")
        if imagen_url: await query.message.reply_photo(photo=imagen_url)
        await mostrar_menu(update, context)
    elif data == "back_menu": await mostrar_menu(update, context)
    else: await mostrar_menu(update, context)

async def cualquier_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE): await handle_choice(update, context)

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start)); application.add_handler(CommandHandler("menu", menu)); application.add_handler(CommandHandler("info", info)); application.add_handler(CommandHandler("ping", ping)); application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ttmp3", ttmp3)); application.add_handler(CommandHandler("playaudio", playaudio)); application.add_handler(CommandHandler("tt", tt))
    application.add_handler(CommandHandler("verify", verify)); application.add_handler(CommandHandler("nsfw", nsfw)); application.add_handler(CommandHandler("categorias", categorias))
    application.add_handler(CallbackQueryHandler(callback_handler)); application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cualquier_mensaje))
    logging.info("Bot v2.8 iniciado...")
    application.run_polling()

if __name__ == "__main__": main()
