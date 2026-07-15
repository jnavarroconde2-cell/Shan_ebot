@bot.message_handler(commands=['ttmp3'])
def ttmp3(message):
    try:
        url = message.text.split(" ", 1)[1]
    except:
        bot.reply_to(message, "❌ Manda el link así: /ttmp3 https://vm.tiktok.com/...")
        return

    bot.reply_to(message, "⏳ Extrayendo audio...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'tiktok_audio.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'postprocessors': [{ # Esto convierte a MP3
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            filename = filename.rsplit(".", 1)[0] + ".mp3" # cambia la extensión a mp3

        with open(filename, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, title=info.get('title', 'TikTok Audio'))

        os.remove(filename)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")
