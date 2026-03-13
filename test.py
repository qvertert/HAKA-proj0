import yt_dlp

url = input("Введіть посилання на YouTube: ")

ydl_opts = {'quiet': True}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    try:
        info = ydl.extract_info(url, download=False)
        print(f"Тривалість: {info.get('duration')} секунд")
    except Exception as e:
        print(f"Помилка: {e}")