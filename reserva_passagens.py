# Importa o módulo tkinter e renomeia-o como tk para
# facilitar seu uso no código.
import tkinter as tk
from math import expm1
import os
import time

# Importa submódulos ttk e messagebox do tkinter, utilizados
# para criar widgets com estilos melhorados e exibir caixas de diálogo.
from tkinter import ttk, messagebox

# Importa o módulo Calendar do pacote tkcalendar, que permite
# criar um widget de calendário para seleção de datas.
from tkcalendar import Calendar

# Importa o módulo datetime da biblioteca datetime, usado
# para manipular datas e tempos.
from datetime import datetime

# Importa o módulo MongoClient do pacote pymongo, que
# permite conexão com um servidor MongoDB.
from pymongo import MongoClient

# Adicione esta função para configurar o estilo
def configurar_estilo():
    style = ttk.Style()
    
    # Configuração do tema
    style.theme_use('clam')  # ou 'vista' no Windows
    
    # Configuração dos botões
    style.configure('TButton',
                   font=('Segoe UI', 12),
                   padding=10)
    
    # Configuração dos labels
    style.configure('TLabel',
                   font=('Segoe UI', 12),
                   padding=5)
    
    # Configuração do combobox
    style.configure('TCombobox',
                   font=('Segoe UI', 12),
                   padding=5)
    
    # Configuração do Treeview
    style.configure('Treeview',
                   font=('Segoe UI', 11),
                   rowheight=30)
    style.configure('Treeview.Heading',
                   font=('Segoe UI', 12, 'bold'))
    
    # Cores personalizadas
    style.configure('Primary.TButton',
                   background='#2196F3',
                   foreground='white')
    style.configure('Success.TButton',
                   background='#4CAF50',
                   foreground='white')
    style.configure('Warning.TButton',
                   background='#FFC107',
                   foreground='black')

# Chame esta função no início do seu programa
configurar_estilo()

# Define a classe Onibus, responsável pela gestão das
# reservas de um ônibus.
class Onibus:

    # Método construtor da classe com parâmetro capacidade, que
    # define o número de lugares no ônibus.
    def __init__(self, capacidade):

        # Atributo que armazena a capacidade total de lugares no ônibus.
        self.capacidade = capacidade

        # Lista que representa os lugares no ônibus, inicializada
        # com 0 (desocupado) para cada lugar baseado na capacidade.
        self.lugares = [0] * capacidade

        # Obtém a URI do MongoDB da variável de ambiente ou usa o valor padrão
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')

        # Adiciona retry na conexão com o MongoDB
        max_retries = 5
        retry_delay = 5  # segundos
        
        for attempt in range(max_retries):
            try:
                # Cria um cliente MongoDB, conectando-se ao servidor MongoDB.
                self.cliente = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
                # Testa a conexão
                self.cliente.admin.command('ping')
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Falha ao conectar ao MongoDB após {max_retries} tentativas: {str(e)}")
                print(f"Tentativa {attempt + 1} de {max_retries} falhou. Tentando novamente em {retry_delay} segundos...")
                time.sleep(retry_delay)

        # Seleciona o banco de dados 'reserva_onibus_db' dentro do servidor MongoDB.
        self.bd = self.cliente["reserva_onibus_db"]

        # Seleciona a coleção 'reservas' dentro do banco de dados especificado.
        self.colecao_reservas = self.bd["reservas"]

        # Adiciona lista de horários disponíveis
        self.horarios = ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]


    # Define o método 'carregar_reservas' que atualiza o status dos
    # lugares do ônibus com base nas reservas para uma data específica.
    def carregar_reservas(self, data, horario):

        # Cria ou reinicializa a lista 'lugares' com zeros, indicando que
        # todos os lugares estão disponíveis inicialmente.
        # O uso de [0] * capacidade cria uma lista que contém o número zero
        # repetido tantas vezes quanto o valor de 'capacidade'.
        # Por exemplo, se capacidade é 20, isso resulta em [0, 0, 0, ..., 0] com 20 zeros.
        self.lugares = [0] * self.capacidade

        # Acessa a base de dados e utiliza o método 'find' para procurar todas as
        # entradas (reservas) onde a chave 'dia' corresponde
        # ao valor da variável 'data'. O resultado ('reservas') é um iterável que
        # permite percorrer cada documento que representa
        # uma reserva para esse dia.
        reservas = self.colecao_reservas.find({"dia": data, "horario" : horario})

        # Inicia um loop que irá percorrer cada documento encontrado na busca.
        for r in reservas:

            # Acessa o valor associado à chave 'lugar' dentro do
            # documento (representado por 'r') da reserva.
            # Este valor indica o número do lugar que foi reservado.
            num_lugar = r["lugar"]

            # Verifica se o número do lugar reservado está dentro do
            # intervalo permitido (de 1 até 'capacidade').
            # A verificação assegura que não tentaremos acessar
            # índices fora da lista 'lugares'.
            if 1 <= num_lugar <= self.capacidade:

                # Marca o lugar especificado como ocupado.
                # Ajusta o índice para base zero (listas em Python
                # começam em 0, não em 1), subtraindo 1 do número do lugar.
                # Por exemplo, lugar 1 na reserva corresponde ao
                # índice 0 na lista, lugar 2 ao índice 1, e assim por diante.
                self.lugares[num_lugar - 1] = 1


    # Define o método 'reservar_lugar' para reservar um lugar no ônibus,
    # recebendo como parâmetros o número do lugar, nome do cliente, CPF e a data da reserva.
    def reservar_lugar(self, num_lugar, nome, cpf, dia, horario):

        # Verifica se o número do lugar é válido, ou seja, deve estar
        # dentro do intervalo de 1 até a capacidade máxima do ônibus.
        if num_lugar < 1 or num_lugar > self.capacidade:

            # Retorna uma mensagem indicando que o número do lugar é
            # inválido se estiver fora do intervalo.
            return "Lugar inválido"

        # Chama o método 'carregar_reservas' para atualizar o estado
        # atual dos lugares para a data especificada.
        self.carregar_reservas(dia, horario)

        # Verifica se o lugar especificado está disponível (0 indica disponível).
        if self.lugares[num_lugar - 1] == 0:

            # Se disponível, marca o lugar como reservado (atribuindo 1).
            self.lugares[num_lugar - 1] = 1

            # Cria um dicionário contendo os detalhes da reserva.
            doc = {
                "lugar": num_lugar,  # Número do lugar.
                "nome": nome,  # Nome do cliente.
                "cpf": cpf,  # CPF do cliente.
                "dia": dia, # Data da reserva.
                "horario": horario
            }

            # Insere o documento da reserva na coleção de reservas
            # no banco de dados MongoDB.
            self.colecao_reservas.insert_one(doc)

            # Retorna uma mensagem de sucesso, indicando que o
            # lugar foi reservado com sucesso.
            return f"Lugar {num_lugar} reservado com sucesso para {horario}"

        else:

            # Se o lugar já está ocupado, retorna uma mensagem
            # indicando que o lugar está indisponível.
            return f"Lugar {num_lugar} indisponível para {horario}"


    # Define o método 'cancelar_reserva' para cancelar uma reserva de um
    # lugar específico em uma data específica.
    def cancelar_reserva(self, lugar, dia, horario):

        # Primeiro, carrega todas as reservas para a data especificada para
        # atualizar o estado atual dos lugares.
        self.carregar_reservas(dia, horario)

        # Verifica se o número do lugar está dentro da capacidade do ônibus e se o
        # lugar está atualmente reservado ('1' indica reservado).
        if 1 <= lugar <= self.capacidade and self.lugares[lugar - 1] == 1:

            # Se o lugar está reservado, executa a operação de remoção da
            # reserva no banco de dados.
            # O método 'delete_one' remove um documento específico da coleção,
            # neste caso, onde 'lugar' e 'dia' correspondem aos fornecidos.
            self.colecao_reservas.delete_one({"lugar": lugar, "dia": dia,"horario": horario})

            # Retorna uma mensagem informando que a reserva foi cancelada com sucesso.
            return f"Lugar {lugar} reserva cancelada para {horario}"

        else:

            # Se o lugar não está reservado, retorna uma mensagem
            # indicando que não há reserva para cancelar.
            return f"Lugar {lugar} não está reservado para {horario}"


