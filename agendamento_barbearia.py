import mysql.connector
from datetime import datetime, time

def solicitar_data_hora(cursor):
    while True:
        data_str = input("Digite a data do agendamento (dd/mm/aaaa): ").strip()
        hora_str = input("Digite o horário (hh:mm): ").strip()
        try:
            data_hora = datetime.strptime(f"{data_str} {hora_str}", "%d/%m/%Y %H:%M")
            agora = datetime.now()
            dia_semana = data_hora.weekday()  # 0 = segunda, 6 = domingo
            hora = data_hora.time()

            if data_hora < agora:
                print("❌ Não é possível agendar para datas ou horários passados.")
                continue

            if dia_semana in [0, 6]:
                print("❌ Agendamentos não são permitidos aos domingos ou segundas-feiras.")
                continue

            manha_inicio = time(8, 0)
            manha_fim = time(12, 0)
            tarde_inicio = time(14, 0)
            tarde_fim = time(21, 0)

            if not (manha_inicio <= hora <= manha_fim or tarde_inicio <= hora <= tarde_fim):
                print("❌ Horário inválido. Permitido apenas das 08:00 às 12:00 ou das 14:00 às 21:00.")
                continue

            # Somente agora, após todas as validações de input, verificamos o banco
            cursor.execute("SELECT COUNT(*) FROM agendamentos WHERE data_hora = %s", (data_hora,))
            if cursor.fetchone()[0] > 0:
                print("❌ Já existe um agendamento para este horário. Escolha outro.")
                continue

            return data_hora  # Tudo válido

        except ValueError:
            print("❌ Formato inválido. Use dd/mm/aaaa e hh:mm.")


# --- Configurações do Banco de Dados ---
DB_HOST = "localhost"
DB_USER = "root"  # Substitua pelo seu usuário do MySQL
DB_PASSWORD = "root"  # Substitua pela sua senha do MySQL
DB_NAME = "barbearia"

def conectar_banco():
    """Tenta conectar ao banco de dados MySQL."""
    try:
        conexao = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        print("✅Conexão ao banco de dados estabelecida com sucesso!")
        return conexao
    except mysql.connector.Error as erro:
        print(f"Erro ao conectar ao MySQL: {erro}")
        return None
