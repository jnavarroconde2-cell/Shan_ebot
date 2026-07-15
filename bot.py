import yt_dlp
import os

@bot.command()
async def tt(ctx, *, url: str):
    await ctx.send("⏳ Bajando TikTok sin marca de agua...")
    
    # Acepta todos los links: normal, lite, vm.tiktok
    if "tiktok" not in url:
        await ctx.send("❌ Manda un link de TikTok bro")
        return

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'tiktok.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'cookiefile': 'cookies.txt',  # opcional, por si es privado
        'merge_output_format': 'mp4',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # yt-dlp ya descarga sin marca de agua por defecto en TikTok
            
        await ctx.send(file=discord.File(filename))
        await ctx.send(f"✅ Listo! **{info.get('title', 'TikTok')}**")
        os.remove(filename)  # borra el archivo después de enviarlo
        
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")