# Define a classe 'JanelaCadastro', responsável por criar e gerenciar a
# interface de cadastro de novas reservas de passagens.
class JanelaCadastro:

    # Método construtor que é chamado ao criar uma nova instância de JanelaCadastro.
    # Parâmetros:
    # janela_pai: referência à janela principal ou à janela que
    # chama a janela de cadastro.
    # onibus: objeto que representa o ônibus e suas reservas, permitindo
    # interagir com os dados de reserva.
    # janela_principal: referência à instância da JanelaPrincipal para
    # permitir chamadas de volta a métodos da janela principal.
    # data_inicial: data predefinida para facilitar o processo de cadastro,
    # geralmente a data atual selecionada na janela principal.
    def __init__(self, janela_pai, onibus, janela_principal, data_inicial, lugar=None):
        # Primeiro, criamos a janela
        self.janela = tk.Toplevel(janela_pai)
        self.janela.title("Cadastrar Reserva")
        self.janela.configure(bg="white")
        
        # Configura o tamanho e posição da janela
        self.janela.geometry("500x600")
        self.janela.update_idletasks()
        largura_tela = self.janela.winfo_screenwidth()
        altura_tela = self.janela.winfo_screenheight()
        pos_x = int(largura_tela / 2 - 250)
        pos_y = int(altura_tela / 2 - 300)
        self.janela.geometry(f"500x600+{pos_x}+{pos_y}")
        
        # Agora podemos criar as variáveis StringVar
        self.nome_var = tk.StringVar(self.janela)
        self.cpf_var = tk.StringVar(self.janela)
        self.lugar_var = tk.StringVar(self.janela, value=str(lugar) if lugar else "")
        self.horario_var = tk.StringVar(self.janela)
        
        # Armazena as referências
        self.janela_principal = janela_principal
        self.onibus = onibus
        
        # Frame principal
        frame_principal = tk.Frame(self.janela, bg="white", padx=20, pady=20)
        frame_principal.pack(fill='both', expand=True)
        
        # Título
        tk.Label(frame_principal,
                text="Cadastrar Reserva",
                font=("Segoe UI", 24, "bold"),
                bg="white",
                fg="#333333").pack(pady=(0, 20))
        
        # Frame do formulário
        frame_form = tk.Frame(frame_principal, bg="white")
        frame_form.pack(fill='x', pady=10)
        
        # Nome
        tk.Label(frame_form,
                text="Nome:",
                font=("Segoe UI", 14),
                bg="white").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        
        tk.Entry(frame_form,
                textvariable=self.nome_var,
                font=("Segoe UI", 14),
                width=30).grid(row=0, column=1, padx=5, pady=5)
        
        # CPF
        tk.Label(frame_form,
                text="CPF:",
                font=("Segoe UI", 14),
                bg="white").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        
        tk.Entry(frame_form,
                textvariable=self.cpf_var,
                font=("Segoe UI", 14),
                width=30).grid(row=1, column=1, padx=5, pady=5)
        
        # Lugar
        tk.Label(frame_form,
                text="Lugar:",
                font=("Segoe UI", 14),
                bg="white").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        
        tk.Entry(frame_form,
                textvariable=self.lugar_var,
                font=("Segoe UI", 14),
                width=10,
                state='readonly').grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        # Data
        tk.Label(frame_form,
                text="Data:",
                font=("Segoe UI", 14),
                bg="white").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        
        # Frame para o calendário
        frame_calendario = tk.Frame(frame_form, bg="white")
        frame_calendario.grid(row=3, column=1, sticky='w', padx=5, pady=5)
        
        self.cal_cadastro = Calendar(frame_calendario,
                                   selectmode='day',
                                   date_pattern='dd/mm/yyyy',
                                   font=("Segoe UI", 12))
        self.cal_cadastro.pack()
        self.cal_cadastro.selection_set(data_inicial)
        
        # Horário
        tk.Label(frame_form,
                text="Horário:",
                font=("Segoe UI", 14),
                bg="white").grid(row=4, column=0, sticky='e', padx=5, pady=5)
        
        self.horario_combo = ttk.Combobox(frame_form,
                                         textvariable=self.horario_var,
                                         values=onibus.horarios,
                                         font=("Segoe UI", 14),
                                         state="readonly",
                                         width=15)
        self.horario_combo.grid(row=4, column=1, sticky='w', padx=5, pady=5)
        
        # Adiciona o placeholder
        self.horario_combo.set("Selecione o horário")
        
        # Adiciona evento para quando o combobox receber foco
        def on_focus_in(event):
            if self.horario_var.get() == "Selecione o horário":
                self.horario_combo.set(onibus.horarios[0])
        
        self.horario_combo.bind('<FocusIn>', on_focus_in)
        
        # Frame para o botão
        frame_botao = tk.Frame(frame_principal, bg="white")
        frame_botao.pack(fill='x', pady=20)
        
        # Botão de reservar
        ttk.Button(frame_botao,
                  text="Reservar",
                  style='Success.TButton',
                  command=self.reservar).pack(pady=10)
        
        # Configura o grid do frame_form
        frame_form.grid_columnconfigure(1, weight=1)
        
        # Centraliza a janela
        self.janela.transient(janela_pai)
        self.janela.grab_set()

    # Define o método 'reservar' que é chamado ao clicar no
    # botão "Reservar" na janela de cadastro.
    def reservar(self):
        nome = self.nome_var.get().strip()
        cpf = self.cpf_var.get().strip()
        dia = self.cal_cadastro.get_date()
        horario = self.horario_var.get()
        
        try:
            lugar = int(self.lugar_var.get())
        except:
            messagebox.showwarning("Aviso", "Lugar inválido.")
            return
        
        if not nome or not cpf or not dia or not horario:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return
        
        res = self.onibus.reservar_lugar(lugar, nome, cpf, dia, horario)
        messagebox.showinfo("Info", res)
        
        self.janela.destroy()
        self.janela_principal.atualizar_mapa()


