@bot.message_handler(commands=['playaudio'])
def playaudio(msg):
    query = msg.text.replace('/playaudio', '').strip()
    if not query:
        bot.send_message(msg.chat.id, "❌ Uso: /playaudio nombre de la canción\nEjemplo: /playaudio funk tonta")
        return
    
    wait_msg = bot.send_message(msg.chat.id, f"🔍 Buscando: {query}...")
    
    try:
        filename = f"{uuid.uuid4()}.mp3"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': filename,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch1',
            'nocheckcertificate': True,
            'extractor_retries': 3,
            'socket_timeout': 15,
            'geo_bypass': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            title = info['entries'][0]['title'] if 'entries' in info else info['title']
        
        bot.delete_message(msg.chat.id, wait_msg.message_id)
        bot.send_message(msg.chat.id, f"⬇️ Enviando: {title}")
        
        with open(filename, 'rb') as audio:
            bot.send_audio(msg.chat.id, audio=audio, title=title)
        os.remove(filename)
        
    except Exception as e:
        bot.delete_message(msg.chat.id, wait_msg.message_id)
        bot.send_message(msg.chat.id, f"❌ Error: YouTube bloqueó la descarga\nPrueba con otro nombre más corto")
        print("Error:", e)
