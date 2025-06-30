import tkinter as tk
from tkinter import ttk
import time
import random
import threading
import requests
import json
from datetime import datetime

# === KONFIGURASI WARNA ===
COLOR_BG = "#0d1117"
COLOR_FRAME = "#161b22"
COLOR_TEXT = "#c9d1d9"
COLOR_TEXT_SECONDARY = "#8b949e"
COLOR_BORDER = "#30363d"

# Status Colors
COLOR_SAFE = "#2fbf71"
COLOR_WARNING = "#fca61f"
COLOR_DANGER = "#f93e3e"
COLOR_CRITICAL = "#e40e0e"

# Sensor Colors
COLOR_GAS = "#3b82f6"
COLOR_TEMP = "#ef4444"
COLOR_HUMIDITY = "#a855f7"
COLOR_FLAME = "#ff6b35"

class SensorCard(tk.Frame):
    """Kartu sensor yang simpel dan stabil"""
    def __init__(self, parent, title, unit, icon, color, threshold=None):
        super().__init__(parent, bg=COLOR_FRAME, relief="solid", bd=1)
        self.title = title
        self.unit = unit
        self.color = color
        self.threshold = threshold
        self.current_value = 0
        self.is_danger = False
        
        self.pack_propagate(False)
        self.configure(width=280, height=140)
        
        # Header
        header = tk.Frame(self, bg=COLOR_FRAME)
        header.pack(fill="x", padx=15, pady=(10, 0))
        
        tk.Label(header, text=icon, font=("Segoe UI Emoji", 16), 
                bg=COLOR_FRAME, fg=color).pack(side="left")
        tk.Label(header, text=title, font=("Segoe UI", 10, "bold"), 
                bg=COLOR_FRAME, fg=COLOR_TEXT_SECONDARY).pack(side="left", padx=(8, 0))
        
        # Status indicator
        self.status_dot = tk.Label(header, text="●", font=("Arial", 12), 
                                  bg=COLOR_FRAME, fg=COLOR_SAFE)
        self.status_dot.pack(side="right")
        
        # Value display
        value_frame = tk.Frame(self, bg=COLOR_FRAME)
        value_frame.pack(expand=True, fill="both", padx=15)
        
        self.value_label = tk.Label(value_frame, text="--", 
                                   font=("Segoe UI Light", 32), 
                                   bg=COLOR_FRAME, fg=COLOR_TEXT)
        self.value_label.pack(side="left", anchor="sw")
        
        self.unit_label = tk.Label(value_frame, text=unit, 
                                  font=("Segoe UI", 12), 
                                  bg=COLOR_FRAME, fg=color)
        self.unit_label.pack(side="left", anchor="sw", padx=(5, 0))
        
        # Status text
        self.status_label = tk.Label(self, text="Normal", 
                                    font=("Segoe UI", 9), 
                                    bg=COLOR_FRAME, fg=COLOR_TEXT_SECONDARY)
        self.status_label.pack(pady=(0, 10))
        
        # Progress bar (jika ada threshold)
        if threshold:
            self.progress_frame = tk.Frame(self, bg=COLOR_FRAME, height=4)
            self.progress_frame.pack(fill="x", padx=15, pady=(0, 10))
            self.progress_frame.pack_propagate(False)
            
            self.progress_bg = tk.Frame(self.progress_frame, bg=COLOR_BORDER, height=4)
            self.progress_bg.pack(fill="x")
            
            self.progress_bar = tk.Frame(self.progress_bg, bg=color, height=4)
            self.progress_bar.place(x=0, y=0, relwidth=0, relheight=1)
    
    def update_value(self, value, status_text="Normal"):
        """Update nilai sensor dengan deteksi bahaya otomatis"""
        self.current_value = value
        
        # Tentukan status bahaya
        if self.threshold and value > self.threshold:
            self.is_danger = True
            status_text = "TINGGI"
        elif self.title == "DETEKSI API" and value > 0:
            self.is_danger = True
            status_text = "TERDETEKSI"
        else:
            self.is_danger = False
            status_text = "Normal"
        
        # Update tampilan nilai
        if self.title == "DETEKSI API":
            self.value_label.config(text="YA" if value > 0 else "TIDAK")
        else:
            self.value_label.config(text=f"{value:.1f}" if isinstance(value, float) else str(value))
        
        # Update warna berdasarkan status
        if self.is_danger:
            self.configure(bd=2, highlightbackground=COLOR_DANGER)
            self.status_dot.config(fg=COLOR_DANGER)
            self.status_label.config(fg=COLOR_DANGER)
            self.value_label.config(fg=COLOR_DANGER)
        else:
            self.configure(bd=1, highlightbackground=COLOR_BORDER)
            self.status_dot.config(fg=COLOR_SAFE)
            self.status_label.config(fg=COLOR_TEXT_SECONDARY)
            self.value_label.config(fg=COLOR_TEXT)
        
        self.status_label.config(text=status_text)
        
        # Update progress bar
        if hasattr(self, 'progress_bar') and self.threshold:
            progress = min(value / self.threshold, 1.0)
            self.progress_bar.place(relwidth=progress)
            if self.is_danger:
                self.progress_bar.config(bg=COLOR_DANGER)
            else:
                self.progress_bar.config(bg=self.color)

