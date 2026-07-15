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
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from youtubesearchpython import VideosSearch # NUEVA LIBRERIA PARA BUSCAR

TOKEN = "8546862851:AAE25jmlZ2dskHBDRO9UcOz2F41K8lPXJ2U"
OWNER_NUMBER = "929 207 065"
START_TIME = time.time()

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

usuarios_verificados = set()
categorias_disponibles = ["random", "waifu", "hentai", "neko", "blowjob","trap", "femdom", "boobs", "hentai_api", "anal", "cum", "pussy"]
search_results = {}

YDL_OPTS_AUDIO = {
    'format': 'bestaudio/best',
    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
    'quiet': True, 'noplaylist': True, 'nocheckcertificate': True,
}

YDL_OPTS_VIDEO = {
    'format': 'best[ext=mp4][filesize<50M]/best[ext=mp4]/best',
    'quiet': True, 'noplaylist': True, 'nocheckcertificate': True,
}

URL_REGEX = re.compile(r'(https?://\S+)') # AHORA AGARRA SOLO EL LINK DEL TEXTO

# ============ FUNCIONES ============
async def mostrar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔞 Verificar Edad", callback_data="menu_verify")],[InlineKeyboardButton("🎲 NSFW Random", callback_data="menu_nsfw_random")],[InlineKeyboardButton("⬇️ Descargas", callback_data="menu_descargas")],[InlineKeyboardButton("❓ Ayuda", callback_data="menu_help")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    texto = "👋 **Menú de Comandos**\n\nElige una opción:"
    if update.callback_query: await update.callback_query.edit_message_text(texto, reply_markup=reply_markup, parse_mode='Markdown')
    else: await update.message.reply_text(texto, reply_markup=reply_markup, parse_mode='Markdown')

async def download_and_send_audio(update, url, title_msg="Audio"):
    temp_dir = tempfile.mkdtemp()
    try:
        status_msg = await update.message.reply_text("⏳ Descargando audio...")
        ydl_opts = YDL_OPTS_AUDIO.copy(); ydl_opts['outtmpl'] = os.path.join(temp_dir, '%(id)s.%(ext)s')
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True))
        filename = yt_dlp.YoutubeDL(ydl_opts).prepare_filename(info)
        mp3_file = os.path.splitext(filename)[0] + '.mp3'
        title = info.get('title', title_msg)
        await status_msg.delete()
        await update.message.reply_audio(audio=open(mp3_file, 'rb'), title=title, caption=f"🎵 {title}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
    finally: shutil.rmtree(temp_dir, ignore_errors=True)

async def download_and_send_video(update, url, title_msg="Video"):
    temp_dir = tempfile.mkdtemp()
    try:
        status_msg = await update.message.reply_text("⏳ Descargando video sin logo...")
        ydl_opts = YDL_OPTS_VIDEO.copy(); ydl_opts['outtmpl'] = os.path.join(temp_dir, '%(id)s.%(ext)s')
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True))
        filename = yt_dlp.YoutubeDL(ydl_opts).prepare_filename(info)
        title = info.get('title', title_msg)
        await status_msg.delete()
        await update.message.reply_video(video=open(filename, 'rb'), caption=f"🎬 {title}", supports_streaming=True)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
    finally: shutil.rmtree(temp_dir, ignore_errors=True)

# FIX 1: BUSQUEDA CON YOUTUBESEARCHPYTHON
async def playaudio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usa así:\n`/playaudio nombre de la cancion`\n`/playaudio link`"); return
    query = " ".join(context.args); user_id = update.effective_user.id

    if URL_REGEX.match(query):
        match = URL_REGEX.search(query) # Extrae solo el link
        await download_and_send_audio(update, match.group(1), "Audio"); return

    await update.message.reply_text(f"🔍 Buscando en YouTube: {query}...")
    try:
        videos_search = VideosSearch(query, limit=5)
        results = videos_search.result()['result']
        search_results[user_id] = results
        
        msg = f"✅ Encontré 5 opciones:\n\n"
        for i, entry in enumerate(results, 1):
            title = entry.get('title', 'Sin título'); duration = entry.get('duration', '0:00')
            msg += f"`{i}`. {title} - {duration}\n"
        msg += "\nResponde con un número del `1` al `5`"
        await update.message.reply_text(msg, reply_markup=ForceReply(selective=True))
    except Exception as e:
        await update.message.reply_text(f"❌ Error buscando. Intenta con el link directo")

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in search_results or not update.message.text.isdigit(): return
    choice = int(update.message.text)
    if choice < 1 or choice > 5: await update.message.reply_text("❌ Elige del 1 al 5"); return
    results = search_results.pop(user_id); selected = results[choice-1]
    url = selected['link']
    await download_and_send_audio(update, url, selected['title'])

# FIX 2: LIMPIAR LINK DE TIKTOK
async def ttmp3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: await update.message.reply_text("❌ Usa: `/ttmp3 link_de_tiktok`"); return
    text = " ".join(context.args)
    match = URL_REGEX.search(text) # Agarra solo el link aunque pegues todo
    if not match: await update.message.reply_text("❌ No encontré ningún link"); return
    url = match.group(1)
    await download_and_send_audio(update, url, "Audio de TikTok")

async def tt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: await update.message.reply_text("❌ Usa: `/tt link_de_tiktok`"); return
    text = " ".join(context.args)
    match = URL_REGEX.search(text) # Agarra solo el link aunque pegues todo
    if not match: await update.message.reply_text("❌ No encontré ningún link"); return
    url = match.group(1)
    await download_and_send_video(update, url, "Video de TikTok")

# Resto de comandos iguales...
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await mostrar_menu(update, context)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("**COMANDOS v2.9:**\n/playaudio nombre/link\n/tt link\n/ttmp3 link", parse_mode='Markdown')
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): await mostrar_menu(update, context)
async def cualquier_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE): await handle_choice(update, context)

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ttmp3", ttmp3))
    application.add_handler(CommandHandler("playaudio", playaudio))
    application.add_handler(CommandHandler("tt", tt))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cualquier_mensaje))
    logging.info("Bot v2.9 iniciado...")
    application.run_polling()

if __name__ == "__main__": main()
