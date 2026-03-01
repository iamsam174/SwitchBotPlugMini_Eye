import tkinter as tk
from tkinter import ttk, messagebox
import threading
import cv2
from PIL import Image, ImageTk
import winsound
import sys
import asyncio
import traceback
from bleak import BleakClient, BleakScanner

# SwitchBot PlugMini 制御用サービスUUID
UUID_VAL = "cba20002-224d-11e6-9fb8-0002a5d5c51b"

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("SwitchBot PlugMini BT Control App")
        
        # 画面設定
        self.root.state('zoomed')
        self.root.configure(bg="#f0f0f0") # 背景色を明るいグレーに
        
        # キーバインドの設定
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))
        self.root.bind("<F11>", self.toggle_fullscreen)
        # モード切替ショートカット
        self.root.bind("1", lambda e: self.mode.set(1))
        self.root.bind("2", lambda e: self.mode.set(2))
        self.root.bind("3", lambda e: self.mode.set(3))
        # --- 矢印キーでのタイマー変更バインド ---
        self.root.bind("<Left>", self.decrease_timer)
        self.root.bind("<Right>", self.increase_timer)
        
        self.target_mac = None
        self.client = None
        self.is_running = False
        self.cap = None
        self.loop = None
        self.sound = tk.BooleanVar(value=True)
        self.mode = tk.IntVar(value=1)
        self.found_devs = []

        self.size_var = tk.StringVar(value="中")
        self.sizes = {"特大": (1000, 563), "大": (800, 450), "中": (600, 338), "小": (400, 225)}

        try:
            self.setup_ui()
            self.root.after(100, self.update_camera)
            self.root.after(200, self.start_thread)
        except Exception as e:
            messagebox.showerror("UI起動エラー", traceback.format_exc())
            sys.exit()

    # タイマー加減算用メソッドの追加
    def decrease_timer(self, event=None):
        current = self.sc_t.get()
        if current > 1:
            self.sc_t.set(current - 1)

    def increase_timer(self, event=None):
        current = self.sc_t.get()
        if current < 180:
            self.sc_t.set(current + 1)

    def toggle_fullscreen(self, event=None):
        is_full = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not is_full)

    def setup_ui(self):
        f_b = ("Yu Gothic", 12, "bold")
        
        self.header = tk.Frame(self.root, bg="#f0f0f0")
        self.header.pack(side="top", fill="x", padx=40, pady=5)

        # 1. 設定セクション
        adm = tk.LabelFrame(self.header, text=" 設定 ", font=f_b, bg="white", fg="#333", padx=15, pady=10)
        adm.pack(fill="x", pady=2)

        r1 = tk.Frame(adm, bg="white")
        r1.pack(fill="x", pady=2)
        tk.Button(r1, text="🔍 SwitchBotプラグミニを探査", command=self.scan, font=f_b, bg="#4CAF50", fg="white", padx=10).pack(side="left", padx=5)
        self.lbl_s = tk.Label(r1, text="スキャン待機中", font=f_b, bg="white")
        self.lbl_s.pack(side="left", padx=15)

        tk.Label(r1, text="ペアリング:", font=f_b, bg="white").pack(side="left")
        self.cb_dev = ttk.Combobox(r1, state="readonly", width=27, font=("Consolas", 10))
        self.cb_dev.pack(side="left", padx=5)
        tk.Button(r1, text="接続", command=self.conn, font=f_b, bg="#2196F3", fg="white", padx=10).pack(side="left", padx=5)

        tk.Label(r1, text=" | カメラ:", font=f_b, bg="white").pack(side="left", padx=(15,0))
        self.cb_cam = ttk.Combobox(r1, state="readonly", width=10, font=f_b)
        self.cb_cam['values'] = ("カメラ1", "カメラ2", "カメラなし")
        self.cb_cam.current(2)
        self.cb_cam.pack(side="left", padx=5)
        self.cb_cam.bind("<<ComboboxSelected>>", self.cam_chg)

        # タイマー設定の配置
        tk.Label(r1, text=" | タイマー設定 (1～180秒):", font=f_b, bg="white").pack(side="left", padx=(15,0))
        self.sc_t = tk.Scale(r1, from_=1, to=180, orient="horizontal", length=300, bg="white", highlightthickness=0, font=f_b)
        self.sc_t.set(5)
        self.sc_t.pack(side="left", padx=10)

        r2 = tk.Frame(adm, bg="white")
        r2.pack(fill="x", pady=(10, 0))
        tk.Checkbutton(r2, text="操作音を有効にする", variable=self.sound, font=f_b, bg="white").pack(side="left", padx=10)
        tk.Label(r2, text=" | 動作モード:", font=f_b, bg="white").pack(side="left", padx=(10,0))
        tk.Radiobutton(r2, text="①クリック/注視でタイマー実行", variable=self.mode, value=1, font=f_b, bg="white").pack(side="left", padx=5)
        tk.Radiobutton(r2, text="②マウスオーバーでタイマー実行", variable=self.mode, value=2, font=f_b, bg="white").pack(side="left", padx=5)
        tk.Radiobutton(r2, text="③マウスポインターがボタン内にある間ON", variable=self.mode, value=3, font=f_b, bg="white").pack(side="left", padx=5)

        # ボタンサイズ設定の配置
        tk.Label(r2, text=" | ボタンサイズ:", font=f_b, bg="white").pack(side="left", padx=(15,0))
        self.cb_size = ttk.Combobox(r2, textvariable=self.size_var, state="readonly", width=5, font=f_b)
        self.cb_size['values'] = ("特大", "大", "中", "小")
        self.cb_size.pack(side="left", padx=5)
        self.cb_size.bind("<<ComboboxSelected>>", self.resize_canvas)

        # 操作エリア
        self.canvas_container = tk.Frame(self.root, bg="#f0f0f0")
        self.canvas_container.place(relx=0.5, rely=0.6, anchor="center")

        w, h = self.sizes[self.size_var.get()]
        self.cv = tk.Canvas(self.canvas_container, width=w, height=h, bg="#b2e2a2", highlightthickness=10, highlightbackground="#689f38")
        self.cv.pack()
        self.id_i = self.cv.create_image(w//2, h//2, anchor="center")
        self.id_t = self.cv.create_text(w//2, h//2, text="スイッチON", font=("Yu Gothic", 48, "bold"), fill="#333333", anchor="center")

        self.cv.bind("<Button-1>", self.on_start_drag)
        self.cv.bind("<B1-Motion>", self.on_drag)
        self.cv.bind("<ButtonRelease-1>", self.on_stop_drag)
        
        self.cv.bind("<Enter>", lambda e: self.ent())
        self.cv.bind("<Leave>", lambda e: self.lev())

        # ヘルプテキストの更新
        self.lbl_esc = tk.Label(self.root, text="※スイッチONボタンはマウスドラッグで移動可 / [F11]キー:全画面表示切替 / [1][2][3]キー:動作モード切替 / [←][→]キー:タイマー秒数設定", font=f_b, bg="#f0f0f0", fg="#555")
        self.lbl_esc.pack(side="bottom", pady=10)

    def on_start_drag(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self._is_dragging = False

    def on_drag(self, event):
        if abs(event.x - self._drag_start_x) > 5 or abs(event.y - self._drag_start_y) > 5:
            self._is_dragging = True
            x = self.canvas_container.winfo_x() + (event.x - self._drag_start_x)
            y = self.canvas_container.pady = self.canvas_container.winfo_y() + (event.y - self._drag_start_y)
            self.canvas_container.place(x=x, y=y, anchor="nw", relx=0, rely=0)

    def on_stop_drag(self, event):
        if not getattr(self, '_is_dragging', False):
            self.act()
        self._is_dragging = False

    def resize_canvas(self, event=None):
        w, h = self.sizes[self.size_var.get()]
        self.cv.config(width=w, height=h)
        self.cv.coords(self.id_i, w//2, h//2)
        s = self.cb_cam.get()
        if s == "カメラなし":
            self.cv.coords(self.id_t, w//2, h//2)
            self.cv.itemconfig(self.id_t, font=("Yu Gothic", 48, "bold"))
        else:
            self.cv.coords(self.id_t, w//2, 40)
            self.cv.itemconfig(self.id_t, font=("Yu Gothic", 28, "bold"))

    def cam_chg(self, e=None):
        w, h = self.sizes[self.size_var.get()]
        s = self.cb_cam.get()
        if self.cap: self.cap.release()
        if s == "カメラなし":
            self.cap = None
            self.cv.itemconfig(self.id_i, image="")
            self.cv.coords(self.id_t, w//2, h//2)
            self.cv.itemconfig(self.id_t, font=("Yu Gothic", 48, "bold"))
        else:
            self.cv.coords(self.id_t, w//2, 40)
            self.cv.itemconfig(self.id_t, font=("Yu Gothic", 28, "bold"))
            idx = 0 if s == "カメラ1" else 1
            self.cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)

    def update_camera(self):
        try:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    w, h = self.sizes[self.size_var.get()]
                    frame = cv2.resize(cv2.flip(frame, 1), (w, h))
                    self.tk_img = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                    self.cv.itemconfig(self.id_i, image=self.tk_img)
        except Exception: pass
        self.root.after(15, self.update_camera)

    def start_thread(self):
        def run():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.create_task(self.keep())
            self.loop.run_forever()
        threading.Thread(target=run, daemon=True).start()

    async def keep(self):
        while True:
            await asyncio.sleep(2)
            if self.target_mac and (self.client is None or not self.client.is_connected):
                self.up_s("接続中...", "red")
                try:
                    self.client = BleakClient(self.target_mac); await self.client.connect()
                    self.up_s("接続完了", "green")
                    self.play_sound()
                except Exception: self.up_s("再試行中...", "red")

    def up_s(self, t, c):
        if self.root: self.root.after(0, lambda: self.lbl_s.config(text=t, fg=c))

    def scan(self):
        if not self.loop: return
        self.up_s("スキャン中...", "blue")
        async def do():
            try:
                ds = await BleakScanner.discover(timeout=5.0)
                nms, found = [], []
                for d in ds:
                    n = d.name if d.name else "Unknown"
                    found.append(d.address); nms.append(f"{n} ({d.address})")
                self.root.after(0, lambda: self.update_dev_list(nms, found))
                self.up_s("完了", "black")
                self.play_sound()
            except Exception: pass
        asyncio.run_coroutine_threadsafe(do(), self.loop)

    def update_dev_list(self, nms, found):
        self.cb_dev.config(values=nms); self.found_devs = found

    def conn(self):
        i = self.cb_dev.current()
        if i >= 0: self.target_mac = self.found_devs[i]

    def send(self, on):
        if not self.client or not self.client.is_connected: return
        v = b'\x57\x01\x01' if on else b'\x57\x01\x00'
        asyncio.run_coroutine_threadsafe(self.client.write_gatt_char(UUID_VAL, v), self.loop)

    def act(self):
        if self.mode.get() == 1: self.run_t()
    def ent(self):
        if self.mode.get() == 2: self.run_t()
        elif self.mode.get() == 3:
            if not self.is_running:
                self.is_running = True
                self.play_sound()
            self.send(True); self.cv.itemconfig(self.id_t, text="実行中", fill="#FFFFFF")
            self.cv.config(highlightbackground="#F44336", bg="#F44336")
    def lev(self):
        if self.mode.get() == 3:
            if self.is_running:
                self.is_running = False
                self.play_sound()
            self.send(False); self.cv.itemconfig(self.id_t, text="スイッチON", fill="#333333")
            self.cv.config(highlightbackground="#689f38", bg="#b2e2a2")

    def run_t(self):
        if self.is_running: return
        self.is_running = True; self.send(True)
        self.play_sound()
        self.remaining = self.sc_t.get()
        self.cv.config(highlightbackground="#F44336", bg="#F44336")
        self.cv.itemconfig(self.id_t, fill="#FFFFFF")
        self.update_timer()

    def update_timer(self):
        if self.remaining > 0:
            self.cv.itemconfig(self.id_t, text=f"実行中 {self.remaining}秒")
            self.remaining -= 1; self.root.after(1000, self.update_timer)
        else: self.fin_t()

    def fin_t(self):
        self.play_sound()
        self.send(False)
        self.cv.itemconfig(self.id_t, text="スイッチON", fill="#333333")
        self.cv.config(highlightbackground="#689f38", bg="#b2e2a2")
        self.is_running = False

    def play_sound(self):
        if self.sound.get():
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)

if __name__ == "__main__":
    r = tk.Tk(); a = App(r); r.mainloop()