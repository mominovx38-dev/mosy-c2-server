import socket
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk

VPS_IP = '127.0.0.1'  # Server IP manzili
VPS_PORT = 4444

class AdminPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("MOSY C2 - Professional Boshqaruv Markazi")
        self.root.geometry("900x520")
        
        self.status_label = tk.Label(root, text="Serverga ulanishga tayyor", font=("Arial", 11, "bold"), fg="blue")
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

    def refresh_agents(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.agents_data.clear()
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((VPS_IP, VPS_PORT))
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
                        
                self.status_label.config(text=f"Topildi: {len(self.agents_data)} ta agent", fg="green")
            else:
                self.status_label.config(text="Tarmoqda faol agentlar yo'q", fg="red")
        except Exception as e:
            self.status_label.config(text=f"Serverga ulanish xatosi: {str(e)}", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminPanel(root)
    root.mainloop()