# ----------- funções agendamento---------
#----------------- editar agendamento1
def editar_agendamento():
    """Edita um agendamento no banco de dados."""
    conexao = conectar_banco()
    if not conexao:
        print("❌ Não foi possível conectar ao banco de dados.")
        return

    cursor = conexao.cursor()

    try:
        id_agendamento = int(input("Digite o ID do agendamento a ser editado: "))

        # Verifica se o agendamento existe e obtém dados atuais
        cursor.execute("""
            SELECT a.id_agendamentos, c.nome_cliente, a.data_hora, a.tipo_pagamento
            FROM agendamentos a
            JOIN clientes c ON a.cliente_id = c.id_clientes
            WHERE a.id_agendamentos = %s
        """, (id_agendamento,))
        dados = cursor.fetchone()

        if not dados:
            print("Agendamento não encontrado.")
            return

        print(f"\nEditando Agendamento ID {id_agendamento}")
        print(f"Cliente atual: {dados[1]}")
        print(f"Data e Hora atual: {dados[2]}")
        print(f"Tipo de pagamento atual: {dados[3]}")

        novo_nome = input("Novo nome do cliente (ou deixe em branco para manter): ").strip()
        nova_data_str = input("Nova data (dd/mm/aaaa) (ou deixe em branco): ").strip()
        nova_hora_str = input("Nova hora (hh:mm) (ou deixe em branco): ").strip()
        novo_tipo_pagamento = input("Novo tipo de pagamento (ou deixe em branco): ").strip()

        sql = "UPDATE agendamentos SET "
        valores = []

        if novo_nome:
            cursor.execute("SELECT id_clientes FROM clientes WHERE nome_cliente = %s", (novo_nome,))
            cliente = cursor.fetchone()
            if cliente:
                sql += "cliente_id = %s, "
                valores.append(cliente[0])
            else:
                print("⚠️ Cliente não encontrado. Mantendo cliente atual.")

        if nova_data_str and nova_hora_str:
            try:
                data_obj = datetime.datetime.strptime(f"{nova_data_str} {nova_hora_str}", "%d/%m/%Y %H:%M")
                hoje = datetime.datetime.now()
                dia_semana = data_obj.weekday()
                hora = data_obj.time()

                if data_obj < hoje:
                    print("Data/hora no passado. Não será alterado.")
                elif dia_semana in [0, 6]:
                    print("Domingo ou segunda-feira. Não será alterado.")
                elif not (datetime.time(8, 0) <= hora <= datetime.time(12, 0) or datetime.time(14, 0) <= hora <= datetime.time(21, 0)):
                    print("Horário fora do permitido. Não será alterado.")
                else:
                    # Verifica se já existe agendamento nesse horário
                    cursor.execute("SELECT COUNT(*) FROM agendamentos WHERE data_hora = %s AND id_agendamentos != %s", (data_obj, id_agendamento))
                    if cursor.fetchone()[0] > 0:
                        print("Esse horário já está ocupado. Não será alterado.")
                    else:
                        sql += "data_hora = %s, "
                        valores.append(data_obj)
            except ValueError:
                print("❌Formato de data/hora inválido. Não será alterado.")

        if novo_tipo_pagamento:
            sql += "tipo_pagamento = %s, "
            valores.append(novo_tipo_pagamento)

        if valores:
            sql = sql.rstrip(', ') + " WHERE id_agendamentos = %s"
            valores.append(id_agendamento)
            cursor.execute(sql, valores)
            conexao.commit()
            print("✅ Agendamento atualizado com sucesso.")
        else:
            print("Nenhuma alteração feita nos dados principais.")

        # --- Atualiza Serviços ---
        cursor.execute("SELECT id_servicos, nome_servicos FROM servicos")
        servicos = cursor.fetchall()
        print("\nServiços disponíveis:")
        for s in servicos:
            print(f"{s[0]} - {s[1]}")

        servico_ids = input("Digite os IDs dos novos serviços (ou deixe vazio): ").strip()
        cursor.execute("DELETE FROM agendamento_servico WHERE agendamento_id = %s", (id_agendamento,))
        if servico_ids:
            for sid in servico_ids.split(','):
                sid = sid.strip()
                if sid.isdigit():
                    cursor.execute("INSERT INTO agendamento_servico (agendamento_id, servico_id) VALUES (%s, %s)", (id_agendamento, int(sid)))

        # --- Atualiza Produtos ---
        cursor.execute("SELECT id_produtos, nome_produtos FROM produtos")
        produtos = cursor.fetchall()
        print("\nProdutos disponíveis:")
        for p in produtos:
            print(f"{p[0]} - {p[1]}")

        produto_ids = input("Digite os IDs dos novos produtos (ou '0' para nenhum): ").strip()
        cursor.execute("DELETE FROM agendamento_produto WHERE agendamento_id = %s", (id_agendamento,))
        if produto_ids != '0':
            for pid in produto_ids.split(','):
                pid = pid.strip()
                if pid.isdigit():
                    cursor.execute("INSERT INTO agendamento_produto (agendamento_id, produto_id) VALUES (%s, %s)", (id_agendamento, int(pid)))

        conexao.commit()
        print("✅Serviços e produtos atualizados com sucesso.")

    except mysql.connector.Error as erro:
        print(f"Erro ao editar agendamento: {erro}")
        conexao.rollback()
    except ValueError:
        print("❌ID inválido. Digite um número inteiro.")
    finally:
        cursor.close()
        conexao.close()

