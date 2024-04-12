import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO
import threading

# YouTube Data APIのAPIキーを設定（適切な値に置き換えてください）
API_KEY = "AIzaSyB8bwL7RWovJKLJU-CeiDEukdxDRjuSYRU"
SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

class YouTubeChatBot(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube検索チャットボット")
        self.geometry("800x600")
        self.chat_bubbles = []  # チャットバブルを追跡

        # チャット表示用のCanvasとScrollbarの作成
        self.canvas = tk.Canvas(self, borderwidth=0)
        self.frame = tk.Frame(self.canvas)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        # ScrollbarとCanvasの配置
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.frame, anchor="nw", 
                                  tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)

        # メッセージ入力欄と送信ボタンの配置
        self.entry = tk.Entry(self, width=100)
        self.entry.pack(side="left", expand=True, fill="x", padx=10, pady=10)
        self.entry.bind("<Return>", lambda event: self.on_send_click())

        self.send_button = tk.Button(self, text="送信", command=self.on_send_click)
        self.send_button.pack(side="right", padx=10, pady=10)

    def onFrameConfigure(self, event):
        '''スクロール領域をフレームのサイズに合わせる'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_send_click(self):
        user_message = self.entry.get()
        if user_message.strip() != "":
            self.display_message(user_message, "right")
            self.entry.delete(0, tk.END)
            threading.Thread(target=self.search_youtube, args=(user_message,)).start()

    def display_message(self, message, side):
        bubble = tk.Label(self.frame, text=message, wraplength=400,
                          bg="#DCF8C6" if side == "right" else "#ECECEC",
                          justify="right" if side == "right" else "left")
        bubble.pack(padx=10, pady=5, anchor="e" if side == "right" else "w")
        self.canvas.yview_moveto(1)
        self.chat_bubbles.append(bubble)

    def search_youtube(self, query):
        params = {
            'part': 'snippet',
            'q': query,
            'key': API_KEY,
            'maxResults': 5,
            'type': 'video'
        }
        response = requests.get(SEARCH_URL, params=params).json()
        self.display_search_results(response.get('items', []))

    def display_search_results(self, results):
        for result in results:
            title = result['snippet']['title']
            thumbnail_url = result['snippet']['thumbnails']['high']['url']
            video_id = result['id']['videoId']
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            self.display_video_result(title, thumbnail_url, video_url)

    def display_video_result(self, title, thumbnail_url, video_url):
        response = requests.get(thumbnail_url)
        img_data = BytesIO(response.content)
        img = Image.open(img_data)
        img.thumbnail((200, 200), Image.Resampling.LANCZOS)  # ここを修正
        photo = ImageTk.PhotoImage(img)

        thumbnail = tk.Label(self.frame, image=photo)
        thumbnail.image = photo
        thumbnail.pack()

        title_link = tk.Label(self.frame, text=title, fg="blue", cursor="hand2", wraplength=400)
        title_link.pack()
        title_link.bind("<Button-1>", lambda e, url=video_url: self.open_link(url))


    def open_link(self, url):
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("エラー", "リンクを開けませんでした。")

if __name__ == "__main__":
    app = YouTubeChatBot()
    app.mainloop()
