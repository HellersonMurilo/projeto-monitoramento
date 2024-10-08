import time
from pynput import mouse, keyboard
import csv
import os
import smtplib
from email.mime.text import MIMEText
import getpass
from datetime import datetime

# Tempo máximo de inatividade (em segundos)
tempo_max_inatividade = 30  # 30 segundos

# Arquivo para salvar o log de inatividade
arquivo_log = "atividade.csv"
# Arquivo para salvar a última data registrada
arquivo_data = "ultima_data.txt"

# Última vez que houve interação com o mouse ou teclado
ultimo_evento = time.time()
atividade_iniciada = False  # Indica se a atividade foi registrada

# Captura o usuário local
usuario_local = getpass.getuser()

# Funções para monitorar mouse e teclado
def on_move(x, y):
    registrar_evento()

def on_click(x, y, button, pressed):
    registrar_evento()

def on_scroll(x, y, dx, dy):
    registrar_evento()

def on_key_press(key):
    registrar_evento()

def registrar_evento():
    global ultimo_evento, atividade_iniciada
    tempo_atual = time.time()
    if not atividade_iniciada:  # Se a atividade ainda não foi registrada
        registrar_inicio(tempo_atual)
        atividade_iniciada = True
    ultimo_evento = tempo_atual  # Atualiza o último evento

# Função para registrar o início de uma atividade
def registrar_inicio(tempo_atual):
    with open(arquivo_log, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(tempo_atual)),
                "Início",
                "",
            ]
        )

# Função para registrar o fim de uma atividade
def registrar_fim(tempo_atual):
    with open(arquivo_log, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(tempo_atual)), "Fim", ""]
        )

# Função para enviar o relatório por e-mail
def enviar_relatorio_email(ultimo_dia):
    remetente = "calabianquimurilo328@gmail.com"
    destinatario = "hellerson.souza@libbs.com.br"
    assunto = f"Relatório de Atividades do Dia - {usuario_local}"

    # Lê o conteúdo do arquivo CSV
    with open(arquivo_log, "r") as file:
        conteudo = file.read()

    corpo = f"Relatório de atividades de {usuario_local} no dia {ultimo_dia}:\n\n{conteudo}"

    msg = MIMEText(corpo)
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = destinatario

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()  # Conexão segura
        server.login(
            "trilhaeducation@gmail.com", "xdjs nlct ogvl xzdx"  # Insira sua senha aqui
        )
        server.sendmail(remetente, destinatario, msg.as_string())

# Função para verificar a data do log e a data atual
def verificar_data_log():
    if os.path.exists(arquivo_data):
        with open(arquivo_data, "r") as file:
            last_date_str = file.read().strip()  # Lê a última data do arquivo .txt
            last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
            current_date = datetime.now().date()
            return last_date, current_date
    return None, None

# Verifica se o arquivo de log existe e se a data precisa ser atualizada
ultima_data_log, data_atual = verificar_data_log()

# Se o arquivo de log não existir, cria um novo
if ultima_data_log is None:
    with open(arquivo_log, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Horário", "Tipo de Evento", "Comentário"])

# Se o arquivo de data não existir, cria um novo
if not os.path.exists(arquivo_data):
    with open(arquivo_data, "w") as file:
        file.write(datetime.now().strftime("%Y-%m-%d"))  # Escreve a data atual

# Se a última data do log não for None, e a data atual é maior que a última data do log
if ultima_data_log is not None and data_atual > ultima_data_log:
    enviar_relatorio_email(ultima_data_log)  # Envia o e-mail com o log
    os.remove(arquivo_log)  # Exclui o arquivo antigo
    # Cria um novo arquivo de log com cabeçalho
    with open(arquivo_log, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Horário", "Tipo de Evento", "Comentário"])
    # Atualiza a data no arquivo .txt
    with open(arquivo_data, "w") as file:
        file.write(data_atual.strftime("%Y-%m-%d"))

# Configura listeners para mouse e teclado
mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
keyboard_listener = keyboard.Listener(on_press=on_key_press)

# Inicia os listeners
mouse_listener.start()
keyboard_listener.start()

# Variável para controlar o envio do e-mail
email_enviado = False

try:
    while True:
        tempo_atual = time.time()

        # Verifica se houve inatividade acima do limite
        if atividade_iniciada and (tempo_atual - ultimo_evento > tempo_max_inatividade):
            registrar_fim(tempo_atual)  # Registra o fim da atividade
            atividade_iniciada = False  # Reinicia o estado para a próxima atividade

        # Checa se é o final do dia para enviar o relatório (ajustável)
        if time.strftime("%H:%M") == "14:30" and not email_enviado:
            enviar_relatorio_email()
            email_enviado = True  # Marca que o e-mail foi enviado

        # Reseta a variável email_enviado no início de um novo dia
        if time.strftime("%H:%M") == "00:00":
            email_enviado = False

        time.sleep(1)

except KeyboardInterrupt:
    mouse_listener.stop()
    keyboard_listener.stop()
