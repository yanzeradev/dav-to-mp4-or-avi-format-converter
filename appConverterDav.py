import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import re

# Variáveis globais para controle do processo
process = None

def select_file():
    # Abre um diálogo para selecionar um arquivo .dav
    file_path = filedialog.askopenfilename(filetypes=[("DAV Files", "*.dav")])
    if file_path:
        input_path.set(file_path)

def select_output():
    # Abre um diálogo para escolher onde salvar o arquivo .mp4 ou .avi
    file_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 Files", "*.mp4"), ("AVI Files", "*.avi")])
    if file_path:
        output_path.set(file_path)
        output_path_label.config(text=f"Salvar em: {file_path}")  # Atualiza o label com o caminho selecionado

def convert_dav_to_mp4_or_avi():
    global process

    # Caminho do arquivo .dav e nome de saída
    input_file = input_path.get()
    output_file = output_path.get()

    if not input_file:
        messagebox.showerror("Erro", "Por favor, selecione um arquivo .dav para converter.")
        return
    if not output_file:
        messagebox.showerror("Erro", "Por favor, escolha onde salvar o arquivo.")
        return

    # Processo de conversão com ffmpeg
    try:
        # Executa o comando ffmpeg para converter o arquivo
        command = ['ffmpeg', '-i', input_file, '-c:v', 'libx264', '-preset', 'fast', '-crf', '22', output_file]

        # Se estiver no Windows, use CREATE_NO_WINDOW para evitar que o terminal apareça
        if os.name == 'nt':  # Se o sistema for Windows
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        else:  # Para outros sistemas operacionais
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Atualiza a interface com o progresso do tempo
        while True:
            output = process.stderr.readline()  # Saída de erro (stderr) para capturar o progresso
            if output == '' and process.poll() is not None:
                break
            if output:
                # Procura pela linha que contém o tempo atual do vídeo
                match = re.search(r"time=(\d+:\d+:\d+)", output)  # Remover milissegundos da captura
                if match:
                    time_info = match.group(1)
                    update_progress(time_info)

        process.wait()
        messagebox.showinfo("Sucesso", f"Conversão concluída! Arquivo salvo como: {output_file}")

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Erro", f"Ocorreu um erro durante a conversão: {e}")

def update_progress(time_info):
    # Atualiza a label de progresso na interface gráfica
    progress_label.config(text=f"Processando o minuto {time_info} do seu video.")

def cancel_conversion():
    global process
    if process:
        process.terminate()  # Termina o processo de conversão
        messagebox.showinfo("Cancelado", "Conversão cancelada.")
        reset_buttons()  # Reseta os botões para o estado inicial

def reset_buttons():
    cancel_button.config(state=tk.NORMAL)  # Habilita o botão de cancelar

# Criação da interface gráfica
root = tk.Tk()
root.title("Conversor de DAV para MP4 ou AVI")

# Campo de entrada para o caminho do arquivo
input_path = tk.StringVar()
output_path = tk.StringVar()

# Layout da Interface Gráfica
frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

# Rótulo e botão para selecionar o arquivo
label = tk.Label(frame, text="Selecione o arquivo .dav:")
label.grid(row=0, column=0, sticky="w")

entry = tk.Entry(frame, textvariable=input_path, width=40)
entry.grid(row=1, column=0, padx=5, pady=5)

browse_button = tk.Button(frame, text="Procurar", command=select_file)
browse_button.grid(row=1, column=1, padx=5, pady=5)

# Rótulo e botão para selecionar onde salvar o arquivo
save_label = tk.Label(frame, text="Escolha o destino do arquivo .mp4 ou .avi:")
save_label.grid(row=2, column=0, sticky="w")

save_button = tk.Button(frame, text="Salvar Como", command=select_output)
save_button.grid(row=2, column=1, padx=5, pady=5)

# Label para mostrar o caminho selecionado para salvar o arquivo
output_path_label = tk.Label(frame, text="Salvar em: Nenhum arquivo selecionado")
output_path_label.grid(row=3, column=0, columnspan=2, pady=5)

# Rótulo de progresso
progress_label = tk.Label(frame, text="Processando... Tempo atual: 00:00:00")
progress_label.grid(row=4, column=0, columnspan=2, pady=10)

# Botão para iniciar a conversão
convert_button = tk.Button(frame, text="Converter para MP4 ou AVI", command=lambda: threading.Thread(target=convert_dav_to_mp4_or_avi).start())
convert_button.grid(row=5, column=0, columnspan=2, pady=10)

# Botão de cancelar
cancel_button = tk.Button(frame, text="Cancelar", state=tk.NORMAL, command=cancel_conversion)
cancel_button.grid(row=6, column=0, columnspan=2, pady=10)

# Inicia o loop da interface gráfica
root.mainloop()
