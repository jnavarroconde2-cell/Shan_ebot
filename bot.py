import os
import yt_dlp
import asyncio
import logging
import random
import requests
import time
import tempfile
import shutil
import json
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

# ============ OPCIONES YT-DLP ANTI-BOT 2026 ============
YDL_OPTS_AUDIO = {
    'format': 'bestaudio/best',
    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
    'quiet': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'age_limit': 18,
    'extractor_args': {'youtube': {'player_client': ['android', 'ios', 'web']}}, # Anti-bot mejorado
}

YDL_OPTS_SEARCH = {
    'format': 'bestaudio/best',
    'quiet': True,
    'noplaylist': True,
    'default_search': 'ytsearch',
    'extract_flat': True,
    'age_limit': 18,
    'extractor_args': {'youtube': {'player_client': ['android', 'ios', 'web']}} # Anti-bot mejorado
}

YDL_OPTS_VIDEO = { # NUEVO para /tt
    'format': 'best[ext=mp4][filesize<50M]/best[ext=mp4]/best',
    'quiet': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'age_limit': 18,
    'extractor_args': {'youtube': {'player_client': ['android', 'ios', 'web']}}
}

# ============ FUNCIONES AUXILIARES ============
async def mostrar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔞 Verificar Edad", callback_data="menu_verify")],
        [InlineKeyboardButton("🎲 NSFW Random", callback_data="menu_nsfw_random")],
        [InlineKeyboardButton("📂 Ver Categorías", callback_data="menu_categorias")],
        [InlineKeyboardButton("📌 Pinterest", callback_data="menu_pin")],
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

# ============ FUNCIÓN NSFW CORREGIDA ============
def obtener_imagen_nsfw(categoria: str = "random"):
    apis = {
        "random": "https://api.waifu.im/search/?is_nsfw=true",
        "waifu": "https://api.waifu.im/search/?is_nsfw=true&included_tags=waifu",
        "hentai": "https://api.waifu.im/search/?is_nsfw=true&included_tags=hentai",
        "neko": "https://api.waifu.im/search/?is_nsfw=true&included_tags=maid",
        "blowjob": "https://api.waifu.im/search/?is_nsfw=true&included_tags=uniform",
        "trap": "https://api.waifu.im/search/?is_nsfw=true&included_tags=uniform",
        "femdom": "https://api.waifu.im/search/?is_nsfw=true&included_tags=uniform",
        "boobs": "https://api.waifu.im/search/?is_nsfw=true&included_tags=uniform",
        "hentai_api": "https://api.waifu.im/search/?is_nsfw=true&included_tags=hentai",
        "anal": "https://api.waifu.im/search/?is_nsfw=true&included_tags=hentai",
        "cum": "https://api.waifu.im/search/?is_nsfw=true&included_tags=hentai",
        "pussy": "https://api.waifu.im/search/?is_nsfw=true&included_tags=hentai"
    }
    nekos_apis = {
        "neko": "https://nekos.life/api/v2/img/lewd",
        "blowjob": "https://nekos.life/api/v2/img/blowjob",
        "trap": "https://nekos.life/api/v2/img/trap",
        "femdom": "https://nekos.life/api/v2/img/femdom",
        "boobs": "https://nekos.life/api/v2/img/boobs",
        "hentai_api": "https://nekos.life/api/v2/img/hentai",
        "anal": "https://nekos.life/api/v2/img/anal",
        "cum": "https://nekos.life/api/v2/img/cum",
        "pussy": "https://nekos.life/api/v2/img/pussy"
    }
    try:
        url_api = apis.get(categoria, apis["random"])
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url_api, timeout=10, headers=headers)
        data = response.json()
        if "images" in data and len(data["images"]) > 0: return data["images"][0]["url"]
        elif "url" in data: return data["url"]
        if categoria in nekos_apis:
            response = requests.get(nekos_apis[categoria], timeout=10, headers=headers)
            data = response.json()
            if "url" in data: return data["url"]
        return None
    except Exception as e:
        logging.error(f"Error en NSFW: {e}")
        return None