# Define a classe 'JanelaPesquisa' para gerenciar a interface de
# pesquisa de reservas históricas.
class JanelaPesquisa:

    # Método construtor que é chamado ao criar uma nova instância de JanelaPesquisa.
    def __init__(self, janela_pai, onibus, janela_principal):
        # Primeiro, armazenamos as referências
        self.janela_principal = janela_principal
        self.onibus = onibus  # Armazena a referência do onibus
        
        # Cria a janela
        self.janela = tk.Toplevel(janela_pai)
        self.janela.title("Pesquisar Reservas")
        self.janela.configure(bg="white")
        
        # Configura o tamanho e posição da janela
        self.janela.geometry("1200x600")
        self.janela.update_idletasks()
        largura_tela = self.janela.winfo_screenwidth()
        altura_tela = self.janela.winfo_screenheight()
        pos_x = int(largura_tela / 2 - 600)
        pos_y = int(altura_tela / 2 - 300)
        self.janela.geometry(f"1200x600+{pos_x}+{pos_y}")
        
        # Frame principal
        frame_principal = tk.Frame(self.janela, bg="white", padx=20, pady=20)
        frame_principal.pack(fill='both', expand=True)
        
        # Título
        tk.Label(frame_principal,
                text="Pesquisar Reservas",
                font=("Segoe UI", 24, "bold"),
                bg="white",
                fg="#333333").pack(pady=(0, 20))
        
        # Frame para filtros
        frame_filtros = tk.Frame(frame_principal, bg="white")
        frame_filtros.pack(fill='x', pady=(0, 20))
        
        # Campos de filtro
        self.rotulos_filtro = ["Lugar", "Nome", "CPF", "Data", "Horário"]
        self.campos_filtro = []
        
        # Cria os campos de filtro
        for i, rotulo in enumerate(self.rotulos_filtro):
            # Frame para cada campo
            frame_campo = tk.Frame(frame_filtros, bg="white")
            frame_campo.pack(side=tk.LEFT, padx=10)
            
            # Label
            tk.Label(frame_campo,
                    text=rotulo + ":",
                    font=("Segoe UI", 12),
                    bg="white").pack(side=tk.TOP)
            
            # Campo de entrada
            campo = ttk.Entry(frame_campo,
                            font=("Segoe UI", 12),
                            width=15)
            campo.pack(side=tk.TOP, pady=(5, 0))
            self.campos_filtro.append(campo)
        
        # Botão de filtrar
        ttk.Button(frame_filtros,
                  text="Filtrar",
                  style='Primary.TButton',
                  command=self.filtrar_reservas).pack(side=tk.LEFT, padx=10, pady=(25, 0))
        
        # Frame para a tabela
        frame_tabela = tk.Frame(frame_principal, bg="white")
        frame_tabela.pack(fill='both', expand=True)
        
        # Treeview
        self.treeview = ttk.Treeview(frame_tabela)
        self.treeview["columns"] = ("Lugar", "Nome", "CPF", "Data", "Horário")
        
        # Configuração das colunas
        self.treeview.column("#0", width=0, stretch=tk.NO)
        self.treeview.column("Lugar", width=100, anchor=tk.CENTER)
        self.treeview.column("Nome", width=300, anchor=tk.W)
        self.treeview.column("CPF", width=150, anchor=tk.CENTER)
        self.treeview.column("Data", width=100, anchor=tk.CENTER)
        self.treeview.column("Horário", width=100, anchor=tk.CENTER)
        
        # Configuração dos cabeçalhos
        self.treeview.heading("Lugar", text="Lugar", anchor=tk.CENTER)
        self.treeview.heading("Nome", text="Nome", anchor=tk.CENTER)
        self.treeview.heading("CPF", text="CPF", anchor=tk.CENTER)
        self.treeview.heading("Data", text="Data", anchor=tk.CENTER)
        self.treeview.heading("Horário", text="Horário", anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabela,
                                 orient=tk.VERTICAL,
                                 command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=scrollbar.set)
        
        # Empacotamento
        self.treeview.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
        # Frame para botões de ação
        frame_acoes = tk.Frame(frame_principal, bg="white")
        frame_acoes.pack(fill='x', pady=(20, 0))
        
        # Botão de cancelar reserva
        ttk.Button(frame_acoes,
                  text="Cancelar Reserva Selecionada",
                  style='Warning.TButton',
                  command=self.cancelar_reserva).pack(side=tk.LEFT, padx=5)
        
        # Agora que tudo está configurado, carregamos as reservas
        self.carregar_reservas()
    
    def carregar_reservas(self):
        # Limpa o treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        
        # Carrega todas as reservas
        self.reservas = list(self.onibus.colecao_reservas.find({}))
        
        # Insere as reservas no treeview
        for reserva in self.reservas:
            # Obtém os valores com tratamento para campos ausentes
            lugar = reserva.get("lugar", "N/A")
            nome = reserva.get("nome", "N/A")
            cpf = reserva.get("cpf", "N/A")
            dia = reserva.get("dia", "N/A")
            horario = reserva.get("horario", "N/A")  # Usa "N/A" se o horário não existir
            
            self.treeview.insert("",
                                tk.END,
                                values=(lugar, nome, cpf, dia, horario))
    
    def filtrar_reservas(self):
        # Limpa o treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        
        # Cria o dicionário de filtros
        filtros = {}
        for rotulo, campo in zip(self.rotulos_filtro, self.campos_filtro):
            valor = campo.get().strip()
            if valor:
                filtros[rotulo] = valor.lower()
        
        # Filtra as reservas
        for reserva in self.reservas:
            corresponde = True
            
            # Obtém os valores com tratamento para campos ausentes
            lugar = str(reserva.get("lugar", "N/A")).lower()
            nome = reserva.get("nome", "N/A").lower()
            cpf = reserva.get("cpf", "N/A").lower()
            dia = reserva.get("dia", "N/A").lower()
            horario = reserva.get("horario", "N/A").lower()
            
            if "Lugar" in filtros and filtros["Lugar"] != lugar:
                corresponde = False
            if "Nome" in filtros and filtros["Nome"] not in nome:
                corresponde = False
            if "CPF" in filtros and filtros["CPF"] != cpf:
                corresponde = False
            if "Data" in filtros and filtros["Data"] != dia:
                corresponde = False
            if "Horário" in filtros and filtros["Horário"] != horario:
                corresponde = False
            
            if corresponde:
                self.treeview.insert("",
                                    tk.END,
                                    values=(reserva.get("lugar", "N/A"),
                                           reserva.get("nome", "N/A"),
                                           reserva.get("cpf", "N/A"),
                                           reserva.get("dia", "N/A"),
                                           reserva.get("horario", "N/A")))
    
    def cancelar_reserva(self):
        selecao = self.treeview.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione uma reserva para cancelar.")
            return
        
        item = self.treeview.item(selecao[0])
        lugar = item["values"][0]
        dia = item["values"][3]
        horario = item["values"][4]
        
        # Verifica se o horário é válido
        if horario == "N/A":
            messagebox.showwarning("Aviso", "Não é possível cancelar esta reserva: horário não disponível.")
            return
        
        res = self.onibus.cancelar_reserva(lugar, dia, horario)
        messagebox.showinfo("Info", res)
        
        # Atualiza a lista de reservas
        self.carregar_reservas()
        # Atualiza o mapa na janela principal
        self.janela_principal.atualizar_mapa()


