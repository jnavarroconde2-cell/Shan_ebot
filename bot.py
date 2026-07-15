import os
import yt_dlp
import asyncio
import logging
import random
import requests
import time
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters, ConversationHandler

# ============ CONFIGURACIÓN ============
os.makedirs("downloads", exist_ok=True)

TOKEN = "8546862851:AAE25jmlZ2dskHBDRO9UcOz2F41K8lPXJ2U" # Cambia esto por tu token de @BotFather
OWNER_NUMBER = "929 207 065"
ADMIN_ID = 123456789

MAX_SIZE = 50 * 1024 * 1024 # 50MB limite de Telegram
START_TIME = time.time()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Base de datos simple NSFW
usuarios_verificados = set()
categorias_disponibles = ["random", "waifu", "hentai", "neko", "blowjob","trap", "femdom", "boobs", "hentai_api", "anal", "cum", "pussy"]
search_results = {} # Para /playaudio

# ESTADOS PARA LA CONVERSACION DE /HOLA
HABLANDO = 1

# ============ FUNCIONES AUXILIARES NSFW ============
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
    except Exception as e: logging.error(f"Error obteniendo imagen: {e}"); return None

# ============ HANDLERS GENERALES ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await mostrar_menu(update, context)
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE): await mostrar_menu(update, context)
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = ("🤖 **INFO DEL BOT**\n\n**Versión:** 2.2\n**Funciones:** Descargas + NSFW + Chat\n**Creador:** @TuUsuario\n**Límite:** 50MB por video\n**Host:** 24/7 Railway")
    await update.message.reply_text(texto, parse_mode='Markdown')
async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE): await help_command(update, context)
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = int(time.time() - START_TIME); horas, resto = divmod(uptime, 3600); minutos, segundos = divmod(resto, 60)
    await update.message.reply_text(f"🏓 Pong!\nBot activo: {horas}h {minutos}m {segundos}s")
async def owner(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text(f"👑 Creador del bot\n📱 Número: {OWNER_NUMBER}")

# NUEVO: /HOLA CONVERSACION
async def hola_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.effective_user.first_name
    await update.message.reply_text(f"👋 Hola {nombre}! ¿Cómo estás hoy?")
    return HABLANDO
async def hola_responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text.lower()
    respuestas = {"bien": "Me alegra escuchar eso 😄 ¿Y qué tal tu día?","mal": "Uff que pena bro 😔 ¿Quieres contarme qué pasó?","aburrido": "Ya veo... ¿quieres usar /tt o /playaudio? 👀","gracias": "De nada bro! Para eso estoy 🔥","chau": "Ya te me vas? Cuídate mucho! 👋"}
    respuesta = "Ya veo... cuéntame más 👀"
    for palabra, resp in respuestas.items():
        if palabra in user_msg: respuesta = resp; break
    await update.message.reply_text(respuesta)
    if "chau" in user_msg or "bye" in user_msg:
        await update.message.reply_text("Listo, aquí estaré cuando me necesites 😎")
        return ConversationHandler.END
    return HABLANDO
async def hola_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ok, terminamos la charla. Usa /menu para volver.")
    return ConversationHandler.END

# ============ HANDLERS DESCARGAS ============
async def ttmp3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: await update.message.reply_text("❌ Usa así: `/ttmp3 https://www.tiktok.com/...`"); return
    url = context.args[0]; await update.message.reply_text("⏳ Extrayendo audio de TikTok..."); await download_audio(update, url, "tiktok")
async def playaudio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: await update.message.reply_text("❌ Usa así: `/playaudio funk tonta slowed`"); return
    query = " ".join(context.args); user_id = update.effective_user.id
    await update.message.reply_text(f"🔍 Buscando 5 versiones de: {query}...")
    ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True, 'default_search': 'ytsearch', 'extract_flat': True}
    try:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(f"ytsearch5:{query}", download=False))
        results = info['entries']; search_results[user_id] = results
        msg = f"✅ Encontré 5 opciones para `{query}`:\n\n"
        for i, entry in enumerate(results, 1):
            title = entry.get('title', 'Sin título'); duration = entry.get('duration', 0)
            mins, secs = divmod(duration, 60); msg += f"`{i}`. {title} - {mins}:{secs:02d}\n"
        msg += "\nResponde con un número del `1` al `5` para descargar"
        await update.message.reply_text(msg, reply_markup=ForceReply(selective=True))
    except Exception as e: await update.message.reply_text(f"❌ Error buscando: {str(e)}")
