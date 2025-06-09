from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_connection
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'chave-secreta-super-segura'

# ---------------------- HOME ----------------------
@app.route('/')
def home():
    return redirect(url_for('login'))

# ---------------------- LOGIN ALUNO ----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form['email']
    senha = request.form['senha']

    conn = get_connection()
    if not conn:
        return "Erro de conexão com o banco de dados", 500

    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nome, senha, tipo_usuario
        FROM Usuario
        WHERE email = ? AND tipo_usuario = 'aluno'
    """, (email,))
    usuario = cursor.fetchone()

    if usuario and check_password_hash(usuario[2], senha):
        session['usuario_id'] = usuario[0]
        session['usuario_nome'] = usuario[1]
        session['tipo_usuario'] = usuario[3]
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', erro='Email ou senha inválidos.')

# ---------------------- LOGIN FUNCIONÁRIO ----------------------
@app.route('/login-funcionario', methods=['GET', 'POST'])
def login_funcionario():
    if request.method == 'GET':
        return render_template('login_funcionario.html')

    matricula = request.form['matricula'].strip()
    cpf = request.form['cpf'].strip()
    senha = request.form['senha']

    conn = get_connection()
    if not conn:
        return "Erro de conexão com o banco de dados", 500

    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nome, senha
        FROM Usuario
        WHERE tipo_usuario = 'funcionario' AND matricula = ? AND cpf = ?
    """, (matricula, cpf))
    funcionario = cursor.fetchone()

    if funcionario and check_password_hash(funcionario[2], senha):
        session['usuario_id'] = funcionario[0]
        session['usuario_nome'] = funcionario[1]
        session['tipo_usuario'] = 'funcionario'
        return redirect(url_for('painel_funcionario'))

    return render_template('login_funcionario.html', erro='Dados inválidos.')

# ---------------------- CADASTRO ----------------------
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'GET':
        return render_template('cadastro.html')

    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']
    tipo_usuario = request.form['tipo_usuario']
    matricula = request.form.get('matricula')
    cpf = request.form.get('cpf')

    senha_hash = generate_password_hash(senha)

    conn = get_connection()
    if not conn:
        return "Erro de conexão com o banco de dados", 500

    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO Usuario (nome, email, senha, tipo_usuario, matricula, cpf)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nome, email, senha_hash, tipo_usuario, matricula, cpf))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return render_template('cadastro.html', erro='Erro: Dados já cadastrados ou inválidos.')
    finally:
        conn.close()

    return redirect(url_for('login'))

# ---------------------- DASHBOARD ----------------------
@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'aluno':
        return redirect(url_for('login'))
    return render_template('dashboard.html', nome=session.get('usuario_nome'))

# ---------------------- AGENDAR ----------------------
@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    mensagem = None

    if 'usuario_id' not in session or session.get('tipo_usuario') != 'aluno':
        return redirect(url_for('login'))

    conn = get_connection()
    if not conn:
        return "Erro de conexão com o banco de dados", 500

    cursor = conn.cursor()

    if request.method == 'POST':
        setor = request.form['setor']
        data = request.form['data']
        hora = request.form['hora']

        cursor.execute("""
            SELECT COUNT(*) FROM Agendamento
            WHERE data = ? AND hora = ? AND status = 'ativo'
        """, (data, hora))
        existe = cursor.fetchone()[0]

        if existe > 0:
            mensagem = f"Erro: Já existe um agendamento para {data} às {hora}."
        else:
            cursor.execute("""
                INSERT INTO Agendamento (usuario_id, setor, data, hora, status)
                VALUES (?, ?, ?, ?, 'ativo')
            """, (session['usuario_id'], setor, data, hora))
            conn.commit()
            mensagem = "Agendamento realizado com sucesso!"

    cursor.execute("""
        SELECT id, setor, data, hora
        FROM Agendamento
        WHERE usuario_id = ? AND status = 'ativo'
        ORDER BY data DESC, hora DESC
    """, (session['usuario_id'],))
    agendamentos = cursor.fetchall()

    conn.close()

    return render_template(
        'agendar.html',
        agendamentos=agendamentos,
        mensagem=mensagem
    )