# Define a classe 'JanelaPrincipal' que gerencia a janela principal do
# sistema de reserva de passagens.
class JanelaPrincipal:

    # Método construtor que inicializa uma nova instância da JanelaPrincipal com a
    # janela do sistema e uma instância do ônibus.
    def __init__(self, janela_sistema, onibus):
        # Armazena a referência da janela principal do sistema (tk.Tk())
        # passada como argumento.
        self.janela_sistema = janela_sistema

        # Armazena a referência para a instância da classe
        # Onibus passada como argumento.
        self.onibus = onibus

        # Define o título da janela do sistema, que aparecerá na
        # barra de título da janela.
        self.janela_sistema.title("Sistema de Reserva de Passagens")

        # Configura o estado da janela para maximizado
        self.janela_sistema.attributes('-zoomed', True)  # Para Linux
        try:
            self.janela_sistema.state('zoomed')  # Para Windows
        except:
            pass

        # Define a cor de fundo da janela principal para um
        # cinza claro (#f0f0f0).
        self.janela_sistema.configure(bg="#f0f0f0")

        # Configurar o estilo
        configurar_estilo()
        
        # Frame principal com padding
        frame_principal = tk.Frame(self.janela_sistema, bg="#f5f5f5", padx=20, pady=20)
        frame_principal.pack(fill='both', expand=True)
        
        # Frame esquerdo com sombra e borda
        frame_esquerda = tk.Frame(frame_principal, 
                                 bg="white",
                                 relief="solid",
                                 borderwidth=1,
                                 padx=20,
                                 pady=20)
        frame_esquerda.pack(side='left',
                           fill='y',
                           padx=10,
                           pady=10)
        
        # Título com fonte mais moderna
        titulo = tk.Label(frame_esquerda,
                         text="Reserva de Passagens",
                         font=("Segoe UI", 24, "bold"),
                         bg="white",
                         fg="#333333")
        titulo.pack(pady=(0, 20))
        
        # Frame para o calendário com borda
        frame_calendario = tk.Frame(frame_esquerda,
                                   bg="white",
                                   relief="solid",
                                   borderwidth=1,
                                   padx=10,
                                   pady=10)
        frame_calendario.pack(fill='x', pady=10)
        
        # Label do calendário
        tk.Label(frame_calendario,
                text="Selecione a data:",
                font=("Segoe UI", 14),
                bg="white").pack(pady=(0, 10))
        
        # Calendário com estilo personalizado
        self.cal = Calendar(frame_calendario,
                           selectmode='day',
                           date_pattern='dd/mm/yyyy',
                           font=("Segoe UI", 12),
                           background="white",
                           foreground="black",
                           selectbackground="#2196F3")
        self.cal.pack(pady=10)
        
        # Frame para seleção de horário
        frame_horario = tk.Frame(frame_esquerda,
                                bg="white",
                                relief="solid",
                                borderwidth=1,
                                padx=10,
                                pady=10)
        frame_horario.pack(fill='x', pady=10)
        
        # Adiciona label para horário
        tk.Label(frame_esquerda,
                text="Selecione o horário:",
                font=("Segoe UI", 14),
                bg="white").pack(pady=10)

        # Cria combobox para seleção de horário
        self.horario_var = tk.StringVar()
        self.horario_combo = ttk.Combobox(frame_esquerda,
                                         textvariable=self.horario_var,
                                         values=onibus.horarios,
                                         font=("Segoe UI", 12),
                                         state="readonly")
        self.horario_combo.pack(pady=10)

        # Adiciona o placeholder
        self.horario_combo.set("Selecione o horário")  # Placeholder inicial

        # Adiciona evento para atualizar o mapa quando o horário mudar
        self.horario_combo.bind('<<ComboboxSelected>>', lambda e: self.atualizar_mapa())

        # Adiciona evento para quando o combobox receber foco
        def on_focus_in(event):
            if self.horario_var.get() == "Selecione o horário":
                self.horario_combo.set(onibus.horarios[0])

        self.horario_combo.bind('<FocusIn>', on_focus_in)
        
        # Frame para botões
        frame_botoes = tk.Frame(frame_esquerda, bg="white")
        frame_botoes.pack(fill='x', pady=20)
        
        # Botões com estilo moderno
        ttk.Button(frame_botoes,
                  text="Atualizar Mapa",
                  style='Primary.TButton',
                  command=self.atualizar_mapa).pack(fill='x', pady=5)
        
        ttk.Button(frame_botoes,
                  text="Cadastrar Reserva",
                  style='Success.TButton',
                  command=self.abrir_cadastro).pack(fill='x', pady=5)
        
        ttk.Button(frame_botoes,
                  text="Pesquisar Reservas",
                  style='Primary.TButton',
                  command=self.abrir_pesquisa).pack(fill='x', pady=5)

        # Cria um frame que será usado para conter o mapa de assentos
        # na parte direita da janela principal.
        # 'frame_principal' é o contêiner pai onde este novo frame será inserido.
        # 'bg="#f0f0f0"' define a cor de fundo do frame como cinza claro,
        # onde "#f0f0f0" é o código hexadecimal dessa cor,
        # proporcionando um fundo neutro que não distrai.
        frame_direita = tk.Frame(frame_principal,
                                 bg="#f0f0f0")

        # Posiciona o 'frame_direita' dentro do 'frame_principal'.
        # 'side='right'' faz com que o frame seja ancorado ao lado direito da janela principal.
        # 'fill='both'' faz com que o frame expanda tanto horizontal quanto
        # verticalmente para preencher o espaço disponível.
        # 'expand=True' permite que o frame expanda para ocupar qualquer espaço
        # extra na janela, garantindo que utilize todo o espaço disponível.
        # 'padx=5' e 'pady=20' adicionam um espaçamento externo de 5 pixels
        # horizontalmente e 20 pixels verticalmente em torno do frame,
        # criando uma margem que separa o frame dos outros elementos ou bordas da janela.
        frame_direita.pack(side='right',
                           fill='both',
                           expand=True,
                           padx=5,
                           pady=20)

        # Frame do mapa com estilo moderno
        self.frame_mapa = tk.Frame(frame_direita,
                                  bg="white",
                                  relief="solid",
                                  borderwidth=1,
                                  padx=20,
                                  pady=20)
        self.frame_mapa.pack(fill='both',
                            expand=True,
                            padx=10,
                            pady=10)
        
        # Título do mapa
        self.mapa_label = tk.Label(self.frame_mapa,
                                  text="Mapa de Assentos",
                                  font=("Segoe UI", 20, "bold"),
                                  bg="white",
                                  fg="#333333")
        self.mapa_label.pack(pady=(0, 20))
        
        # Canvas com estilo moderno
        self.canvas = tk.Canvas(self.frame_mapa,
                               bg="white",
                               highlightthickness=0)
        
        # Cria uma barra de rolagem vertical associada ao Canvas criado anteriormente.
        # 'orient=tk.VERTICAL' configura a orientação da barra de rolagem para
        # vertical, o que é apropriado para a visualização de uma lista extensa de
        # assentos que pode não caber totalmente na altura disponível da janela.
        # 'command=self.canvas.yview' associa a movimentação da barra de rolagem ao
        # deslocamento vertical do conteúdo dentro do Canvas.
        # Isso permite que o usuário desloque a visualização dos assentos verticalmente
        # usando a barra de rolagem, melhorando a acessibilidade e usabilidade da interface.
        self.scrollbar = tk.Scrollbar(self.frame_mapa,
                                      orient=tk.VERTICAL,
                                      command=self.canvas.yview)

        # Configura o Canvas para responder ao deslocamento da barra de rolagem.
        # 'yscrollcommand=self.scrollbar.set' faz com que a posição da barra de
        # rolagem reflita e controle a posição da visualização vertical dentro do Canvas.
        # Essa configuração é necessária para sincronizar o movimento da barra de
        # rolagem com o conteúdo do Canvas, garantindo que o usuário possa
        # navegar efetivamente pelo mapa de assentos.
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Adiciona a barra de rolagem ('scrollbar') ao lado direito do frame que contém o canvas.
        # 'side=tk.RIGHT' posiciona a barra de rolagem na parte direita do frame 'self.frame_mapa'.
        # 'fill=tk.Y' faz com que a barra de rolagem se estenda verticalmente ao
        # longo de todo o lado direito do frame, ocupando todo o espaço vertical disponível.
        # Essa configuração é ideal para interfaces onde é necessário rolar
        # através de uma lista longa de itens, como um mapa de assentos.
        self.scrollbar.pack(side=tk.RIGHT,
                            fill=tk.Y)

        # Adiciona o canvas ao lado esquerdo do frame, garantindo que ele ocupe o
        # espaço restante não utilizado pela barra de rolagem.
        # 'side=tk.LEFT' posiciona o canvas à esquerda dentro do frame,
        # oposto à barra de rolagem.
        # 'fill=tk.BOTH' permite que o canvas expanda tanto vertical quanto
        # horizontalmente para preencher todo o espaço disponível no frame.
        # 'expand=True' faz com que o canvas cresça para ocupar qualquer espaço
        # extra na interface, garantindo que o conteúdo dentro do
        # canvas seja acessível e bem apresentado.
        self.canvas.pack(side=tk.LEFT,
                         fill=tk.BOTH,
                         expand=True)

        # Cria um frame dentro do canvas para servir como container para os
        # widgets (como botões que representam os assentos).
        # Este frame será usado para organizar visualmente os assentos dentro do canvas.
        # 'bg="#f0f0f0"' define a cor de fundo do frame interno como cinza claro,
        # mantendo a consistência com o design geral da interface.
        self.canvas_frame = tk.Frame(self.canvas,
                                     bg="#f0f0f0")

        # Cria uma 'janela' dentro do canvas, onde o 'self.canvas_frame' é ancorado.
        # '(0, 0)' define a posição inicial da janela no canvas, no canto superior esquerdo.
        # 'window=self.canvas_frame' especifica que o frame interno criado
        # anteriormente será o conteúdo dessa 'janela'.
        # 'anchor="nw"' garante que o frame seja ancorado a partir do canto
        # superior esquerdo (noroeste), ajudando a manter a orientação
        # correta dos conteúdos dentro do canvas.
        self.canvas.create_window((0, 0),
                                  window=self.canvas_frame,
                                  anchor="nw")

        # Cria um botão no frame à esquerda que, quando clicado, chamará a
        # função 'atualizar_mapa' para atualizar a visualização dos assentos.
        # 'text="Atualizar Mapa"' define o texto do botão.
        # 'font=("Arial", 16)' define a fonte do texto como Arial tamanho 16.
        # 'bg="#dcedc8"' define a cor de fundo do botão para um verde claro.
        # 'command=self.atualizar_mapa' associa o botão à função 'atualizar_mapa'
        # que será executada ao clicar no botão.
        # 'pack(pady=10)' posiciona o botão no frame, adicionando um espaçamento
        # vertical de 10 pixels para separação dos elementos.
        tk.Button(frame_esquerda,
                  text="Atualizar Mapa",
                  font=("Arial", 16),
                  bg="#dcedc8",
                  command=self.atualizar_mapa).pack(pady=10)

        # Cria um botão para abrir a janela de cadastro de novas reservas.
        # 'text="Cadastrar Reserva"' define o texto do botão.
        # 'bg="#a5d6a7"' define a cor de fundo do botão para um verde médio.
        tk.Button(frame_esquerda,
                  text="Cadastrar Reserva",
                  font=("Arial", 16),
                  bg="#a5d6a7",
                  command=self.abrir_cadastro).pack(pady=10)

        # Cria um botão para abrir a janela de pesquisa de reservas históricas,
        # que permite ao usuário consultar reservas passadas.
        tk.Button(frame_esquerda,

                  # Define o texto do botão.
                  text="Pesquisar (Histórico)",

                  # Define a fonte como Arial tamanho 16, garantindo que o texto seja legível.
                  font=("Arial", 16),

                  # Define a cor de fundo do botão para um azul claro, criando um visual atraente.
                  bg="#b3e5fc",

                  # Associa o botão à função 'abrir_pesquisa' e posiciona com um
                  # padding vertical de 10 pixels para separação.
                  command=self.abrir_pesquisa).pack(pady=10)

        # Seleciona a data atual no calendário e atualiza o mapa de assentos
        hoje = datetime.now().strftime("%d/%m/%Y")
        self.cal.selection_set(hoje)
        
        # Agora que horario_var já foi criado, podemos chamar atualizar_mapa
        self.atualizar_mapa()


    """
        Atualiza o mapa de assentos em formato de duas colunas com 
                barra de rolagem e largura expandida.
        Este método é responsável por mostrar visualmente o estado atual dos 
                assentos (livres ou reservados) com base na data selecionada no calendário.
        """

    def atualizar_mapa(self):

        # A linha abaixo recupera a data selecionada pelo usuário no
        # widget de calendário.
        # O método 'get_date()' é um método do tkcalendar.Calendar que
        # retorna a data selecionada no formato de string.
        data = self.cal.get_date()

        horario = self.horario_var.get()

        # Após obter a data, o método 'carregar_reservas' do objeto 'onibus' é
        # chamado com essa data como argumento.
        # Este método é responsável por carregar o estado atual dos assentos (se
        # estão reservados ou não) para a data especificada,
        # atualizando o atributo 'lugares' do objeto 'onibus' que é uma lista onde
        # cada posição representa um assento e o valor
        # indica se o assento está reservado (1) ou não (0).
        self.onibus.carregar_reservas(data, horario)

        # A seguir, todos os widgets existentes no 'canvas_frame' são removidos.
        # 'canvas_frame' é um contêiner (frame) dentro de um objeto 'Canvas' que
        # contém botões representando os assentos do ônibus.
        # O método 'winfo_children()' retorna uma lista de todos os widgets filhos (neste
        # caso, botões de assento) contidos dentro de 'canvas_frame'.
        for widget in self.canvas_frame.winfo_children():

            # Cada widget (botão de assento) é destruído iterativamente.
            # O método 'destroy()' é usado para remover completamente um widget da
            # interface gráfica e liberar todos os recursos de sistema relacionados.
            widget.destroy()

        # Adiciona os botões no layout de duas colunas
        for i in range(self.onibus.capacidade):

            # Verifica se o assento atual (índice i) está reservado. A lista 'lugares'
            # contém 1 para reservado e 0 para livre.
            reservado = self.onibus.lugares[i] == 1

            # Define a cor do botão baseado no status do assento: amarelo (#ffd700) se
            # reservado, verde (#98fb98) se livre.
            cor = "#ffd700" if reservado else "#98fb98"

            # A função 'manipular_click' captura o valor atual de 'i' na variável 'indice'.
            def manipular_click(indice=i):

                # Verifica se o assento no índice especificado está reservado.
                if self.onibus.lugares[indice] == 1:

                    # Consulta no banco de dados MongoDB para encontrar uma reserva específica.
                    # Usa 'find_one' para buscar um único documento que corresponde aos
                    # critérios: número do lugar ('lugar') e data ('dia').
                    # 'indice + 1' ajusta o índice base-0 para base-1, já que os
                    # lugares no banco de dados começam em 1, não em 0.
                    reserva = self.onibus.colecao_reservas.find_one({
                        "lugar": indice + 1,
                        "dia": data,
                        "horario": horario
                    })

                    # Verifica se algum documento foi encontrado com os critérios especificados.
                    # Se 'reserva' não é None, significa que uma reserva foi encontrada
                    # para o assento e a data especificados.
                    if reserva:

                        # Constrói uma string que contém as informações da reserva encontrada.
                        # Esta string inclui o número do lugar, o nome da pessoa que fez a
                        # reserva, o CPF e a data da reserva.
                        # Os dados são acessados diretamente do documento retornado do banco de dados.
                        info_reserva = (
                            f"Lugar: {reserva['lugar']}\n"
                            f"Nome: {reserva['nome']}\n"
                            f"CPF: {reserva['cpf']}\n"
                            f"Data: {reserva['dia']}\n"
                            f"Horário: {reserva['horario']}"
                        )

                        # Abre uma caixa de diálogo perguntando ao usuário se deseja
                        # cancelar a reserva encontrada.
                        # 'askyesno' cria uma janela de mensagem com botões 'Sim' e 'Não'.
                        # O texto exibido inclui as informações da reserva e pergunta se o
                        # usuário deseja cancelar essa reserva.
                        confirmar = messagebox.askyesno("Reserva Encontrada",
                                                        f"{info_reserva}\n\nDeseja cancelar esta reserva?")

                        # Verifica se o usuário clicou no botão 'Sim' na caixa de diálogo.
                        if confirmar:

                            # Chama o método 'cancelar_reserva' do objeto 'onibus' para
                            # cancelar a reserva no banco de dados.
                            # Passa o índice do lugar (ajustado para base-1) e a data como
                            # argumentos para identificar a reserva a ser cancelada.
                            resultado = self.onibus.cancelar_reserva(indice + 1, data, horario)

                            # Exibe uma mensagem informando o resultado do processo de cancelamento.
                            # 'showinfo' cria uma janela de mensagem que mostra o texto do
                            # resultado, que geralmente confirma o cancelamento.
                            messagebox.showinfo("Reserva Cancelada", resultado)

                            # Atualiza o mapa de assentos para refletir a mudança no estado
                            # dos assentos após o cancelamento.
                            # Isso garante que o mapa gráfico dos assentos mostre o assento
                            # como disponível se o cancelamento foi bem-sucedido.
                            self.atualizar_mapa()


                else:

                    # Se o lugar está disponível, abre a janela de cadastro para fazer uma nova reserva.
                    JanelaCadastro(self.janela_sistema, self.onibus, self, data, lugar=indice + 1)

            # Cria um botão para cada assento. O botão é configurado
            # com o texto do número do lugar,
            # a cor determinada pelo status do assento (reservado ou livre), e uma
            # ação associada ao clique que executa a função 'manipular_click'.
            # Esta função manipula o comportamento do botão dependendo do
            # estado do assento (reservado ou não).
            botao = tk.Button(

                # Especifica o frame dentro do canvas onde o botão será adicionado.
                self.canvas_frame,

                # Configura o texto do botão para indicar o número do lugar,
                # incrementando i por 1 para corresponder à contagem humana.
                text=f"Lugar {i + 1}",

                # Define a cor de fundo do botão baseado na variável 'cor', que é
                # amarela para assentos reservados e verde para livres.
                bg=cor,

                # Associa o botão à função 'manipular_click', que será chamada
                # quando o botão for clicado.
                command=manipular_click,

                # Define a fonte do texto do botão como Arial, tamanho 14, em negrito.
                font=("Arial", 14, "bold"),

                # Define a altura do botão como 1, adequado para a visualização do texto.
                height=1,

                # Define a largura do botão como 30, suficiente para exibir o
                # texto do lugar confortavelmente.
                width=30

            )

            # Organiza os botões em um grid de duas colunas dentro do frame especificado.
            # Isso permite uma apresentação organizada dos lugares em pares.
            # A organização em grid é escolhida para simular a disposição física dos
            # assentos em um ônibus, facilitando a visualização pelo usuário.
            # Calcula a linha para o botão baseado no índice do assento.
            # A divisão inteira por 2 agrupa os lugares em pares.
            row = i // 2

            # Calcula a coluna (0 ou 1) para alternar os botões entre esquerda e
            # direita, mantendo a simetria do layout de assentos.
            column = i % 2

            # Posiciona o botão criado anteriormente dentro do grid layout do 'canvas_frame'.
            # 'row=row' define em qual linha do grid o botão será colocado. O valor de 'row' é
            # calculado com base no índice do assento,
            # permitindo uma distribuição equilibrada dos botões em várias linhas,
            # dependendo do número total de assentos.
            # 'column=column' define em qual coluna do grid o botão será colocado.
            # O valor de 'column' alterna entre 0 e 1,
            # permitindo que os botões sejam organizados em duas colunas, o que ajuda a
            # simular a disposição física dos assentos em um ônibus.
            # 'padx=10' e 'pady=5' adicionam um espaçamento externo de 10 pixels na
            # horizontal e 5 pixels na vertical entre o botão e outros elementos do grid.
            # Isso ajuda a evitar que os botões fiquem visualmente amontoados e
            # melhora a estética geral da interface.
            # 'sticky="nsew"' é uma opção de configuração que faz o botão expandir
            # para preencher todo o espaço disponível na célula do grid.
            # As letras 'n', 's', 'e', 'w' representam norte, sul, leste e oeste,
            # respectivamente, indicando que o botão deve se expandir
            # em todas as direções para ocupar completamente sua célula no
            # grid, assegurando que o layout seja responsivo e visualmente coerente.
            botao.grid(row=row,
                       column=column,
                       padx=10,
                       pady=5,
                       sticky="nsew")  # Expande na horizontal

            # Configura as propriedades de expansão das colunas dentro do frame 'canvas_frame'.
            # Isso é necessário para garantir que ambos os lados do grid (esquerda e
            # direita) expandam uniformemente ao redimensionar a janela.
            self.canvas_frame.grid_columnconfigure(0, weight=1)  # Atribui um 'peso' de 1 à coluna da esquerda.
            self.canvas_frame.grid_columnconfigure(1, weight=1)  # Atribui um 'peso' de 1 à coluna da direita.

            # Estas configurações asseguram que ambas as colunas tenham a mesma capacidade de
            # expansão e que o layout responda bem a mudanças no tamanho da janela.

            # Atualiza as tarefas pendentes de layout do Canvas.
            # Isso é importante para garantir que todos os elementos gráficos sejam
            # corretamente dimensionados e posicionados antes de realizar mais configurações.
            self.canvas.update_idletasks()

            # Configura a região de rolagem do Canvas para englobar toda a
            # área onde os botões são desenhados.
            # 'self.canvas.bbox("all")' calcula a caixa de delimitação que
            # contém todos os elementos no Canvas,
            # garantindo que a barra de rolagem permita visualizar todos os
            # elementos ao mover-se verticalmente.
            self.canvas.config(scrollregion=self.canvas.bbox("all"))


    # Define o método 'abrir_cadastro' usado para abrir uma janela de
    # cadastro de novas reservas.
    def abrir_cadastro(self):

        # Obtém a data atualmente selecionada no calendário pelo usuário. Este valor
        # será usado para predefinir a data na janela de cadastro.
        data_selecionada = self.cal.get_date()

        # Cria uma nova instância da classe 'JanelaCadastro'. Esta classe é uma janela
        # que permite ao usuário cadastrar uma nova reserva.
        # 'self.janela_sistema' passa a janela principal como parâmetro para que a
        # janela de cadastro possa ser aberta dentro do contexto da aplicação principal.
        # 'self.onibus' passa a instância do ônibus para permitir que a janela de
        # cadastro interaja com os dados das reservas.
        # 'self' passa a instância atual da classe JanelaPrincipal para permitir
        # chamadas de volta para métodos desta classe.
        # 'data_selecionada' é usada para configurar automaticamente a data da
        # reserva na nova janela de cadastro.
        JanelaCadastro(self.janela_sistema,
                       self.onibus,
                       self,
                       data_selecionada)

    # Define o método 'abrir_pesquisa' usado para abrir uma janela de
    # pesquisa de reservas históricas.
    def abrir_pesquisa(self):
        """
        Abre a janela de pesquisa de reservas.
        """
        # Cria uma nova instância da janela de pesquisa
        JanelaPesquisa(self.janela_sistema, self.onibus, self)


# 'tk.Tk()' inicializa a janela principal da interface gráfica.
# Cria a janela principal da aplicação usando Tkinter.
janela_sistema = tk.Tk()

# Cria uma instância da classe 'Onibus', que gerencia os dados
        # relacionados ao ônibus e suas reservas.
# 'Onibus(20)' inicializa o objeto do ônibus com uma
        # capacidade de 20 lugares.
onibus = Onibus(20)

# Cria a interface principal da aplicação, associando a janela do
        # sistema e o objeto do ônibus.
# 'JanelaPrincipal(janela_sistema, onibus)' cria a interface
        # gráfica principal da aplicação.
# Passa a janela Tk ('janela_sistema') para exibir a interface e o
        # objeto 'onibus' para gerenciar as operações relacionadas às reservas.
app = JanelaPrincipal(janela_sistema, onibus)

# Inicia o loop principal da interface gráfica.
# 'mainloop()' é um método Tkinter que entra em um loop
        # contínuo para processar eventos.
janela_sistema.mainloop()