# ============ FUNCIÓN PINTEREST CORREGIDA ============
def buscar_pinterest(query: str):
    try:
        search_query = query.replace(' ', '%20')
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5",}
        search_url = f"https://www.pinterest.com/search/pins/?q={search_query}&rs=typed"
        session = requests.Session()
        session.headers.update(headers)
        r = session.get(search_url, timeout=15)
        img_urls = []
        pattern = r'https://i\.pinimg\.com/[^"\']+\.(?:jpg|jpeg|png|gif)'
        matches = re.findall(pattern, r.text)
        for url in matches:
            clean_url = url.split('?')[0]
            if '236x' in clean_url: clean_url = clean_url.replace('236x', '736x')
            elif '474x' in clean_url: clean_url = clean_url.replace('474x', '736x')
            if clean_url not in img_urls: img_urls.append(clean_url)
        if img_urls: return random.choice(img_urls[:15])
        unsplash_url = f"https://source.unsplash.com/800x600/?{query.replace(' ',')}"
        response = requests.get(unsplash_url, allow_redirects=True, timeout=10)
        if response.status_code == 200: return response.url
        return None
    except Exception as e:
        logging.error(f"Error en Pinterest: {e}")
        try: return f"https://picsum.photos/800/600?random={random.randint(1,1000)}"
        except: return None

# ============ HANDLERS GENERALES ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await mostrar_menu(update, context)
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE): await mostrar_menu(update, context)
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = ("🤖 **INFO DEL BOT v2.7**\n\n**Versión:** Descarga Silenciosa + Anti-Bot YT\n**Fix:** player_client android/ios/web")
    await update.message.reply_text(texto, parse_mode='Markdown')
async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE): await help_command(update, context)
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = int(time.time() - START_TIME); horas, resto = divmod(uptime, 3600); minutos, segundos = divmod(resto, 60)
    await update.message.reply_text(f"🏓 Pong!\nBot activo: {horas}h {minutos}m {segundos}s")
async def owner(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text(f"👑 Creador: {OWNER_NUMBER}")

async def hola_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.effective_user.first_name
    await update.message.reply_text(f"👋 Hola {nombre}! ¿Cómo estás hoy?")
    return HABLANDO
async def hola_responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text.lower()
    respuestas = {"bien": "Me alegra 😄 ¿Y qué tal tu día?","mal": "Uff que pena 😔 ¿Quieres contarme?","aburrido": "Usa /tt o /playaudio 👀","gracias": "De nada bro! 🔥","chau": "Cuídate! 👋"}
    respuesta = "Ya veo... cuéntame más 👀"
    for palabra, resp in respuestas.items():
        if palabra in user_msg: respuesta = resp; break
    await update.message.reply_text(respuesta)
    if "chau" in user_msg: return ConversationHandler.END
    return HABLANDO
async def hola_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ok, terminamos la charla. Usa /menu para volver.")
    return ConversationHandler.END

# ============ HANDLERS DESCARGAS MODO SILENCIOSO ============
async def download_and_send_audio(update, url, title_msg="Audio"):
    temp_dir = tempfile.mkdtemp()
    try:
        status_msg = await update.message.reply_text("⏳ Descargando...")
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

async def ttmp3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: await update.message.reply_text("❌ Usa: `/ttmp3 link_de_tiktok`"); return
    url = context.args[0]
    await download_and_send_audio(update, url, "Audio de TikTok")

async def playaudio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: await update.message.reply_text("❌ Usa: `/playaudio nombre de la cancion`"); return
    query = " ".join(context.args); user_id = update.effective_user.id
    await update.message.reply_text(f"🔍 Buscando: {query}...")
    try:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(YDL_OPTS_SEARCH).extract_info(f"ytsearch5:{query}", download=False))
        results = info['entries']; search_results[user_id] = results
        msg = f"✅ Encontré 5 opciones:\n\n"
        for i, entry in enumerate(results, 1):
            title = entry.get('title', 'Sin título'); duration = entry.get('duration', 0)
            mins, secs = divmod(duration, 60); msg += f"`{i}`. {title} - {mins}:{secs:02d}\n"
        msg += "\nResponde con un número del `1` al `5`"
        await update.message.reply_text(msg, reply_markup=ForceReply(selective=True))
    except Exception as e: await update.message.reply_text(f"❌ Error buscando: {str(e)}")

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in search_results or not update.message.text.isdigit(): return
    choice = int(update.message.text)
    if choice < 1 or choice > 5: await update.message.reply_text("❌ Elige del 1 al 5"); return
    results = search_results.pop(user_id); selected = results[choice-1]
    url = f"https://www.youtube.com/watch?v={selected['id']}"
    await download_and_send_audio(update, url, selected['title'])

async def tt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: await update.message.reply_text("❌ Usa: `/tt link_de_tiktok`"); return
    url = context.args[0]; await update.message.reply_text("⏳ Descargando video...")
    try:
        temp_dir = tempfile.mkdtemp()
        ydl_opts = YDL_OPTS_VIDEO.copy() # CAMBIO 2: Usa el nuevo anti-bot
        ydl_opts['outtmpl'] = os.path.join(temp_dir, '%(id)s.%(ext)s')
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True))
        filename = yt_dlp.YoutubeDL(ydl_opts).prepare_filename(info)
        await update.message.reply_video(video=open(filename, 'rb'), caption=f"🎬 {info.get('title', 'TikTok')}", supports_streaming=True)
    except Exception as e: await update.message.reply_text(f"❌ Error: {str(e)}")
    finally: shutil.rmtree(temp_dir, ignore_errors=True)