#-------------------- visualizar_agendamento1
def visualizar_agendamento():
    conexao = conectar_banco()
    if conexao:
        cursor = conexao.cursor()
        try:
            cursor.execute("""
                SELECT
                    a.id_agendamentos,
                    c.nome_cliente,
                    a.data_hora,
                    a.tipo_pagamento,
                    GROUP_CONCAT(DISTINCT s.nome_servicos SEPARATOR ', ') AS servicos_nomes,
                    GROUP_CONCAT(DISTINCT p.nome_produtos SEPARATOR ', ') AS produtos_nomes
                FROM agendamentos a
                JOIN clientes c ON a.cliente_id = c.id_clientes
                LEFT JOIN agendamento_servico ags ON a.id_agendamentos = ags.agendamento_id
                LEFT JOIN servicos s ON ags.servico_id = s.id_servicos
                LEFT JOIN agendamento_produto agp ON a.id_agendamentos = agp.agendamento_id
                LEFT JOIN produtos p ON agp.produto_id = p.id_produtos
                GROUP BY a.id_agendamentos
                ORDER BY a.data_hora
            """)
            agendamentos = cursor.fetchall()

            if not agendamentos:
                print("Não há agendamentos cadastrados.")
                return

            print("\n--- Agendamentos ---")
            for agendamento in agendamentos:
                print(f"\nID: {agendamento[0]}")
                print(f"Cliente: {agendamento[1]}")
                print(f"Data e Hora: {agendamento[2]}")
                print(f"Tipo de Pagamento: {agendamento[3]}")
                print("Serviços:", agendamento[4] if agendamento[4] else "Nenhum") # agendamento[4] é servicos_nomes
                print("Produtos:", agendamento[5] if agendamento[5] else "Nenhum") # agendamento[5] é produtos_nomes
                print("-" * 30)

        except mysql.connector.Error as erro:
            print(f"Erro ao visualizar agendamentos: {erro}")
        finally:
            cursor.close()
            conexao.close()
    else:
        print("Erro ao conectar ao banco de dados.")

#-------------------- cadastrar agendamento1
def cadastrar_agendamento():
    conexao = conectar_banco()
    if not conexao:
        print("Erro ao conectar ao banco de dados.")
        return

    cursor = conexao.cursor()

    try:
        # Seleciona clientes
        cursor.execute("SELECT id_clientes, nome_cliente FROM clientes")
        clientes = cursor.fetchall()
        if not clientes:
            print("Não há clientes cadastrados.")
            return

        print("\n--- Clientes ---")
        for c in clientes:
            print(f"{c[0]} - {c[1]}")
        cliente_id = int(input("Digite o ID do cliente: "))

        # Solicita data/hora e tipo de pagamento
        data_hora = solicitar_data_hora(cursor)
        tipo_pagamento = input("Digite o tipo de pagamento (Dinheiro, Cartão, Pix): ").strip()

        # Insere o agendamento
        cursor.execute(
            "INSERT INTO agendamentos (cliente_id, data_hora, tipo_pagamento) VALUES (%s, %s, %s)",
            (cliente_id, data_hora, tipo_pagamento)
        )
        agendamento_id = cursor.lastrowid

        while True:
            # Coletar serviços
            cursor.execute("SELECT id_servicos, nome_servicos FROM servicos")
            servicos = cursor.fetchall()
            servico_ids = []
            if servicos:
                print("\n--- Serviços ---")
                for s in servicos:
                    print(f"{s[0]} - {s[1]}")
                entrada_servicos = input("Escolha os IDs dos serviços (separados por vírgula, ou deixe em branco): ").strip()
                if entrada_servicos:
                    servico_ids = [int(sid.strip()) for sid in entrada_servicos.split(',') if sid.strip().isdigit()]

            # Coletar produtos
            cursor.execute("SELECT id_produtos, nome_produtos FROM produtos")
            produtos = cursor.fetchall()
            produto_ids = []
            if produtos:
                print("\n--- Produtos ---")
                for p in produtos:
                    print(f"{p[0]} - {p[1]}")
                entrada_produtos = input("Escolha os IDs dos produtos (separados por vírgula, ou deixe em branco): ").strip()
                if entrada_produtos:
                    produto_ids = [int(pid.strip()) for pid in entrada_produtos.split(',') if pid.strip().isdigit()]

            # Validação: pelo menos um produto ou serviço
            if servico_ids or produto_ids:
                break  # Ok, sai do loop
            else:
                print("⚠️ Você deve selecionar pelo menos um produto ou serviço. Tente novamente.\n")

        # Inserir serviços
        for sid in servico_ids:
            cursor.execute(
                "INSERT INTO agendamento_servico (agendamento_id, servico_id) VALUES (%s, %s)",
                (agendamento_id, sid)
            )

        # Inserir produtos
        for pid in produto_ids:
            cursor.execute(
                "INSERT INTO agendamento_produto (agendamento_id, produto_id) VALUES (%s, %s)",
                (agendamento_id, pid)
            )

        conexao.commit()
        print("✅ Agendamento realizado com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao cadastrar agendamento: {e}")
        conexao.rollback()
    finally:
        cursor.close()
        conexao.close()

