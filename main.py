from youtube_transcript_api import YouTubeTranscriptApi
import re
import os
from g4f.client import Client
from g4f.Provider import PollinationsAI
from g4f.cookies import set_cookies_dir, read_cookie_files

client = Client(provider=PollinationsAI)

cookies_dir = os.path.join(os.getcwd(), "har_and_cookies")
os.makedirs(cookies_dir, exist_ok=True)

set_cookies_dir(cookies_dir)
read_cookie_files()

with open("note.txt", "w", encoding="utf-8") as file:
    pass


def get_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    if match:
        return match.group(1)
    raise ValueError("id isnt identyfied")


url = input("Введіть посилання на YouTube відео: ")


try:
    video_id = get_video_id(url)

    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id, languages=["uk", "en"])

    for line in transcript:
        print(line.text)
        with open("note.txt", "a", encoding="utf-8") as file:
            file.write(line.text + "\n")

    with open("note.txt", "r", encoding="utf-8") as file:
        content = file.read()

    response = client.chat.completions.create(
        model="openai",
        messages=[
            {"role": "user", "content": "зроби міні-конспект по субтитрам з відео, без таблиць, тільки текст. надаю субтитри: "+ content}
        ]
    )

    print(response.choices[0].message.content)

except Exception as e:
    print("Помилка:", e)