class StatusPanel(tk.Frame):
    """Panel status utama yang simpel"""
    def __init__(self, parent):
        super().__init__(parent, bg=COLOR_FRAME)
        
        # Header
        header = tk.Frame(self, bg=COLOR_FRAME)
        header.pack(fill="x", padx=20, pady=20)
        
        tk.Label(header, text="🛡️", font=("Segoe UI Emoji", 32), 
                bg=COLOR_FRAME, fg=COLOR_SAFE).pack()
        
        self.status_title = tk.Label(header, text="SISTEM AMAN", 
                                    font=("Segoe UI", 18, "bold"), 
                                    bg=COLOR_FRAME, fg=COLOR_TEXT)
        self.status_title.pack(pady=(10, 5))
        
        self.status_detail = tk.Label(header, text="Semua sensor normal", 
                                     font=("Segoe UI", 10), 
                                     bg=COLOR_FRAME, fg=COLOR_TEXT_SECONDARY)
        self.status_detail.pack()
        
        # Fuzzy Logic Result
        fuzzy_frame = tk.Frame(self, bg=COLOR_FRAME)
        fuzzy_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(fuzzy_frame, text="NILAI FUZZY LOGIC", 
                font=("Segoe UI", 10, "bold"), 
                bg=COLOR_FRAME, fg=COLOR_TEXT_SECONDARY).pack()
        
        self.fuzzy_value = tk.Label(fuzzy_frame, text="0.0", 
                                   font=("Segoe UI Light", 24), 
                                   bg=COLOR_FRAME, fg=COLOR_TEXT)
        self.fuzzy_value.pack(pady=(5, 0))
        
        # Log area
        log_frame = tk.Frame(self, bg=COLOR_FRAME)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(20, 20))
        
        tk.Label(log_frame, text="LOG SISTEM", 
                font=("Segoe UI", 10, "bold"), 
                bg=COLOR_FRAME, fg=COLOR_TEXT_SECONDARY).pack(anchor="w")
        
        # Scrollable log
        log_scroll_frame = tk.Frame(log_frame, bg=COLOR_BG)
        log_scroll_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        self.log_text = tk.Text(log_scroll_frame, bg=COLOR_BG, fg=COLOR_TEXT_SECONDARY,
                               font=("Consolas", 9), height=12, wrap="word", bd=0)
        
        scrollbar = ttk.Scrollbar(log_scroll_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.add_log("Sistem diinisialisasi")
    
    def update_status(self, is_danger, fuzzy_value, status_text):
        """Update status utama sistem"""
        if is_danger:
            self.status_title.config(text="⚠️ PERINGATAN", fg=COLOR_DANGER)
            self.status_detail.config(text=status_text, fg=COLOR_DANGER)
        else:
            self.status_title.config(text="🛡️ SISTEM AMAN", fg=COLOR_SAFE)
            self.status_detail.config(text="Semua sensor normal", fg=COLOR_TEXT_SECONDARY)
        
        self.fuzzy_value.config(text=f"{fuzzy_value:.1f}")
        
        # Update warna fuzzy value
        if fuzzy_value >= 80:
            self.fuzzy_value.config(fg=COLOR_CRITICAL)
        elif fuzzy_value >= 60:
            self.fuzzy_value.config(fg=COLOR_DANGER)
        elif fuzzy_value >= 40:
            self.fuzzy_value.config(fg=COLOR_WARNING)
        else:
            self.fuzzy_value.config(fg=COLOR_SAFE)
    
    def add_log(self, message, level="info"):
        """Tambahkan log baru"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert("1.0", log_entry)
        
        # Warna berdasarkan level
        if level == "danger":
            self.log_text.tag_add("danger", "1.0", "1.end")
            self.log_text.tag_config("danger", foreground=COLOR_DANGER)
        elif level == "warning":
            self.log_text.tag_add("warning", "1.0", "1.end")
            self.log_text.tag_config("warning", foreground=COLOR_WARNING)
        
        # Batasi jumlah log (hapus yang lama)
        lines = self.log_text.get("1.0", "end-1c").split("\n")
        if len(lines) > 50:
            self.log_text.delete(f"{len(lines)-50}.0", "end")

class SimpleGraph(tk.Frame):
    """Grafik sederhana menggunakan canvas"""
    def __init__(self, parent):
        super().__init__(parent, bg=COLOR_FRAME)
        
        # Header
        tk.Label(self, text="GRAFIK SENSOR (Real-time)", 
                font=("Segoe UI", 12, "bold"), 
                bg=COLOR_FRAME, fg=COLOR_TEXT).pack(pady=(10, 5))
        
        # Canvas untuk grafik
        self.canvas = tk.Canvas(self, width=500, height=200, bg=COLOR_BG, highlightthickness=0)
        self.canvas.pack(padx=20, pady=(0, 20))
        
        # Data points (menyimpan 50 titik terakhir)
        self.data_points = []
        self.max_points = 50
        
        # Legenda
        legend_frame = tk.Frame(self, bg=COLOR_FRAME)
        legend_frame.pack()
        
        tk.Label(legend_frame, text="● Gas", fg=COLOR_GAS, bg=COLOR_FRAME, 
                font=("Segoe UI", 9)).pack(side="left", padx=10)
        tk.Label(legend_frame, text="● Suhu", fg=COLOR_TEMP, bg=COLOR_FRAME, 
                font=("Segoe UI", 9)).pack(side="left", padx=10)
        tk.Label(legend_frame, text="● Kelembapan", fg=COLOR_HUMIDITY, bg=COLOR_FRAME, 
                font=("Segoe UI", 9)).pack(side="left", padx=10)
    
    def update_graph(self, gas, temp, humidity):
        """Update grafik dengan data baru"""
        # Tambah data baru
        self.data_points.append({"gas": gas, "temp": temp, "humidity": humidity})
        
        # Batasi jumlah data
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)
        
        # Gambar ulang grafik
        self.redraw_graph()
    
    def redraw_graph(self):
        """Gambar ulang grafik"""
        self.canvas.delete("all")
        
        if len(self.data_points) < 2:
            return
        
        # Dimensi canvas
        width = 500
        height = 200
        margin = 20
        
        # Hitung nilai min/max untuk scaling
        gas_values = [d["gas"] for d in self.data_points]
        temp_values = [d["temp"] for d in self.data_points]
        humidity_values = [d["humidity"] for d in self.data_points]
        
        max_gas = max(gas_values) if gas_values else 1
        max_temp = max(temp_values) if temp_values else 1
        max_humidity = max(humidity_values) if humidity_values else 1
        
        # Gambar grid
        for i in range(0, width, 50):
            self.canvas.create_line(i, margin, i, height-margin, 
                                  fill=COLOR_BORDER, width=1)
        for i in range(margin, height-margin, 30):
            self.canvas.create_line(margin, i, width-margin, i, 
                                  fill=COLOR_BORDER, width=1)
        
        # Gambar garis data
        points_count = len(self.data_points)
        x_step = (width - 2*margin) / max(points_count-1, 1)
        
        # Gas line
        if max_gas > 0:
            gas_points = []
            for i, data in enumerate(self.data_points):
                x = margin + i * x_step
                y = height - margin - (data["gas"] / max_gas) * (height - 2*margin)
                gas_points.extend([x, y])
            
            if len(gas_points) >= 4:
                self.canvas.create_line(gas_points, fill=COLOR_GAS, width=2, smooth=True)
        
        # Temperature line
        if max_temp > 0:
            temp_points = []
            for i, data in enumerate(self.data_points):
                x = margin + i * x_step
                y = height - margin - (data["temp"] / max_temp) * (height - 2*margin)
                temp_points.extend([x, y])
            
            if len(temp_points) >= 4:
                self.canvas.create_line(temp_points, fill=COLOR_TEMP, width=2, smooth=True)
        
        # Humidity line
        if max_humidity > 0:
            humidity_points = []
            for i, data in enumerate(self.data_points):
                x = margin + i * x_step
                y = height - margin - (data["humidity"] / max_humidity) * (height - 2*margin)
                humidity_points.extend([x, y])
            
            if len(humidity_points) >= 4:
                self.canvas.create_line(humidity_points, fill=COLOR_HUMIDITY, width=2, smooth=True)

class FireDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔥 Fire Detection System - Stable Version")
        self.root.configure(bg=COLOR_BG)
        self.root.geometry("1400x800")
        
        # Variabel untuk tracking status
        self.last_danger_status = False
        self.server_url = "http://192.168.134.160:8080/api/sensor"
        
        self.create_ui()
        self.start_simulation()  # Ganti dengan start_server_monitoring() jika ingin real data
    
    def create_ui(self):
        """Buat interface pengguna"""
        # Main container
        main_frame = tk.Frame(self.root, bg=COLOR_BG)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Layout: Left panel (status), Right panel (sensors + graph)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)
        
        # Left Panel - Status
        self.status_panel = StatusPanel(main_frame)
        self.status_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Right Panel
        right_panel = tk.Frame(main_frame, bg=COLOR_BG)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.rowconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        right_panel.columnconfigure(0, weight=1)
        
        # Sensor cards
        sensors_frame = tk.Frame(right_panel, bg=COLOR_BG)
        sensors_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        # Grid 2x2 untuk sensor cards
        sensors_frame.columnconfigure(0, weight=1)
        sensors_frame.columnconfigure(1, weight=1)
        sensors_frame.rowconfigure(0, weight=1)
        sensors_frame.rowconfigure(1, weight=1)
        
        # Sensor Cards (sesuai dengan data Arduino)
        self.gas_card = SensorCard(sensors_frame, "LEVEL GAS", "PPM", "🌫️", COLOR_GAS, threshold=2000)
        self.gas_card.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.temp_card = SensorCard(sensors_frame, "SUHU", "°C", "🌡️", COLOR_TEMP, threshold=35)
        self.temp_card.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        self.humidity_card = SensorCard(sensors_frame, "KELEMBAPAN", "%", "💧", COLOR_HUMIDITY)
        self.humidity_card.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        self.flame_card = SensorCard(sensors_frame, "DETEKSI API", "", "🔥", COLOR_FLAME)
        self.flame_card.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        # Graph
        self.graph = SimpleGraph(right_panel)
        self.graph.grid(row=1, column=0, sticky="nsew")
    
    def update_display(self, data):
        """Update tampilan dengan data terbaru"""
        # Update sensor cards
        self.gas_card.update_value(data["gas"])
        self.temp_card.update_value(data["suhu"])
        self.humidity_card.update_value(data["kelembapan"])
        self.flame_card.update_value(1 if data["api"] else 0)
        
        # Update graph
        self.graph.update_graph(data["gas"], data["suhu"], data["kelembapan"])
        
        # Tentukan status bahaya
        fuzzy_value = data.get("nilai_fuzzy", 0)
        status_bahaya = data.get("status_bahaya", "Aman")
        
        # Cek kondisi bahaya
        is_danger = (data["gas"] > 2000 or data["suhu"] > 35 or data["api"] or fuzzy_value >= 40)
        
        # Update status panel
        self.status_panel.update_status(is_danger, fuzzy_value, status_bahaya)
        
        # Log perubahan status
        if is_danger and not self.last_danger_status:
            reasons = []
            if data["gas"] > 2000:
                reasons.append("Gas tinggi")
            if data["suhu"] > 35:
                reasons.append("Suhu tinggi")
            if data["api"]:
                reasons.append("Api terdeteksi")
            
            self.status_panel.add_log(f"PERINGATAN: {', '.join(reasons)}", "danger")
        elif not is_danger and self.last_danger_status:
            self.status_panel.add_log("Kondisi kembali normal", "info")
        
        self.last_danger_status = is_danger
    
    def start_simulation(self):
        """Mulai simulasi data (untuk testing)"""
        def simulate():
            # Simulasi data sensor
            gas = random.randint(800, 1500)
            temp = random.uniform(25, 32)
            humidity = random.uniform(40, 70)
            flame = False
            
            # Simulasi kondisi bahaya sesekali
            if random.random() < 0.1:  # 10% kemungkinan
                scenario = random.choice(['gas', 'temp', 'flame'])
                if scenario == 'gas':
                    gas = random.randint(2500, 3500)
                elif scenario == 'temp':
                    temp = random.uniform(40, 50)
                elif scenario == 'flame':
                    flame = True
            
            # Hitung fuzzy logic sederhana
            fuzzy_value = 0
            if gas > 2000:
                fuzzy_value += 30
            if temp > 35:
                fuzzy_value += 25
            if flame:
                fuzzy_value += 45
            
            # Status bahaya
            if fuzzy_value >= 80:
                status = "Bahaya Sangat Tinggi"
            elif fuzzy_value >= 60:
                status = "Bahaya Tinggi"
            elif fuzzy_value >= 40:
                status = "Bahaya Sedang"
            elif fuzzy_value >= 25:
                status = "Waspada"
            else:
                status = "Aman"
            
            data = {
                "gas": gas,
                "suhu": temp,
                "kelembapan": humidity,
                "api": flame,
                "nilai_fuzzy": fuzzy_value,
                "status_bahaya": status
            }
            
            # Update UI di main thread
            self.root.after(0, lambda: self.update_display(data))
            
            # Schedule next update
            threading.Timer(2.0, simulate).start()
        
        # Mulai simulasi
        simulate()
    
    def start_server_monitoring(self):
        """Mulai monitoring server untuk data real (gunakan ini untuk koneksi real ke Arduino)"""
        def monitor():
            try:
                # Coba ambil data dari server
                response = requests.get(f"{self.server_url}/latest", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    self.root.after(0, lambda: self.update_display(data))
                else:
                    self.root.after(0, lambda: self.status_panel.add_log("Koneksi server gagal", "warning"))
            except Exception as e:
                self.root.after(0, lambda: self.status_panel.add_log(f"Error: {str(e)}", "warning"))
            
            # Schedule next check
            threading.Timer(3.0, monitor).start()
        
        # Mulai monitoring
        monitor()

if __name__ == "__main__":
    root = tk.Tk()
    app = FireDetectionApp(root)
    root.mainloop()