# ============ HANDLERS NSFW ============
async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id; usuarios_verificados.add(user_id)
    await update.message.reply_text("✅ Verificado"); await mostrar_menu(update, context)

async def nsfw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await verificar_edad(update, context): return
    categoria = context.args[0].lower() if context.args else "random"
    if categoria not in categorias_disponibles:
        await update.message.reply_text(f"❌ Categoría no válida. Usa: {', '.join(categorias_disponibles)}")
        return
    msg = await update.message.reply_text("🔄 Buscando imagen...")
    imagen_url = await asyncio.to_thread(obtener_imagen_nsfw, categoria)
    if imagen_url:
        await msg.delete()
        await update.message.reply_photo(photo=imagen_url, caption=f"🔞 Categoría: {categoria}")
    else:
        await msg.edit_text("❌ No se pudo obtener la imagen. Intenta con otra categoría.")

async def categorias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await verificar_edad(update, context): return
    texto = "**Categorías NSFW:**\n\n"
    for cat in categorias_disponibles: texto += f"• `/nsfw {cat}`\n"
    await update.message.reply_text(texto, parse_mode='Markdown')

# ============ HANDLER PINTEREST CORREGIDO ============
async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usa: `/pin memes de goku`\nEjemplo: `/pin paisajes naturales`")
        return
    query = " ".join(context.args)
    msg = await update.message.reply_text(f"🔍 Buscando imágenes de: *{query}*...", parse_mode='Markdown')
    imagen_url = await asyncio.to_thread(buscar_pinterest, query)
    if imagen_url:
        try:
            await msg.delete()
            await update.message.reply_photo(photo=imagen_url, caption=f"📌 **Resultado:** {query}\n🔍 Fuente: Pinterest",parse_mode='Markdown')
        except Exception as e:
            await msg.edit_text(f"❌ Error al enviar la imagen: {str(e)}")
    else:
        await msg.edit_text("❌ No se encontraron imágenes. Intenta con otras palabras clave.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = ("**COMANDOS v2.7:**\n\n**Generales:**\n/start /menu /info /hola /ping /owner\n**Descargas:**\n/playaudio nombre - Busca 5 audios\n/ttmp3 link - Audio de TikTok\n/tt link - Video de TikTok\n**Búsqueda:**\n/pin texto - Busca imágenes en Pinterest\n**NSFW +18:**\n/verify /nsfw /categorias")
    await update.message.reply_text(texto, parse_mode='Markdown')

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer(); data = query.data
    if data == "verify_yes": usuarios_verificados.add(query.from_user.id); await query.edit_message_text("✅ Verificado."); await asyncio.sleep(1); await mostrar_menu(update, context)
    elif data == "menu_verify": await verificar_edad(update, context)
    elif data == "menu_nsfw_random":
        if not await verificar_edad(update, context): return
        await query.edit_message_text("🔄 Buscando...")
        imagen_url = await asyncio.to_thread(obtener_imagen_nsfw, "random")
        if imagen_url: await query.message.reply_photo(photo=imagen_url)
        await mostrar_menu(update, context)
    elif data == "back_menu": await mostrar_menu(update, context)
    else: await mostrar_menu(update, context)

async def cualquier_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE): await handle_choice(update, context)

def main():
    application = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(entry_points=[CommandHandler("hola", hola_start)],states={HABLANDO: [MessageHandler(filters.TEXT & ~filters.COMMAND, hola_responder)]},fallbacks=[CommandHandler("cancelar", hola_cancelar)])
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start)); application.add_handler(CommandHandler("menu", menu)); application.add_handler(CommandHandler("info", info)); application.add_handler(CommandHandler("ayuda", ayuda)); application.add_handler(CommandHandler("ping", ping)); application.add_handler(CommandHandler("owner", owner)); application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ttmp3", ttmp3)); application.add_handler(CommandHandler("playaudio", playaudio)); application.add_handler(CommandHandler("tt", tt))
    application.add_handler(CommandHandler("verify", verify)); application.add_handler(CommandHandler("nsfw", nsfw)); application.add_handler(CommandHandler("categorias", categorias))
    application.add_handler(CommandHandler("pin", pin))
    application.add_handler(CallbackQueryHandler(callback_handler)); application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cualquier_mensaje))
    logging.info("Bot v2.7 iniciado...")
    application.run_polling()

if __name__ == "__main__": main()
