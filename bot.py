import os
import yt_dlp
import asyncio
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# CREAR CARPETA PARA GUARDAR LOS MP3 Y VIDEOS
os.makedirs("downloads", exist_ok=True)

# PON TU TOKEN AQUÍ
TOKEN = "8546862851:AAE25jmlZ2dskHBDRO9UcOz2F41K8lPXJ2U"

# NUMERO DEL CREADOR
OWNER_NUMBER = "929 207 065"

# GUARDAR BÚSQUEDAS TEMPORALES {user_id: [lista_de_videos]}
search_results = {}

MAX_SIZE = 50 * 1024 * 1024 # 50MB limite de Telegram

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hola! Soy tu bot\n"
        "Comandos:\n"
        "`/ttmp3 nombre` - Busca 5 audios y eliges\n"
        "`/playaudio nombre` - Busca 1 audio directo\n"
        "`/tt link_de_tiktok` - Descarga video de TikTok\n"
        "`/owner` - Número del creador"
    )

async def ttmp3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usa así: `/ttmp3 funk tonta slowed`")
        return

    query = " ".join(context.args)
    user_id = update.effective_user.id
    await update.message.reply_text(f"🔍 Buscando 5 versiones de: {query}...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'default_search': 'ytsearch',
        'extract_flat': True, # solo info, no descarga
    }

    try:
        loop = asyncio.get_event_loop()
        # Buscamos 5 resultados
        info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(f"ytsearch5:{query}", download=False))

        results = info['entries']
        search_results[user_id] = results # guardamos para elegir después

        msg = f"✅ Encontré 5 opciones para `{query}`:\n\n"
        for i, entry in enumerate(results, 1):
            title = entry.get('title', 'Sin título')
            duration = entry.get('duration', 0)
            mins, secs = divmod(duration, 60)
            msg += f"`{i}`. {title} - {mins}:{secs:02d}\n"

        msg += "\nResponde con un número del `1` al `5` para descargar"
        await update.message.reply_text(msg, reply_markup=ForceReply(selective=True))

    except Exception as e:
        await update.message.reply_text(f"❌ Error buscando: {str(e)}")

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in search_results or not update.message.text.isdigit():
        return # no es una elección

    choice = int(update.message.text)
    if choice < 1 or choice > 5:
        await update.message.reply_text("❌ Elige del 1 al 5")
        return

    results = search_results.pop(user_id)
    selected = results[choice-1]
    url = f"https://www.youtube.com/watch?v={selected['id']}"

    await update.message.reply_text(f"⏳ Descargando: {selected['title']}...")
    await download_audio(update, url, "youtube")

async def playaudio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usa así: `/playaudio funk tonta`")
        return
    query = " ".join(context.args)
    await update.message.reply_text(f"🔍 Buscando: {query}...")
    await download_audio(update, f"ytsearch1:{query}", "youtube")

async def download_audio(update, url, source):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            'quiet': True, 'noplaylist': True,
        }
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True))
        filename = yt_dlp.YoutubeDL(ydl_opts).prepare_filename(info)
        mp3_file = os.path.splitext(filename)[0] + '.mp3'
        title = info.get('title', 'Audio')

        await update.message.reply_audio(audio=open(mp3_file, 'rb'), title=title, caption=f"🎵 {title}")
        os.remove(mp3_file)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def tt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usa: `/tt link_de_tiktok`")
        return

    url = context.args[0]
    await update.message.reply_text("⏳ Descargando video...")

    try:
        # OPCIONES: si pesa mucho lo comprime a 720p 30fps
        ydl_opts = {
            'format': 'best[ext=mp4][filesize<50M]/best[ext=mp4]/best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'quiet': True, 'noplaylist': True,
            'http_headers': {'User-Agent': 'Mozilla/5.0'},
            'postprocessor_args': ['-fs', '50M'] # fuerza limite
        }

        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True))

        filename = yt_dlp.YoutubeDL(ydl_opts).prepare_filename(info)
        filesize = os.path.getsize(filename)

        if filesize > MAX_SIZE:
            await update.message.reply_text("❌ El video pesa más de 50MB. Telegram no deja enviarlo.")
            os.remove(filename)
            return

        title = info.get('title', 'TikTok Video')
        await update.message.reply_video(video=open(filename, 'rb'), caption=title, supports_streaming=True)
        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"👑 Creador del bot\n📱 Número: {OWNER_NUMBER}")

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ttmp3", ttmp3))
    application.add_handler(CommandHandler("playaudio", playaudio))
    application.add_handler(CommandHandler("tt", tt))
    application.add_handler(CommandHandler("owner", owner))
    # Para capturar cuando eliges 1 al 5
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice))

    print("Bot iniciado...")
    application.run_polling()

if __name__ == "__main__":
    main()