# ------------agendamento1
def deletar_agendamento():
    """Deleta um ou mais agendamentos do banco de dados."""
    conexao = conectar_banco()
    if not conexao:
        print("Erro ao conectar ao banco de dados.")
        return

    cursor = conexao.cursor()
    try:
        cursor.execute("""
            SELECT a.id_agendamentos, c.nome_cliente, a.data_hora
            FROM agendamentos a
            JOIN clientes c ON a.cliente_id = c.id_clientes
        """)
        agendamentos = cursor.fetchall()

        if not agendamentos:
            print("Não há agendamentos cadastrados.")
            return

        print("\n--- Agendamentos ---")
        for ag in agendamentos:
            print(f"{ag[0]} - {ag[1]} em {ag[2].strftime('%d/%m/%Y %H:%M')}")

        ids = input("Digite os IDs dos agendamentos a serem deletados (separados por vírgula): ").split(',')
        ids = [int(i.strip()) for i in ids]

        for aid in ids:
            try:
                cursor.execute("DELETE FROM agendamento_servico WHERE agendamento_id = %s", (aid,))
                cursor.execute("DELETE FROM agendamento_produto WHERE agendamento_id = %s", (aid,))
                cursor.execute("DELETE FROM agendamentos WHERE id_agendamentos = %s", (aid,))
            except mysql.connector.Error as e:
                print(f"Erro ao deletar agendamento {aid}: {e}")

        conexao.commit()
        print("✅ Agendamentos excluídos com sucesso.")

    except ValueError:
        print("❌Entrada inválida. Use apenas números separados por vírgula.")
    finally:
        cursor.close()
        conexao.close()

#submenu agendamento
def submenu_agendamento():
    """Submenu para operações de agendamento."""
    while True:
        print("\n--- Submenu Agendamento ---")
        print("1. Criar Agendamento ➕")
        print("2. Deletar Agendamento 🗑️")
        print("3. Editar Agendamento ✏️")
        print("4. Visualizar Agendamentos 👁️")
        print("5. Voltar ↩️")
        escolha = input("Escolha uma opção: ")
        if escolha == "1":
            cadastrar_agendamento()
        elif escolha == "2":
            deletar_agendamento()
        elif escolha == "3":
            editar_agendamento()
        elif escolha == "4":
            visualizar_agendamento()
        elif escolha == "5":
            return
        else:
            print("❌Opção inválida, tente novamente.")
# -------------- Produto1
def cadastrar_produto():
    """Cadastra um novo produto no banco de dados."""
    conexao = conectar_banco()
    if not conexao:
        print("Erro ao conectar ao banco de dados.")
        return

    cursor = conexao.cursor()
    try:
        nome = input("Digite o nome do produto: ").strip()
        preco_str = input("Digite o preço do produto (ex: 19.90): ").strip()

        # Valida o nome
        if not nome:
            print("❌ O nome do produto não pode estar vazio.")
            return

        # Valida o preço
        try:
            preco = float(preco_str)
            if preco <= 0:
                print("❌ O preço deve ser maior que zero.")
                return
        except ValueError:
            print("❌ Preço inválido. Digite um número, por exemplo: 12.50")
            return

        # Insere no banco
        cursor.execute(
            "INSERT INTO produtos (nome_produtos, preco_produtos) VALUES (%s, %s)",
            (nome, preco)
        )
        conexao.commit()
        print("✅ Produto cadastrado com sucesso!")

    except mysql.connector.Error as erro:
        print(f"❌ Erro ao cadastrar produto: {erro}")
        conexao.rollback()
    finally:
        cursor.close()
        conexao.close()
