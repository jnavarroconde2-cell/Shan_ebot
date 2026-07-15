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
        "👋 Hola! Soy tu bot de TikTok\n"
        "Usa: `/ttmp3 link_de_tiktok` para descargar solo el audio en mp3"
    )

async def ttmp3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Bajando audio de TikTok... 30 seg bro")

    try:
        if not context.args:
            await update.message.reply_text("❌ Usa así: `/ttmp3 https://www.tiktok.com/...`")
            return

        url = context.args[0]

        # OPCIONES PARA TIKTOK + FFMPEG
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(uploader)s - %(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'noplaylist': True,
        }

        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True))

        filename = yt_dlp.YoutubeDL(ydl_opts).prepare_filename(info)
        mp3_file = os.path.splitext(filename)[0] + '.mp3'
        title = info.get('title', 'TikTok Audio')
        uploader = info.get('uploader', 'TikTok')

        # ENVIAR EL MP3
        await update.message.reply_audio(
            audio=open(mp3_file, 'rb'),
            title=title,
            performer=uploader,
            caption=f"✅ Audio de: {uploader}"
        )

        # BORRAR EL ARCHIVO DESPUÉS DE ENVIARLO
        os.remove(mp3_file)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}\nAsegúrate que el link sea público")

def main():
    application = Application.builder().token(TOKEN).build()

    # COMANDOS
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ttmp3", ttmp3)) # <- AQUI CAMBIO

    print("Bot iniciado...")
    application.run_polling()

if __name__ == "__main__":
    main()
