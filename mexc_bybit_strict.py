import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import requests
import threading
import os

# --- ЦВЕТА ---
COLORS = {
    "bg": "#08080A",
    "sidebar": "#12121A",
    "accent": "#7C4DFF",
    "danger": "#FF5252",
    "success": "#69F0AE",
    "panel": "#1C1C26",
    "text_bright": "#FFFFFF",
    "text_dim": "#A0A0A0"
}

BLACKLIST_FILE = "blacklist.txt"

def format_price(price):
    try:
        p = float(price)
        if p == 0: return "0"
        if p < 0.0001:
            return f"{p:.10f}".rstrip('0').rstrip('.')
        if p < 1:
            return f"{p:.6f}".rstrip('0').rstrip('.')
        return f"{p:.4f}".rstrip('0').rstrip('.')
    except:
        return str(price)

class UltraHunter(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("OporaÐV V0.1 (dont realse)")
        self.geometry("1400x850")
        self.configure(fg_color=COLORS["bg"])

        self.ignored_coins = self.load_blacklist()
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.setup_table()

        self.setup_ui()
        self.attributes("-alpha", 0.0)
        self.fade_in()

    def fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            alpha += 0.05
            self.attributes("-alpha", alpha)
            self.after(20, self.fade_in)

    def load_blacklist(self):
        if os.path.exists(BLACKLIST_FILE):
            with open(BLACKLIST_FILE, "r") as f:
                return set(line.strip() for line in f if line.strip())
        return set()

    def setup_ui(self):
        self.sidebar = ctk.CTkFrame(self, width=300, fg_color=COLORS["sidebar"], corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.logo = ctk.CTkLabel(self.sidebar, text="OPORA ÐV x\nSYSTEM", 
                                 font=ctk.CTkFont(size=28, weight="bold"), text_color=COLORS["accent"])
        self.logo.pack(pady=(40, 40))

        self.opt_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.opt_frame.pack(fill="x", padx=25)

        ctk.CTkLabel(self.opt_frame, text="MIN VOLUME ($)", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["text_dim"]).pack(anchor="w")
        self.min_vol_entry = ctk.CTkEntry(self.opt_frame, height=35, fg_color=COLORS["panel"], border_color=COLORS["accent"], text_color="#FFFFFF")
        self.min_vol_entry.insert(0, "100")
        self.min_vol_entry.pack(fill="x", pady=(2, 15))

        ctk.CTkLabel(self.opt_frame, text="MAX VOLUME ($)", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["text_dim"]).pack(anchor="w")
        self.max_vol_entry = ctk.CTkEntry(self.opt_frame, height=35, fg_color=COLORS["panel"], border_color=COLORS["accent"], text_color="#FFFFFF")
        self.max_vol_entry.insert(0, "10000000")
        self.max_vol_entry.pack(fill="x", pady=(2, 15))

        check_font = ctk.CTkFont(size=13, weight="bold")
        
        self.check_both = ctk.CTkCheckBox(self.opt_frame, text="Только MEXC + Bybit (Без BIN)", font=check_font, 
                                          text_color=COLORS["text_bright"], fg_color=COLORS["accent"],
                                          command=self.logic_both)
        self.check_both.pack(anchor="w", pady=8)

        self.check_bin_m = ctk.CTkCheckBox(self.opt_frame, text="Binance+MEXC (No Bybit)", font=check_font, 
                                           text_color=COLORS["text_bright"], fg_color=COLORS["accent"],
                                           command=self.logic_bin)
        self.check_bin_m.pack(anchor="w", pady=8)

        self.btn_scan = self.create_btn("START RADAR", COLORS["accent"], self.start_scan_thread, "black")
        self.btn_hide = self.create_btn("BLACK BOX (BAN)", COLORS["danger"], self.add_selected_to_blacklist, "white")
        
        self.status_box = ctk.CTkFrame(self.sidebar, fg_color=COLORS["panel"], corner_radius=10)
        self.status_box.pack(fill="x", padx=20, pady=20, side="bottom")
        self.status_lbl = ctk.CTkLabel(self.status_box, text="READY", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["text_dim"])
        self.status_lbl.pack(pady=10)

    def logic_both(self):
        if self.check_both.get():
            self.check_bin_m.deselect()
            self.check_bin_m.configure(state="disabled")
        else:
            self.check_bin_m.configure(state="normal")

    def logic_bin(self):
        if self.check_bin_m.get():
            self.check_both.deselect()
            self.check_both.configure(state="disabled")
        else:
            self.check_both.configure(state="normal")

    def create_btn(self, text, color, cmd, t_color):
        btn = ctk.CTkButton(self.sidebar, text=text, fg_color=color, hover_color=color, text_color=t_color, height=50, font=ctk.CTkFont(size=14, weight="bold"), corner_radius=12, command=cmd)
        btn.pack(fill="x", padx=25, pady=10)
        return btn

    def setup_table(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=COLORS["bg"], foreground="white", fieldbackground=COLORS["bg"], borderwidth=0, font=('Segoe UI', 11), rowheight=45)
        style.configure("Treeview.Heading", background="#1A1A26", foreground=COLORS["accent"], relief="flat", font=('Segoe UI', 12, 'bold'))
        style.map("Treeview", background=[('selected', COLORS["accent"])], foreground=[('selected', 'black')])

        self.cols = ("Ticker", "Exchange", "Vol 24h", "Price", "Max Size (USDT)")
        self.tree = ttk.Treeview(self.main_area, columns=self.cols, show="headings", selectmode="extended")
        for col in self.cols:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, anchor="center", width=160)
        self.tree.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.tree.bind("<Double-1>", self.copy_to_clipboard)
        self.tree.bind("<B1-Motion>", self.on_drag_select)

    def on_drag_select(self, event):
        item = self.tree.identify_row(event.y)
        if item: self.tree.selection_add(item)

    def copy_to_clipboard(self, event):
        item = self.tree.selection()
        if item:
            ticker = self.tree.item(item[0])['values'][0]
            self.clipboard_clear()
            self.clipboard_append(ticker)
            self.status_lbl.configure(text=f"COPIED: {ticker}", text_color=COLORS["success"])

    def start_scan_thread(self):
        self.btn_scan.configure(state="disabled", text="SCANNING...")
        threading.Thread(target=self.run_logic, daemon=True).start()

    def run_logic(self):
        try:
            min_v = float(self.min_vol_entry.get() or 0)
            max_v = float(self.max_vol_entry.get() or 999999999)
            
            m_resp = requests.get("https://contract.mexc.com/api/v1/contract/ticker", timeout=10).json().get("data", [])
            b_resp_raw = requests.get("https://api.bybit.com/v5/market/tickers?category=linear", timeout=10).json()
            b_resp = b_resp_raw.get("result", {}).get("list", [])
            
            bin_set = set()
            try:
                bin_res = requests.get("https://fapi.binance.com/fapi/v1/exchangeInfo", timeout=5).json().get("symbols", [])
                bin_set.update([s["symbol"] for s in bin_res if s["symbol"].endswith("USDT")])
            except: pass

            risk_resp = requests.get("https://contract.mexc.com/api/v1/contract/detail", timeout=10).json().get("data", [])
            risk_map = {d["symbol"].replace("_", ""): float(d.get("baseLimit", 0)) for d in risk_resp}

            m_data = {i["symbol"].replace("_", ""): {"v": float(i.get("amount24", 0)), "p": float(i.get("lastPrice", 0))} for i in m_resp if i["symbol"].endswith("USDT")}
            b_data = {i["symbol"]: True for i in b_resp if i["symbol"].endswith("USDT")}

            results = []
            for sym, data in m_data.items():
                if sym in self.ignored_coins: continue
                
                in_bybit = sym in b_data
                in_binance = sym in bin_set
                
                # --- ИСКЛЮЧАЮЩАЯ ЛОГИКА ---
                if self.check_both.get():
                    # Только MEXC + Bybit и ОБЯЗАТЕЛЬНО НЕТ НА BINANCE
                    if not (in_bybit and not in_binance): continue
                
                if self.check_bin_m.get():
                    # Только Binance + MEXC и ОБЯЗАТЕЛЬНО НЕТ НА BYBIT
                    if not (in_binance and not in_bybit): continue

                total_v = data['v']
                if min_v <= total_v <= max_v:
                    price = data['p']
                    max_q = risk_map.get(sym, 0)
                    size_str = f"{price * max_q:,.0f}$" if max_q > 0 else "---"
                    
                    ex_label = "MEXC"
                    if in_binance: ex_label += "+BIN"
                    if in_bybit: ex_label += "+BYB"

                    results.append([sym, ex_label, f"{total_v:,.0f}$", format_price(price), size_str])

            results.sort(key=lambda x: float(x[2].replace('$', '').replace(',', '')), reverse=True)
            self.after(0, self.update_table, results)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.after(0, lambda: self.btn_scan.configure(state="normal", text="START RADAR"))

    def update_table(self, results):
        for i in self.tree.get_children(): self.tree.delete(i)
        for row in results: self.tree.insert("", "end", values=row)
        self.status_lbl.configure(text=f"FOUND: {len(results)}", text_color=COLORS["success"])

    def add_selected_to_blacklist(self):
        selected = self.tree.selection()
        for item in selected:
            sym = self.tree.item(item)['values'][0]
            self.ignored_coins.add(sym)
            with open(BLACKLIST_FILE, "a") as f: f.write(f"{sym}\n")
            self.tree.delete(item)

if __name__ == "__main__":
    app = UltraHunter()
    app.mainloop()