#-----------------------------produto1
def deletar_produto():
    """Deleta um produto do banco de dados."""
    conexao = conectar_banco()
    if not conexao:
        print("Erro ao conectar ao banco de dados.")
        return

    cursor = conexao.cursor()
    try:
        # Exibe os produtos disponíveis
        cursor.execute("SELECT id_produtos, nome_produtos, preco_produtos FROM produtos")
        produtos = cursor.fetchall()

        if not produtos:
            print("Não há produtos cadastrados.")
            return

        print("\n--- Produtos Cadastrados ---")
        for produto in produtos:
            print(f"{produto[0]} - {produto[1]} (R${produto[2]:.2f})")

        id_produto = input("Digite o ID do produto que deseja deletar: ").strip()
        if not id_produto.isdigit():
            print("❌ID inválido.")
            return

        id_produto = int(id_produto)

        # Verifica se o produto existe
        cursor.execute("SELECT * FROM produtos WHERE id_produtos = %s", (id_produto,))
        if not cursor.fetchone():
            print("Produto não encontrado.")
            return

        # Exclui o produto
        cursor.execute("DELETE FROM produtos WHERE id_produtos = %s", (id_produto,))
        conexao.commit()
        print("✅ Produto deletado com sucesso.")

    except mysql.connector.Error as erro:
        print(f"❌ Erro ao deletar produto: {erro}")
        conexao.rollback()
    finally:
        cursor.close()
        conexao.close()
#------------------ Produto1

def editar_produto():
    """Edita os dados de um produto no banco de dados."""
    conexao = conectar_banco()
    if not conexao:
        print("Erro ao conectar ao banco de dados.")
        return

    cursor = conexao.cursor()
    try:
        # Lista os produtos existentes
        cursor.execute("SELECT id_produtos, nome_produtos, preco_produtos FROM produtos")
        produtos = cursor.fetchall()

        if not produtos:
            print("Não há produtos cadastrados.")
            return

        print("\n--- Produtos Cadastrados ---")
        for produto in produtos:
            print(f"{produto[0]} - {produto[1]} (R${produto[2]:.2f})")

        id_produto = input("Digite o ID do produto que deseja editar: ").strip()
        if not id_produto.isdigit():
            print("❌ID inválido.")
            return

        id_produto = int(id_produto)

        cursor.execute("SELECT * FROM produtos WHERE id_produtos = %s", (id_produto,))
        if not cursor.fetchone():
            print("Produto não encontrado.")
            return

        novo_nome = input("Novo nome do produto (ou pressione Enter para manter o atual): ").strip()
        novo_preco = input("Novo preço do produto (ou pressione Enter para manter o atual): ").strip()

        campos = []
        valores = []

        if novo_nome:
            campos.append("nome_produtos = %s")
            valores.append(novo_nome)

        if novo_preco:
            try:
                preco_float = float(novo_preco)
                campos.append("preco_produtos = %s")
                valores.append(preco_float)
            except ValueError:
                print("❌Preço inválido. Deve ser um número.")
                return

        if not campos:
            print("Nenhuma alteração feita.")
            return

        sql = f"UPDATE produtos SET {', '.join(campos)} WHERE id_produtos = %s"
        valores.append(id_produto)
        cursor.execute(sql, valores)
        conexao.commit()
        print("✅ Produto atualizado com sucesso.")

    except mysql.connector.Error as erro:
        print(f"❌ Erro ao editar produto: {erro}")
        conexao.rollback()
    finally:
        cursor.close()
        conexao.close()
