from tkinter import *
from tkinter import ttk, filedialog, PhotoImage
from system import add_client, read_clients, remove_client
from main import main
import os, sys

current_banner = None
destroy_job = None

def is_valid_identifier(identifier: str) -> bool:
    return identifier.isdigit() and len(identifier) in (11, 14)

def open_client_management():
    window = Toplevel()
    window.title("Gerenciar Identificadores")
    window.geometry("400x400")
    window.resizable(False, False)

    window.transient(root)
    window.grab_set()

    msg_frame = Frame(window) 
    msg_frame.pack(fill="x", side="top")

    def limit_size(*args):
        value = entry_var.get()
        if len(value) > 14:
            entry_var.set(value[:14])

    def show_banner(text, duration=2500):
        global current_banner, destroy_job
        
        if current_banner is not None:
            current_banner.destroy()
            current_banner = None
        
        if destroy_job is not None:
            window.after_cancel(destroy_job)
            destroy_job = None
        
        current_banner = Label(msg_frame, text=text, bg="blue", fg="white")
        current_banner.pack(fill="x")
        
        destroy_job = window.after(duration, destroy_banner)

    def destroy_banner():
        global current_banner, destroy_job
        if current_banner is not None:
            current_banner.destroy()
            current_banner = None
        destroy_job = None

    # Centraliza sobre a janela principal
    root.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (400 // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (400 // 2)
    window.geometry(f"400x500+{x}+{y}")

    # Entrada de identificadores
    field_frame = Frame(window)
    field_frame.pack(pady=10)

    entry_var = StringVar()
    entry_var.trace_add("write", limit_size)
    entry_client = Entry(field_frame, textvariable=entry_var, width=30)
    entry_client.pack(side="left", padx=(10, 5))

    def register_client():
        client_id = entry_client.get().strip()
        if client_id and client_id not in clients_set:
            if is_valid_identifier(client_id):
                add_client(client_id)
                entry_client.delete(0, END)
                update_client_list()
            else:
                show_banner("Formato inválido. Use CPF (11 dígitos) ou CNPJ (14 dígitos).")
        else:
            show_banner("Campo vazio ou cliente já registrado.")
    
    Button(field_frame, text="Registrar", command=register_client).pack(side="left")

    Label(window, text="Identificadores Registrados (CPF/CNPJ):").pack(padx=5)

    # Container com borda
    frame_clients = Frame(window, bg="white", bd=1, relief="ridge")
    frame_clients.pack(fill="both", expand=True, padx=15, pady=10)

    # Canvas + Scrollbar
    canvas = Canvas(frame_clients, bg="white", highlightthickness=0)
    scrollbar = Scrollbar(frame_clients, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(fill="both", expand=True)

    # Frame interno
    scroll_frame = Frame(canvas, bg="white")
    scroll_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

    # Ajusta largura do frame interno
    def resize_scroll_frame(event=None):
        # Pega largura do canvas
        width = canvas.winfo_width()

        canvas.itemconfig(scroll_window, width=width)

        scroll_frame.update_idletasks()
        content_height = scroll_frame.winfo_height()
        canvas_height = canvas.winfo_height()

        if content_height > canvas_height:
            canvas.configure(scrollregion=(0, 0, width, content_height))
        else:
            canvas.configure(scrollregion=(0, 0, width, canvas_height))


    canvas.bind("<Configure>", resize_scroll_frame)

    # Atualiza scrollregion quando conteúdo muda
    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scroll_frame.bind("<Configure>", on_configure)

    # --- Scroll do mouse ---
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_linux_scroll(event):
        if event.num == 4:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            canvas.yview_scroll(1, "units")

    # Windows/macOS
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    # Linux scroll up
    canvas.bind_all("<Button-4>", _on_linux_scroll)
    # Linux scroll down
    canvas.bind_all("<Button-5>", _on_linux_scroll)

    def update_client_list():
        global clients_set
        for widget in scroll_frame.winfo_children():
            widget.destroy()
        
        clients = read_clients()
        clients_set = set(clients)

        for i, ct in enumerate(clients):
            row = Frame(scroll_frame, bg="white")
            row.pack(fill="x", pady=4, padx=(15, 5))

            Label(row, text=f"{ct}", bg="white").pack(side="left", padx=5)

            Button(
                row,
                text="\u00d7",
                bg="red",
                fg="white",
                bd=0,
                command=lambda c=ct: (remove_client(c), update_client_list())
            ).pack(side="right", padx=5)

            ttk.Separator(scroll_frame, orient="horizontal").pack(fill="x", padx=0, pady=1)

        # força atualização da área rolável
        scroll_frame.update_idletasks()
        resize_scroll_frame()

    update_client_list()

def open_directory():
    directory = filedialog.askdirectory(title="Selecione um diretório")
    dir_var.set(f"{directory}")

if getattr(sys, 'frozen', False):
    # pasta temporária criada pelo PyInstaller
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)

root = Tk()
root.title("Processador de NF-e")
root.geometry("400x400")
icon_path = os.path.join(base_path, "static", "icon-nfe.png")
icon = PhotoImage(file=icon_path)
root.iconphoto(True, icon)
root.minsize(500, 200)
root.maxsize(1800, 720)
x=root.winfo_x()
y=root.winfo_x()
root.geometry("+%d+%d" % (x+500,y+240))
root.resizable(False, False)

# Frame como container único
container = Frame(root, padx=20, pady=20)
container.pack(fill="both", expand=True)

# Campo Diretório
Label(container, text="Diretório:").pack(anchor="w", padx=10, pady=(10, 0))
dir_var = StringVar(value="")
dir_path = Entry(container, textvariable=dir_var, width=50)
dir_path.pack(anchor="w", padx=10)
Button(container, text="Abrir diretório", command=open_directory).pack(anchor="w", padx=10, pady=20)

# Opção de buscar por subdiretórios
Label(container, text="Buscar por arquivos aninhados em subdiretórios?").pack(anchor="w", padx=10, pady=(10, 0))
entry_recursive = BooleanVar(value="True")
frame_recursive = Frame(container)
frame_recursive.pack(anchor="w", padx=10)
Radiobutton(frame_recursive, text="Sim", variable=entry_recursive, value=True).pack(side="left")
Radiobutton(frame_recursive, text="Não", variable=entry_recursive, value=False).pack(side="left")

# Lista de Clientes
Button(container, text="Gerenciar Identificadores", command=open_client_management).pack(anchor="w", padx=10, pady=(20, 0))

style = ttk.Style()
style.configure("My.TButton", background="darkblue", foreground="white")
style.map("My.TButton",
          background=[("active", "black"), ("pressed", "black")],
          foreground=[("pressed", "yellow")])
          
result_var = StringVar()

def on_submit():
    result_var.set(main(dir_var.get(), entry_recursive.get()))

btn_submit = ttk.Button(container, text="Processar notas", command=on_submit, style="My.TButton")
btn_submit.pack(pady=20)

Label(container, textvariable=result_var).pack(anchor="w", padx=10, pady=(10,0))
root.mainloop()