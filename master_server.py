import socket
import threading

HOST = '0.0.0.0'
PORT = 4444

agents = {}  # Faol agentlar: {pc_name: socket}
admin_clients = []

def handle_client(conn, addr):
    try:
        # Client kimligini aniqlash (Agent yoki Admin)
        role_data = conn.recv(1024).decode('utf-8', errors='ignore')
        
        if role_data.startswith("AGENT|"):
            _, pc_name, os_info = role_data.split("|", 2)
            agents[pc_name] = {"socket": conn, "os": os_info, "addr": addr[0]}
            print(f"[+] Agent ulansin: {pc_name} ({addr[0]})")
            
            # Agent aloqada turishi uchun kutib turamiz
            while True:
                msg = conn.recv(1024)
                if not msg:
                    break
        elif role_data == "ADMIN_LIST":
            # Admin barcha faol agentlar ro'yxatini so'rayapti
            active_list = []
            for pcn, info in agents.items():
                active_list.append(f"{pcn}|{info['addr']}|{info['os']}")
            
            response = "___".join(active_list) if active_list else "EMPTY"
            conn.sendall(response.encode('utf-8'))
            conn.close()
    except:
        pass
    finally:
        # Uzilgan agentlarni bazadan o'chirish
        for pcn, info in list(agents.items()):
            if info["socket"] == conn:
                print(f"[-] Agent uzildi: {pcn}")
                del agents[pcn]
                conn.close()
                break

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(100)
    print(f"[*] Markaziy Server {PORT}-portda ishga tushdi...")
    
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()