#----------------------produto1
def visualizar_produtos():
    """Exibe todos os produtos cadastrados no banco de dados."""
    conexao = conectar_banco()
    if not conexao:
        print("Erro ao conectar ao banco de dados.")
        return

    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT id_produtos, nome_produtos, preco_produtos FROM produtos")
        produtos = cursor.fetchall()

        if not produtos:
            print("Não há produtos cadastrados.")
            return

        print("\n--- Produtos Cadastrados ---")
        for produto in produtos:
            print(f"ID: {produto[0]}")
            print(f"Nome: {produto[1]}")
            print(f"Preço: R${produto[2]:.2f}")
            print("-" * 20)

    except mysql.connector.Error as erro:
        print(f"Erro ao visualizar produtos: {erro}")
    finally:
        cursor.close()
        conexao.close()
        #------------------ subprodutos
def submenu_produtos():
    while True:
        print("\n--- Submenu Produtos ---")
        print("1. Cadastrar Produto 📦")
        print("2. Editar Produto ✍️")
        print("3. Deletar Produto 🗑️")
        print("4. Visualizar Produtos 📊")
        print("5. Voltar ↩️")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == '1':
            cadastrar_produto()
        elif opcao == '2':
            editar_produto()
        elif opcao == '3':
            deletar_produto()
        elif opcao == '4':
            visualizar_produtos()
        elif opcao == '5':
            break
        else:
            print("❌Opção inválida. Tente novamente.")

#------------------------ servico1
# --- Funções de Serviço ---
def cadastrar_servico():
    """Cadastra um novo serviço no banco de dados."""
    conexao = conectar_banco()
    if not conexao:
        print("❌Erro ao conectar ao banco.")
        return

    cursor = conexao.cursor()
    try:
        nome = input("Digite o nome do serviço: ").strip()
        preco = float(input("Digite o preço do serviço: "))

        cursor.execute(
            "INSERT INTO servicos (nome_servicos, preco_servicos) VALUES (%s, %s)",
            (nome, preco)
        )
        conexao.commit()
        print("✅Serviço cadastrado com sucesso!")
    except mysql.connector.Error as erro:
        print(f"❌Erro ao cadastrar serviço: {erro}")
        conexao.rollback()
    except ValueError:
        print("❌Preço inválido. Use apenas números.")
    finally:
        cursor.close()
        conexao.close()
#----------------------servico1

def editar_servico():
    """Edita os dados de um serviço no banco de dados."""
    conexao = conectar_banco()
    if not conexao:
        print("Erro ao conectar ao banco.")
        return

    cursor = conexao.cursor()
    try:
        id_servico = int(input("Digite o ID do serviço a ser editado: "))

        cursor.execute("SELECT * FROM servicos WHERE id_servicos = %s", (id_servico,))
        if cursor.fetchone() is None:
            print("Serviço não encontrado.")
            return

        novo_nome = input("Novo nome do serviço (ou pressione Enter para manter): ").strip()
        novo_preco = input("Novo preço do serviço (ou pressione Enter para manter): ").strip()

        sql = "UPDATE servicos SET "
        valores = []

        if novo_nome:
            sql += "nome_servicos = %s, "
            valores.append(novo_nome)

        if novo_preco:
            try:
                preco_float = float(novo_preco)
                sql += "preco_servicos = %s, "
                valores.append(preco_float)
            except ValueError:
                print("❌Preço inválido.")
                return

        if valores:
            sql = sql.rstrip(', ') + " WHERE id_servicos = %s"
            valores.append(id_servico)
            cursor.execute(sql, valores)
            conexao.commit()
            print("✅Serviço atualizado com sucesso!")
        else:
            print("❌Nenhuma alteração feita.")

    except mysql.connector.Error as erro:
        print(f"Erro ao editar serviço: {erro}")
        conexao.rollback()
    except ValueError:
        print("❌ID inválido.")
    finally:
        cursor.close()
        conexao.close()
#----------------- servico1

