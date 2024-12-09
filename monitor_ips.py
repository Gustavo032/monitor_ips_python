import time
import threading
from ping3 import ping
import pygame
from tkinter import Tk, Label

# Configurações iniciais
ip_names = {
    "192.168.2.1": "Roteador",
    "192.168.2.121": "Celular Gustavo",
    "8.8.8.8": "Google DNS",
    "1.1.1.1": "Cloudflare DNS",
}
check_interval = 10  # Intervalo entre os testes (em segundos)
offline_threshold = 3  # Quantidade de testes falhos antes de marcar como offline

# Estado dos IPs
ip_status = {ip: {"fail_count": 0, "status": "online", "alerted": False} for ip in ip_names}

# Variável para armazenar o último IP que gerou o alerta
last_alert_ip = ""

# Função para tocar o som de alerta
def play_alert_sound():
    try:
        pygame.mixer.init()
        pygame.mixer.music.load("alert.mp3")  # Certifique-se de ter o arquivo 'alert.mp3'
        pygame.mixer.music.play()
    except Exception as e:
        print(f"Erro ao tocar som: {e}")

# Função para verificar o status dos IPs
def check_ip_status():
    global last_alert_ip  # Acessa a variável global para atualizar o último IP que gerou o alerta

    for ip in ip_names:
        try:
            response = ping(ip, timeout=2)
            # Considera qualquer falha como erro
            if response is None:
                ip_status[ip]["fail_count"] += 1
            else:
                ip_status[ip]["fail_count"] = 0
        except Exception as e:
            # Em caso de falha no ping (como Host inacessível)
            ip_status[ip]["fail_count"] += 1

        # Atualiza o status com base no contador de falhas
        if ip_status[ip]["fail_count"] >= offline_threshold:
            new_status = "offline"
        elif ip_status[ip]["fail_count"] > 0:
            new_status = "instável"
        else:
            new_status = "online"

        # Se o status mudou, atualiza e dispara o som, se necessário
        if ip_status[ip]["status"] != new_status:
            ip_status[ip]["status"] = new_status
            if new_status == "offline" and not ip_status[ip]["alerted"]:
                ip_status[ip]["alerted"] = True
                last_alert_ip = ip_names[ip]  # Atualiza o último IP que gerou o alerta
                threading.Thread(target=play_alert_sound).start()
            elif new_status != "offline":
                ip_status[ip]["alerted"] = False  # Reset alert when it goes back to online or unstable

# Função para atualizar a interface gráfica
def update_ui():
    for widget in root.winfo_children():
        widget.destroy()
    
    # Exibe o status de cada IP
    for ip, data in ip_status.items():
        color = {
            "online": "green",
            "instável": "blue",
            "offline": "red",
        }.get(data["status"], "gray")
        label = Label(root, text=f"{ip_names[ip]} ({ip}): {data['status']}", bg=color, fg="white", width=40)
        label.pack(pady=5)
    
    # Exibe o IP que gerou o último alerta
    last_alert_label = Label(root, text=f"Último alerta/queda: {last_alert_ip}", bg="gray", fg="white", width=40)
    last_alert_label.pack(pady=5)

# Loop principal
def main_loop():
    while True:
        check_ip_status()
        update_ui()
        time.sleep(check_interval)

# Configuração da interface gráfica
root = Tk()
root.title("Monitor de IPs")
root.geometry("350x175")
root.attributes('-topmost', True)

# Inicia o loop principal em um thread separado
threading.Thread(target=main_loop, daemon=True).start()

# Inicia o loop da interface gráfica
root.mainloop()
