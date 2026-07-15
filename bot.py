import os
import yt_dlp
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# CREAR CARPETA PARA GUARDAR LOS MP3
os.makedirs("downloads", exist_ok=True)

# PON TU TOKEN AQUÍ
TOKEN = "8546862851:AAE25jmlZ2dskHBDRO9UcOz2F41K8lPXJ2U"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hola! Soy tu bot de música\n"
        "Comandos:\n"
        "`/ttmp3 link_de_tiktok` - Descarga audio de TikTok\n"
        "`/playaudio nombre de canción` - Busca en YouTube y descarga el audio"
    )

async def ttmp3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Bajando audio de TikTok... 30 seg bro")
    await download_audio(update, context.args[0] if context.args else None, "tiktok")

async def playaudio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usa así: `/playaudio funk tonta`")
        return

    query = " ".join(context.args)
    await update.message.reply_text(f"🔍 Buscando: {query}...")
    await download_audio(update, f"ytsearch1:{query}", "youtube")

async def download_audio(update, url, source):
    try:
        if not url:
            await update.message.reply_text("❌ Falta el link o el nombre")
            return

        # OPCIONES PARA YT-DLP + FFMPEG
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'noplaylist': True,
            'default_search': 'ytsearch' if source == "youtube" else None,
        }

        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True))

        # Si es búsqueda, yt-dlp devuelve una lista
        if 'entries' in info:
            info = info['entries'][0]

        filename = yt_dlp.YoutubeDL(ydl_opts).prepare_filename(info)
        mp3_file = os.path.splitext(filename)[0] + '.mp3'
        title = info.get('title', 'Audio')

        await update.message.reply_text(f"✅ Encontrado: {title}\n📤 Enviando audio...")

        # ENVIAR EL MP3
        await update.message.reply_audio(
            audio=open(mp3_file, 'rb'),
            title=title,
            caption=f"🎵 {title}"
        )

        # BORRAR EL ARCHIVO DESPUÉS DE ENVIARLO
        os.remove(mp3_file)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    application = Application.builder().token(TOKEN).build()

    # COMANDOS
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ttmp3", ttmp3))
    application.add_handler(CommandHandler("playaudio", playaudio)) # <- NUEVO

    print("Bot iniciado...")
    application.run_polling()

if __name__ == "__main__":
    main()
