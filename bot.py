import os
import yt_dlp
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# CREAR CARPETA PARA GUARDAR LOS VIDEOS
os.makedirs("downloads", exist_ok=True)

# PON TU TOKEN AQUÍ
TOKEN = "8546862851:AAE25jmlZ2dskHBDRO9UcOz2F41K8lPXJ2U"

# NUMERO DEL CREADOR
OWNER_NUMBER = "929 207 065"

async def tt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usa: `/tt link_de_tiktok`")
        return

    url = context.args[0]
    await update.message.reply_text("⏳ Descargando...")

    try:
        # OPCIONES PARA BAJAR EL VIDEO
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'quiet': True,
            'noplaylist': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }

        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True))

        filename = yt_dlp.YoutubeDL(ydl_opts).prepare_filename(info)
        title = info.get('title', 'TikTok Video')

        # ENVIAR EL VIDEO
        await update.message.reply_video(
            video=open(filename, 'rb'),
            caption=title,
            supports_streaming=True
        )

        # BORRAR EL ARCHIVO DESPUÉS DE ENVIARLO
        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👑 Creador del bot\n"
        f"📱 Número: {OWNER_NUMBER}"
    )

def main():
    application = Application.builder().token(TOKEN).build()

    # COMANDOS
    application.add_handler(CommandHandler("tt", tt))
    application.add_handler(CommandHandler("owner", owner)) # <- NUEVO

    print("Bot iniciado...")
    application.run_polling()

if __name__ == "__main__":
    main()