# ---------------------- MEUS AGENDAMENTOS ----------------------
@app.route('/meus-agendamentos')
def meus_agendamentos():
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'aluno':
        return redirect(url_for('login'))

    conn = get_connection()
    if not conn:
        return "Erro de conexão com o banco de dados", 500

    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, setor, data, hora
        FROM Agendamento
        WHERE usuario_id = ? AND status = 'ativo'
        ORDER BY data DESC, hora DESC
    """, (session['usuario_id'],))
    agendamentos = cursor.fetchall()

    conn.close()

    return render_template('meus_agendamentos.html', agendamentos=agendamentos)

# ---------------------- EDITAR AGENDAMENTO ----------------------
@app.route('/editar-agendamento/<int:id>', methods=['GET', 'POST'])
def editar_agendamento(id):
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'aluno':
        return redirect(url_for('login'))

    conn = get_connection()
    if not conn:
        return "Erro de conexão com o banco de dados", 500

    cursor = conn.cursor()

    if request.method == 'POST':
        setor = request.form['setor']
        data = request.form['data']
        hora = request.form['hora']

        cursor.execute("""
            UPDATE Agendamento
            SET setor = ?, data = ?, hora = ?
            WHERE id = ? AND usuario_id = ?
        """, (setor, data, hora, id, session['usuario_id']))
        conn.commit()
        conn.close()

        return redirect(url_for('meus_agendamentos'))

    cursor.execute("""
        SELECT setor, data, hora
        FROM Agendamento
        WHERE id = ? AND usuario_id = ?
    """, (id, session['usuario_id']))
    agendamento = cursor.fetchone()
    conn.close()

    if agendamento:
        return render_template('editar_agendamento.html', agendamento=agendamento, id=id)
    else:
        return redirect(url_for('meus_agendamentos'))

# ---------------------- EXCLUIR AGENDAMENTO ----------------------
@app.route('/excluir-agendamento/<int:id>')
def excluir_agendamento(id):
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'aluno':
        return redirect(url_for('login'))

    conn = get_connection()
    if not conn:
        return "Erro de conexão com o banco de dados", 500

    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM Agendamento
        WHERE id = ? AND usuario_id = ?
    """, (id, session['usuario_id']))
    conn.commit()
    conn.close()

    return redirect(url_for('meus_agendamentos'))

# ---------------------- FILA ----------------------
@app.route('/fila')
def fila():
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'aluno':
        return redirect(url_for('login'))

    data_param = request.args.get('data')
    data_ref = datetime.strptime(data_param, "%Y-%m-%d").date() if data_param else datetime.now().date()

    conn = get_connection()
    if not conn:
        return "Erro de conexão com o banco de dados", 500

    cursor = conn.cursor()
    cursor.execute("""
        SELECT hora, setor, u.nome
        FROM Agendamento a
        JOIN Usuario u ON a.usuario_id = u.id
        WHERE a.data = ? AND a.status = 'ativo'
        ORDER BY hora
    """, (data_ref,))
    agendados = cursor.fetchall()

    horarios_possiveis = []
    hora = datetime.strptime('08:00', '%H:%M')
    while hora.strftime('%H:%M') <= '20:30':
        horarios_possiveis.append(hora.strftime('%H:%M'))
        minutos = hora.minute + 30
        horas = hora.hour + (minutos // 60)
        minutos = minutos % 60
        hora = hora.replace(hour=horas, minute=minutos)

    horarios_ocupados = [h.strftime('%H:%M') for h, _, _ in agendados]
    horarios_disponiveis = [h for h in horarios_possiveis if h not in horarios_ocupados]

    conn.close()

    return render_template(
        'fila.html',
        agendados=agendados,
        horarios_disponiveis=horarios_disponiveis,
        data_busca=data_ref.strftime('%Y-%m-%d')
    )

# ---------------------- PAINEL FUNCIONÁRIO ----------------------
@app.route('/painel-funcionario')
def painel_funcionario():
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'funcionario':
        return redirect(url_for('login_funcionario'))

    mes = request.args.get('mes', type=int)
    ano = request.args.get('ano', type=int)
    filtro_aplicado = False
    agendamentos_por_dia = {}

    nomes_meses = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }

    try:
        if mes and ano:
            filtro_aplicado = True
            conn = get_connection()
            if not conn:
                return "Erro de conexão com o banco de dados", 500

            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.data, a.hora, a.setor, u.nome
                FROM Agendamento a
                JOIN Usuario u ON a.usuario_id = u.id
                WHERE a.status = 'ativo' AND MONTH(a.data) = ? AND YEAR(a.data) = ?
                ORDER BY a.data, a.hora
            """, (mes, ano))
            rows = cursor.fetchall()

            for data, hora, setor, nome in rows:
                data_str = data.strftime('%d/%m/%Y')
                if data_str not in agendamentos_por_dia:
                    agendamentos_por_dia[data_str] = []
                agendamentos_por_dia[data_str].append({
                    'nome': nome,
                    'setor': setor,
                    'hora': hora.strftime('%H:%M')
                })

        return render_template(
            'painel_funcionario.html',
            agendamentos_por_dia=agendamentos_por_dia,
            filtro_aplicado=filtro_aplicado,
            mes_atual=mes,
            ano_atual=ano,
            nomes_meses=nomes_meses
        )
    except Exception as e:
        return f'Erro ao carregar painel: {str(e)}'
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# ---------------------- LOGOUT ----------------------
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------------------- MAIN ----------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