def visualizar_servicos():
    """Exibe todos os serviços cadastrados no banco de dados."""
    conexao = conectar_banco()
    if not conexao:
        print("Erro ao conectar ao banco de dados.")
        return

    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT id_servicos, nome_servicos, preco_servicos FROM servicos")
        servicos = cursor.fetchall()

        if not servicos:
            print("Não há serviços cadastrados.")
            return

        print("\n--- Serviços Cadastrados ---")
        for servico in servicos:
            print(f"ID: {servico[0]}")
            print(f"Nome: {servico[1]}")
            print(f"Preço: R${servico[2]:.2f}")
            print("-" * 20)

    except mysql.connector.Error as erro:
        print(f"Erro ao visualizar serviços: {erro}")
    finally:
        cursor.close()
        conexao.close()

#----------------------servico1        
def deletar_servico():
    """Deleta um ou mais serviços do banco de dados."""
    conexao = conectar_banco()
    if not conexao:
        print("Erro ao conectar ao banco de dados.")
        return

    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT id_servicos, nome_servicos FROM servicos")
        servicos = cursor.fetchall()

        if not servicos:
            print("Não há serviços cadastrados.")
            return

        print("\n--- Serviços Cadastrados ---")
        for s in servicos:
            print(f"{s[0]} - {s[1]}")

        ids = input("Digite os IDs dos serviços a serem deletados (separados por vírgula): ").split(',')
        ids = [int(i.strip()) for i in ids]

        for sid in ids:
            try:
                cursor.execute("DELETE FROM servicos WHERE id_servicos = %s", (sid,))
            except mysql.connector.IntegrityError as e:
                if e.errno == 1451:
                    print(f"❌ Serviço ID {sid} não pode ser deletado porque está vinculado a agendamentos.")
                else:
                    print(f"Erro ao deletar serviço {sid}: {e}")

        conexao.commit()
        print("✅ Processo de exclusão de serviços finalizado.")
    except ValueError:
        print("❌Entrada inválida. Use apenas números separados por vírgula.")
    finally:
        cursor.close()
        conexao.close()


#--------------------- subservico
def submenu_servico():
    while True:
        print("\n--- Submenu Serviço ---")
        print("1. Cadastrar Serviço ✨")
        print("2. Deletar Serviço 🗑️o")
        print("3. Editar Serviço ✍️")
        print("4. Visualizar Serviços 📋")
        print("5. Voltar ↩️")
        escolha = input("Escolha uma opção: ")
        if escolha == "1":
            cadastrar_servico()
        elif escolha == "2":
            deletar_servico()
        elif escolha == "3":
            editar_servico()
        elif escolha == "4":
            visualizar_servicos()
        elif escolha == "5":
            return
        else:
            print("❌Opção inválida, tente novamente.")
#----------------------cliente1
# --- Funções de Cliente ---
def cadastrar_cliente():
    conexao = conectar_banco()
    if not conexao:
        print("Erro ao conectar ao banco.")
        return

    cursor = conexao.cursor()
    try:
        nome = input("Nome do cliente: ").strip()
        telefone = input("Telefone do cliente: ").strip()

        cursor.execute(
            "INSERT INTO clientes (nome_cliente, telefone_cliente) VALUES (%s, %s)",
            (nome, telefone)
        )
        conexao.commit()
        print("✅Cliente cadastrado com sucesso!")
    except mysql.connector.Error as erro:
        print(f"Erro ao cadastrar cliente: {erro}")
    finally:
        cursor.close()
        conexao.close()
#-------------------cliente1

def deletar_clientes():
    """Deleta um ou mais clientes do banco de dados."""
    conexao = conectar_banco()
    if not conexao:
        print("Não foi possível conectar ao banco de dados.")
        return

    cursor = conexao.cursor()

    try:
        cursor.execute("SELECT id_clientes, nome_cliente FROM clientes")
        clientes = cursor.fetchall()
        if not clientes:
            print("Não há clientes cadastrados.")
            return

        print("\n--- Clientes Cadastrados ---")
        for cliente in clientes:
            print(f"{cliente[0]} - {cliente[1]}")

        ids = input("Digite os IDs dos clientes a serem deletados (separados por vírgula): ").strip().split(',')
        ids = [int(i.strip()) for i in ids]

        for cliente_id in ids:
            try:
                cursor.execute("DELETE FROM clientes WHERE id_clientes = %s", (cliente_id,))
            except mysql.connector.IntegrityError as e:
                if e.errno == 1451:  # Código de erro de restrição de chave estrangeira
                    print(f"❌ Não é possível deletar o cliente com ID {cliente_id} porque há agendamentos vinculados.")
                    print("   Para excluir esse cliente, primeiro exclua ou transfira os agendamentos relacionados.\n")
                else:
                    print(f"Erro ao deletar cliente {cliente_id}: {e}")

        conexao.commit()
        print("✅ Processo de exclusão finalizado.")

    except ValueError:
        print("❌Entrada inválida. Digite apenas números separados por vírgula.")
    finally:
        cursor.close()
        conexao.close()