async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in search_results or not update.message.text.isdigit(): return
    choice = int(update.message.text)
    if choice < 1 or choice > 5: await update.message.reply_text("❌ Elige del 1 al 5"); return
    results = search_results.pop(user_id); selected = results[choice-1]
    url = f"https://www.youtube.com/watch?v={selected['id']}"
    await update.message.reply_text(f"⏳ Descargando: {selected['title']}..."); await download_audio(update, url, "youtube")
async def download_audio(update, url, source):
    try:
        ydl_opts = {'format': 'bestaudio/best', 'outtmpl': 'downloads/%(id)s.%(ext)s','postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],'quiet': True, 'noplaylist': True}
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True))
        filename = yt_dlp.YoutubeDL(ydl_opts).prepare_filename(info); mp3_file = os.path.splitext(filename)[0] + '.mp3'
        title = info.get('title', 'Audio')
        await update.message.reply_audio(audio=open(mp3_file, 'rb'), title=title, caption=f"🎵 {title}"); os.remove(mp3_file)
    except Exception as e: await update.message.reply_text(f"❌ Error: {str(e)}")
async def tt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: await update.message.reply_text("❌ Usa: `/tt link_de_tiktok`"); return
    url = context.args[0]; await update.message.reply_text("⏳ Descargando video de TikTok sin marca de agua...")
    try:
        ydl_opts = {'format': 'best[ext=mp4][filesize<50M]/best[ext=mp4]/best','outtmpl': 'downloads/%(id)s.%(ext)s', 'quiet': True, 'noplaylist': True,'http_headers': {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.tiktok.com/'},'extractor_args': {'tiktok': {'api': ['web']} },'postprocessor_args': ['-fs', '50M']}
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True))
        filename = yt_dlp.YoutubeDL(ydl_opts).prepare_filename(info); filesize = os.path.getsize(filename)
        if filesize > MAX_SIZE: await update.message.reply_text("❌ El video pesa más de 50MB. Telegram no deja enviarlo."); os.remove(filename); return
        title = info.get('title', 'TikTok Video')
        await update.message.reply_video(video=open(filename, 'rb'), caption=f"🎬 {title}", supports_streaming=True); os.remove(filename)
    except Exception as e: await update.message.reply_text(f"❌ Error: {str(e)}")

# ============ HANDLERS NSFW ============
async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id; usuarios_verificados.add(user_id)
    await update.message.reply_text("✅ Verificación completada. Ya puedes usar el menú"); await mostrar_menu(update, context)
async def nsfw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await verificar_edad(update, context): return
    categoria = context.args[0].lower() if context.args else "random"
    if categoria not in categorias_disponibles: await update.message.reply_text(f"❌ Categoría no válida. Usa /categorias para ver la lista"); return
    await update.message.reply_text("🔄 Buscando imagen...")
    imagen_url = await asyncio.to_thread(obtener_imagen_nsfw, categoria)
    if imagen_url: await update.message.reply_photo(photo=imagen_url, caption=f"Categoría: {categoria}")
    else: await update.message.reply_text("❌ No se pudo obtener la imagen. Intenta de nuevo.")