#------------------cliente1
def editar_cliente():
    conexao = conectar_banco()
    if not conexao:
        print("Erro ao conectar ao banco.")
        return

    cursor = conexao.cursor()
    try:
        id_cliente = input("ID do cliente que deseja editar: ").strip()

        cursor.execute("SELECT * FROM clientes WHERE id_clientes = %s", (id_cliente,))
        cliente = cursor.fetchone()
        if not cliente:
            print("Cliente não encontrado.")
            return

        novo_nome = input("Novo nome (deixe em branco para manter): ").strip()
        novo_telefone = input("Novo telefone (deixe em branco para manter): ").strip()

        if novo_nome:
            cursor.execute("UPDATE clientes SET nome_cliente = %s WHERE id_clientes = %s", (novo_nome, id_cliente))
        if novo_telefone:
            cursor.execute("UPDATE clientes SET telefone_cliente = %s WHERE id_clientes = %s", (novo_telefone, id_cliente))

        conexao.commit()
        print("✅Cliente atualizado com sucesso.")
    except mysql.connector.Error as erro:
        print(f"Erro ao editar cliente: {erro}")
    finally:
        cursor.close()
        conexao.close()
#------------cliente1

def visualizar_clientes():
    conexao = conectar_banco()
    if not conexao:
        print("Erro ao conectar ao banco.")
        return

    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT id_clientes, nome_cliente, telefone_cliente FROM clientes")
        clientes = cursor.fetchall()

        if not clientes:
            print("Nenhum cliente cadastrado.")
            return

        print("\n--- Lista de Clientes ---")
        for cliente in clientes:
            print(f"ID: {cliente[0]} | Nome: {cliente[1]} | Telefone: {cliente[2]}")
    except mysql.connector.Error as erro:
        print(f"Erro ao visualizar clientes: {erro}")
    finally:
        cursor.close()
        conexao.close()
#----------------subcliente
def submenu_cliente():
    """Submenu para operações de cliente."""
    while True:
        print("\n--- Submenu Cliente ---")
        print("1. Cadastrar Cliente ➕")
        print("2. Deletar Cliente 🗑️")
        print("3. Editar Cliente ✏️e")
        print("4. Visualizar Clientes 👁️")
        print("5. Voltar ↩️")
        escolha = input("Escolha uma opção: ")
        if escolha == "1":
            cadastrar_cliente()
        elif escolha == "2":
            deletar_clientes()
        elif escolha == "3":
            editar_cliente()
        elif escolha == "4":
            visualizar_clientes()
        elif escolha == "5":
            return
        else:
            print("❌Opção inválida, tente novamente.")
#------------------menuprincipal
def menu_principal():
    """Função principal que exibe o menu e direciona para as funções."""
    while True:
        print("\n--- Menu Principal ---")
        print("1. Agendamentos 📅")
        print("2. Produtos 🛍️")
        print("3. Serviços ✂️")
        print("4. Clientes  👥 ")
        print("5. Sair 🚪")
        escolha = input("Escolha uma opção: ")
        if escolha == "1":
            submenu_agendamento()
        elif escolha == "2":
            submenu_produtos()
        elif escolha == "3":
            submenu_servico()
        elif escolha == "4":
            submenu_cliente()
        elif escolha == "5":
            print("Saindo do sistema...")
            break
        else:
            print("❌Opção inválida, tente novamente.")

if __name__ == "__main__":
    menu_principal()