async def categorias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await verificar_edad(update, context): return
    texto = "**Categorías disponibles:**\n\n"
    for cat in categorias_disponibles: texto += f"• `/nsfw {cat}`\n"
    await update.message.reply_text(texto, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = ("**LISTA DE COMANDOS:**\n\n**Generales:**\n/start - Iniciar el bot\n/menu - Ver todos los comandos\n/info - Info del bot\n/ayuda - Ayuda\n/hola - Chatear con el bot\n/ping - Ver si el bot responde\n/owner - Contacto del creador\n**Descargas:**\n/playaudio nombre - Descargar audio de YouTube\n/tt link - Descargar videos de TikTok\n/ttmp3 link - Extraer solo el audio MP3 de TikTok\n**NSFW +18:**\n/verify - Verificar edad\n/nsfw categoria - Enviar imagen\n/categorias - Ver categorías")
    await update.message.reply_text(texto, parse_mode='Markdown')

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer(); data = query.data
    if data == "verify_yes": usuarios_verificados.add(query.from_user.id); await query.edit_message_text("✅ Verificación completada."); await asyncio.sleep(1); await mostrar_menu(update, context)
    elif data == "verify_no": await query.edit_message_text("❌ Debes ser mayor de 18 para usar este bot.")
    elif data == "menu_verify": await verificar_edad(update, context)
    elif data == "menu_nsfw_random":
        if not await verificar_edad(update, context): return
        await query.edit_message_text("🔄 Buscando imagen..."); imagen_url = await asyncio.to_thread(obtener_imagen_nsfw, "random")
        if imagen_url: await query.message.reply_photo(photo=imagen_url, caption="Categoría: random")
        else: await query.message.reply_text("❌ No se pudo obtener la imagen."); await mostrar_menu(update, context)
    elif data == "menu_categorias":
        if not await verificar_edad(update, context): return
        texto = "**Categorías disponibles:**\n\n"
        for cat in categorias_disponibles: texto += f"• `/nsfw {cat}`\n"
        await query.edit_message_text(texto, parse_mode='Markdown'); await asyncio.sleep(3); await mostrar_menu(update, context)
    elif data == "menu_help": await help_command(update, context); await asyncio.sleep(3); await mostrar_menu(update, context)
    elif data == "menu_descargas":
        texto = "**Comandos de Descarga:**\n`/ttmp3 link` - Audio de TikTok\n`/playaudio nombre` - Busca 5 audios\n`/tt link` - Video de TikTok\n"
        await query.edit_message_text(texto, parse_mode='Markdown'); await asyncio.sleep(3); await mostrar_menu(update, context)
    elif data == "back_menu": await mostrar_menu(update, context)

async def cualquier_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE): await mostrar_menu(update, context)

def main():
    application = Application.builder().token(TOKEN).build()
    # ConversationHandler para /hola
    conv_handler = ConversationHandler(entry_points=[CommandHandler("hola", hola_start)],states={HABLANDO: [MessageHandler(filters.TEXT & ~filters.COMMAND, hola_responder)]},fallbacks=[CommandHandler("cancelar", hola_cancelar)])
    application.add_handler(conv_handler)
    # Generales
    application.add_handler(CommandHandler("start", start)); application.add_handler(CommandHandler("menu", menu)); application.add_handler(CommandHandler("info", info)); application.add_handler(CommandHandler("ayuda", ayuda)); application.add_handler(CommandHandler("ping", ping)); application.add_handler(CommandHandler("owner", owner)); application.add_handler(CommandHandler("help", help_command))
    # Descargas
    application.add_handler(CommandHandler("ttmp3", ttmp3)); application.add_handler(CommandHandler("playaudio", playaudio)); application.add_handler(CommandHandler("tt", tt))
    # NSFW
    application.add_handler(CommandHandler("verify", verify)); application.add_handler(CommandHandler("nsfw", nsfw)); application.add_handler(CommandHandler("categorias", categorias))
    # Callbacks
    application.add_handler(CallbackQueryHandler(callback_handler)); application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice)); application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cualquier_mensaje))
    logging.info("Bot iniciado...")
    application.run_polling()

if __name__ == "__main__": main()
