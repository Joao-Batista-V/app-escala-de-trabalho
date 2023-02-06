from flask import Flask, render_template, url_for, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from time import sleep
import calendar
from datetime import datetime

# Configuração para o aplicativo Flask
app = Flask(__name__)

#  Criação do Banco de dados com o nome db_Users
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db_Users.sqlite3'  # 'db_' significa database

# Configuração da chave secreta
app.config['SECRET_KEY'] = 'secret'

# Configuração para a autenticação de usuário
login_manager = LoginManager()
login_manager.init_app(app)

# Configuração do Banco de dados
db = SQLAlchemy(app)


# Criação da tabela User
@login_manager.user_loader  # usado para recarregar o id do usuário autenticado
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


# Configurações para o Banco de dados e criação dda tabela User
class User(db.Model, UserMixin):
    __tablename__ = "Usuarios"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    user = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Integer, nullable=False, default=1)  # Verifica se o funcionário está habilitado

    def __init__(self, name, user, password, status):
        self.name = name
        self.user = user
        self.password = generate_password_hash(password)
        self.status = status


# Criação da tabela db_Funcionarios
class tb_Funcionarios(db.Model):  # 'tb_' significa table
    __tablename__ = "Funcionarios"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    nome = db.Column(db.String(50), nullable=False)  # Nome do funcionário
    status = db.Column(db.Integer, nullable=False, default=1)  # Verifica se o funcionário está habilitado

    def __init__(self, nome, status):
        self.nome = nome
        self.status = status


# Escala da semana 1
class tb_Semana(db.Model):
    __tablename__ = "Semana 1"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    turno_db = db.Column(db.String(20))
    horario_db = db.Column(db.String(20))
    dom_db = db.Column(db.String(20))
    seg_db = db.Column(db.String(20))
    ter_db = db.Column(db.String(20))
    qua_db = db.Column(db.String(20))
    qui_db = db.Column(db.String(20))
    sex_db = db.Column(db.String(20))
    sab_db = db.Column(db.String(20))

    def __init__(self, turno_db, horario_db, dom_db, seg_db, ter_db, qua_db, qui_db, sex_db, sab_db):
        self.turno_db = turno_db
        self.horario_db = horario_db
        self.dom_db = dom_db
        self.seg_db = seg_db
        self.ter_db = ter_db
        self.qua_db = qua_db
        self.qui_db = qui_db
        self.sex_db = sex_db
        self.sab_db = sab_db


# Configuração para criar o Banco de dados
with app.app_context():
    # Criar todas as tabelas
    db.create_all()

    # Comando para adicionar um usuário padrão ao criar o banco de dados
    if User.query.filter_by(user='administrador').count() < 1:
        user = User(name='Administrador', user='administrador', password='FisicaQuantica*', status=1)
        db.session.add(user)
        db.session.commit()


@app.route("/")
def redirecionamento():
    return redirect(url_for('login'))


# Tela de login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form['usuario']
        senha = request.form["senha"]
        user = User.query.filter_by(user=usuario).first()
        if not user or not check_password_hash(user.password, senha):  # Verificar se está correto
            flash("Usuário ou senha inválidos")
        elif user.status == 1:
            login_user(user)
            return redirect(url_for('pagina_inicial'))
    return render_template('login.html')


# Caso o usuário não esteja autenticado ele será redirecionado para a página de login
@login_manager.unauthorized_handler
def unauthorized_callback():
    flash("Faça o login!")
    return redirect(url_for('login'))


# Tela de logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Página inicial
@app.route("/pagina_inicial")
@login_required
def pagina_inicial():
    return render_template("pagina_inicial.html")


# Listagem dos usuários
@app.route('/lista_users')
@login_required
def lista_users():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    todos_users = User.query.paginate(page=page, per_page=per_page)
    return render_template("users.html", users=todos_users)


# Criação de usuários
@app.route("/cria_user", methods=["GET", "POST"])
@login_required
def cria_user():
    nome = request.form.get('nome')
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    status = request.form.get('status')
    if request.method == 'POST':
        # Caso os dados não sejam preenchidos
        if not nome and not usuario and not senha:
            flash("Preencha todos os campos", "error")
        else:
            user = User(nome, usuario, senha, status)
            # Verifica se já existe o 'usuario' cadastrado no banco de dados
            if not User.query.filter_by(user=usuario).count() < 1:
                flash("Usuário já cadastrado!")
            else:
                # Cadastro no banco de dados
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('lista_users'))
    return render_template('novo_user.html')


# Função para a edição dos usuários
@app.route('/<int:id>/atualiza_user', methods=["GET", "POST"])
@login_required
def atualiza_user(id):
    user = User.query.filter_by(id=id).first()
    nome = request.form.get('nome')
    senha = request.form.get('senha')
    if request.method == "POST":
        if not nome and not senha:
            flash("Preencha todos os campos", "error")
        else:
            nome = request.form["nome"]
            # O usuário não pode ser alterado
            senha = request.form["senha"]
            status = request.form["status"]
            cript_senha = generate_password_hash(senha)  # Criptografando a senha
            User.query.filter_by(id=id).update(
                {"name": nome, "user": user.user, "password": cript_senha, "status": status})  # Chamar a tabela
            db.session.commit()
            return redirect(url_for('lista_users'))
    return render_template("atualiza_user.html", user=user)


# Função para a listagem de funcionários contidos no banco de dados
@app.route('/lista_funcionarios')
@login_required
def lista_funcionarios():
    page = request.args.get('page', 1, type=int)
    per_page = 100
    todos_funcionarios = tb_Funcionarios.query.paginate(page=page, per_page=per_page)
    return render_template("funcionarios.html", funcionarios=todos_funcionarios)


# Função para a criação de funcionário no banco de dados
@app.route("/cria_funcionario", methods=["GET", "POST"])
@login_required
def cria_funcionario():
    nome = request.form.get('nome')
    status = request.form.get('status')
    if request.method == 'POST':
        if not nome:
            flash("Preencha todos os campos", "error")
        else:
            funcionario = tb_Funcionarios(nome, status)
            db.session.add(funcionario)
            db.session.commit()
            return redirect(url_for('lista_funcionarios'))
    return render_template('novo_funcionario.html')


# Função para a edição do nome dos funcionários
@app.route('/<int:id>/atualiza_funcionario', methods=["GET", "POST"])
@login_required
def atualiza_funcionario(id):
    funcionario = tb_Funcionarios.query.filter_by(id=id).first()

    nome = request.form.get('nome')
    if request.method == "POST":
        if not nome:
            flash("Preencha todos os campos", "error")
        else:
            nome = request.form["nome"]
            status = request.form["status"]
            tb_Funcionarios.query.filter_by(id=id).update({"nome": nome, "status": status})  # Chamar a tabela
            db.session.commit()
            return redirect(url_for('lista_funcionarios'))
    return render_template("atualiza_funcionario.html", funcionario=funcionario)

mes = 0
# Atribuição dos usuários aos seus respectivos turnos
@app.route('/cria_escala', methods=["GET", "POST"])
@login_required
def cria_escala():
    global lista_mes, mes_str
    page = request.args.get('page', 1, type=int)
    per_page = 50
    todos_funcionarios = tb_Funcionarios.query.paginate(page=page, per_page=per_page)

    if request.method == 'POST':
        user1 = request.form['name_t1']
        user2a = request.form['name_t2a']
        user2b = request.form['name_t2b']
        user3 = request.form['name_t3']
        user4 = request.form['name_t4']
        user_folg1 = request.form['name_folg1']
        user_folg2 = request.form['name_folg2']
        mes = int(request.form['mes'])
        lista_meses = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro',
                       'Outubro', 'Novembro', 'Dezembro']
        mes_str = lista_meses[int(mes)]
        # Verificação do ano atual
        ano_var = datetime.today()
        ano = ano_var.year
        calendar.setfirstweekday(6)  # Inicio da semana no domingo
        # lista com elementos de listas representando as semanas do mes escolhido
        lista_mes = calendar.monthcalendar(ano, mes)  # Lista com listas de cada semana do mês escolhido

        # Excluindo os dados da tabela
        for i in range(100):
            tb_Semana.query.filter_by(id=i).delete()
            db.session.commit()

        # Condição para meses em que o dia 1 não cai em um domingo
        if lista_mes[0][0] == 1:  # Verifica se o dia 1° não é em um domingo
            escala_1(user1, user2a, user2b, user3, user4, user_folg1, user_folg2, lista_mes, mes_str)
        else:
            escala_2(user1, user2a, user2b, user3, user4, user_folg1, user_folg2, lista_mes, mes_str)
        sleep(3)
        return redirect(url_for('escala_mensal'))
    return render_template("cria_escala.html", funcionarios=todos_funcionarios)


# Funções que criam o arquivo HTML e CSV das tabelas
# Escala para meses em que o dia 1 cai em um domingo
def escala_1(user1, user2a, user2b, user3, user4, user_folg1, user_folg2, lista_mes, mes_str):
    global tbl_csv_0, tbl_csv_1, tbl_csv_2, tbl_csv_3, tbl_csv_4, tbl_csv_5, segunda, terca, quarta, quinta, sexta, \
        sabado, dia_none, turno, horario
    domingo = None

    for smn in range(len(lista_mes)):
        # Variável que retornará o dia do mês para cada domingo
        data_dom = lista_mes[smn][0]
        data_seg = lista_mes[smn][1]
        data_ter = lista_mes[smn][2]
        data_qua = lista_mes[smn][3]
        data_qui = lista_mes[smn][4]
        data_sex = lista_mes[smn][5]
        data_sab = lista_mes[smn][6]

        # Criação da escala para cada dia
        turno = ['Data', '1° Turno', '2° Turno', '2° Turno', '3° Turno', '4° Turno']  # Turnos
        horario = [mes_str, '00:00 - 06:15', '06:00 - 12:15', '07:00 - 13:15', '12:00 - 18:15', '18:00 - 00:15']
        segunda = [data_seg, user_folg1, user2a, user2b, user3, user4]
        terca = [data_ter, user1, user2a, user2b, user_folg1, user4]  # Escala da terça-feira
        quarta = [data_qua, user1, user_folg1, user2b, user3, user4]  # Escala da quarta-feira
        quinta = [data_qui, user1, user2a, user_folg1, user3, user4]  # Escala da quinta-feira
        sexta = [data_sex, user1, user2a, user2b, user3, user_folg1]  # Escala da sexta-feira
        sabado = [data_sab, user1, user2a, user2b, user3, user4]  # Escala do sabado
        dia_none = ['', '', '', '', '', '']

        # Condições para as folgas de domingo
        if smn == 0:
            domingo = [data_dom, user_folg1, user2a, user2b, user3, user4]  # Folga do turno 1
        elif smn == 1:
            domingo = [data_dom, user1, user_folg1, user2b, user3, user4]  # Folga do turno 2a
        elif smn == 2:
            domingo = [data_dom, user1, user2a, user2b, user3, user4]  # Folga do folguista
        elif smn == 3:
            domingo = [data_dom, user1, user2a, user_folg1, user3, user4]  # Folga do turno 2b
        elif smn == 4:
            domingo = [data_dom, user1, user2a, 'alocado', user2b, user_folg1]  # Folga do turno 3 e 4
            segunda = [data_seg, user_folg2, user2a, user2b, user_folg1, user4]

        # Condição que verifica se o dia da semana é um dia do calendário do mês escolhido
        if data_dom == 0:
            domingo = dia_none
        if data_seg == 0:
            segunda = dia_none
        if data_ter == 0:
            terca = dia_none
        if data_qua == 0:
            quarta = dia_none
        if data_qui == 0:
            quinta = dia_none
        if data_sex == 0:
            sexta = dia_none
        if data_seg == 0:
            segunda = dia_none
        if data_sab == 0:
            sabado = dia_none

        # Condição que gera escalas para cada semana do mês
        semana = {'Turno': turno,
                  'Horário': horario,
                  'Domingo': domingo,
                  'Segunda': segunda,
                  'Terca': terca,
                  'Quarta': quarta,
                  'Quinta': quinta,
                  'Sexta': sexta,
                  'Sabado': sabado}

        # Criação da tabela
        df = pd.DataFrame(semana)

        # Criação do CSV
        tbl_csv = df.to_csv(index=False, encoding='utf-8')

        # Funções que receberão o código HTML e CSV para cada tabela da semana
        if smn == 0:
            tbl_csv_0 = tbl_csv
            atualiza_db(turno, horario, domingo, segunda, terca, quarta, quinta, sexta, sabado)
        elif smn == 1:
            tbl_csv_1 = tbl_csv
            atualiza_db(turno, horario, domingo, segunda, terca, quarta, quinta, sexta, sabado)
        elif smn == 2:
            tbl_csv_2 = tbl_csv
            atualiza_db(turno, horario, domingo, segunda, terca, quarta, quinta, sexta, sabado)
        elif smn == 3:
            tbl_csv_3 = tbl_csv
            atualiza_db(turno, horario, domingo, segunda, terca, quarta, quinta, sexta, sabado)
        elif smn == 4:
            tbl_csv_4 = tbl_csv
            atualiza_db(turno, horario, domingo, segunda, terca, quarta, quinta, sexta, sabado)

    # Condição para a sexta semana
    domingo = dia_none
    segunda = dia_none
    terca = dia_none
    quarta = dia_none
    quinta = dia_none
    sexta = dia_none
    sabado = dia_none

    tbl_csv_5 = ''
    atualiza_db(turno, horario, domingo, segunda, terca, quarta, quinta, sexta, sabado)

    # Comando para executar a função de criação do código HTML e arquivo CSV das tabelas
    cria_tbl_csv(tbl_csv_0, tbl_csv_1, tbl_csv_2, tbl_csv_3, tbl_csv_4, tbl_csv_5)


# Escala para meses em que o dia 1 não cai em um domingo
def escala_2(user1, user2a, user2b, user3, user4, user_folg1, user_folg2, lista_mes, mes_str):
    global tbl_csv_0, tbl_csv_1, tbl_csv_2, tbl_csv_3, tbl_csv_4, tbl_csv_5, segunda, terca, quarta, quinta, sexta, \
        sabado, dia_none, turno, horario

    for smn in range(len(lista_mes)):
        domingo = None
        # Variável que retornará o dia do mês para cada domingo
        data_dom = lista_mes[smn][0]
        data_seg = lista_mes[smn][1]
        data_ter = lista_mes[smn][2]
        data_qua = lista_mes[smn][3]
        data_qui = lista_mes[smn][4]
        data_sex = lista_mes[smn][5]
        data_sab = lista_mes[smn][6]

        # Criação da escala para cada dia
        turno = ['Data', '1° Turno', '2° Turno', '2° Turno', '3° Turno', '4° Turno']  # Turnos
        horario = [mes_str, '00:00 - 06:15', '06:00 - 12:15', '07:00 - 13:15', '12:00 - 18:15', '18:00 - 00:15']
        segunda = [data_seg, user_folg1, user2a, user2b, user3, user4]
        terca = [data_ter, user1, user2a, user2b, user_folg1, user4]  # Escala da terça-feira
        quarta = [data_qua, user1, user_folg1, user2b, user3, user4]  # Escala da quarta-feira
        quinta = [data_qui, user1, user2a, user_folg1, user3, user4]  # Escala da quinta-feira
        sexta = [data_sex, user1, user2a, user2b, user3, user_folg1]  # Escala da sexta-feira
        sabado = [data_sab, user1, user2a, user2b, user3, user4]  # Escala do sabado
        dia_none = ['', '', '', '', '', '']

        # Para meses com 5 semanas e 4 domingos
        if len(lista_mes) == 5:
            # Condições para as folgas de domingo
            if smn == 0:
                domingo = dia_none
            elif smn == 1:
                domingo = [data_dom, user_folg1, user2a, user2b, user3, user4]  # Folga do turno 1
            elif smn == 2:  # Se houver 6 semanas no mês
                domingo = [data_dom, user1, user_folg1, 'folga', user3, user4]  # Folga dos dois turnos 2
            elif smn == 3:
                domingo = [data_dom, user1, user2a, user2b, user3, user4]  # Folga do folguista
            if smn == 4:
                domingo = [data_dom, user1, user2a, 'alocado', user2b, user_folg1]  # Folga do turno 3 e 4
                segunda = [data_seg, user_folg2, user2a, user2b, user_folg1, user4]

        # Para meses com 6 semanas e 5 domingos
        if len(lista_mes) == 6:
            # Condições para as folgas de domingo
            if smn == 0:
                domingo = dia_none
            elif smn == 1:
                domingo = [data_dom, user_folg1, user2a, user2b, user3, user4]  # Folga do turno 1
            elif smn == 2:
                domingo = [data_dom, user1, user_folg1, user2b, user3, user4]  # Folga do turno 2a
            elif smn == 3:
                domingo = [data_dom, user1, user2a, user2b, user3, user4]  # Folga do folguista
            elif smn == 4:
                domingo = [data_dom, user1, user2a, user_folg1, user3, user4]  # Folga do turno 2a
            elif smn == 5:
                domingo = [data_dom, user1, user2a, 'alocado', user2b, user_folg1]  # Folga do turno 3 e 4
                segunda = [data_seg, user_folg2, user2a, user2b, user_folg1, user4]

        # Condição que verifica se o dia da semana é um dia do calendário do mês escolhido
        if data_dom == 0:
            domingo = dia_none
        if data_seg == 0:
            segunda = dia_none
        if data_ter == 0:
            terca = dia_none
        if data_qua == 0:
            quarta = dia_none
        if data_qui == 0:
            quinta = dia_none
        if data_sex == 0:
            sexta = dia_none
        if data_seg == 0:
            segunda = dia_none
        if data_sab == 0:
            sabado = dia_none

        # Condição que gera escalas para cada semana do mês
        semana = {'Turno': turno,
                  'Horário': horario,
                  'Domingo': domingo,
                  'Segunda': segunda,
                  'Terca': terca,
                  'Quarta': quarta,
                  'Quinta': quinta,
                  'Sexta': sexta,
                  'Sabado': sabado}

        # Criação da tabela
        df = pd.DataFrame(semana)

        # Criação do CSV
        tbl_csv = df.to_csv(index=False, encoding='utf-8')

        # Funções que receberão o código HTML e CSV para cada tabela da semana
        if smn == 0:
            tbl_csv_0 = tbl_csv
            atualiza_db(turno, horario, domingo, segunda, terca, quarta, quinta, sexta, sabado)
        elif smn == 1:
            tbl_csv_1 = tbl_csv
            atualiza_db(turno, horario, domingo, segunda, terca, quarta, quinta, sexta, sabado)
        elif smn == 2:
            tbl_csv_2 = tbl_csv
            atualiza_db(turno, horario, domingo, segunda, terca, quarta, quinta, sexta, sabado)
        elif smn == 3:
            tbl_csv_3 = tbl_csv
            atualiza_db(turno, horario, domingo, segunda, terca, quarta, quinta, sexta, sabado)
        elif smn == 4:
            tbl_csv_4 = tbl_csv
            atualiza_db(turno, horario, domingo, segunda, terca, quarta, quinta, sexta, sabado)
        if smn == 5:
            tbl_csv_5 = tbl_csv
            atualiza_db(turno, horario, domingo, segunda, terca, quarta, quinta, sexta, sabado)

    if len(lista_mes) == 5:
        # Condição para a sexta semana
        domingo = dia_none
        segunda = dia_none
        terca = dia_none
        quarta = dia_none
        quinta = dia_none
        sexta = dia_none
        sabado = dia_none

        tbl_csv_5 = ''
        atualiza_db(turno, horario, domingo, segunda, terca, quarta, quinta, sexta, sabado)

    # Comando para executar a função de criação do código HTML e arquivo CSV das tabelas
    cria_tbl_csv(tbl_csv_0, tbl_csv_1, tbl_csv_2, tbl_csv_3, tbl_csv_4, tbl_csv_5)


# Criação dos valores na tabela semanal na tabela tb_Tabela
def atualiza_db(turno, horario, domingo, segunda, terca, quarta, quinta, sexta, sabado):
    # Escala da primeira semana
    db.session.add(
        tb_Semana(turno[0], horario[0], domingo[0], segunda[0], terca[0], quarta[0], quinta[0], sexta[0], sabado[0]))
    db.session.add(
        tb_Semana(turno[1], horario[1], domingo[1], segunda[1], terca[1], quarta[1], quinta[1], sexta[1], sabado[1]))
    db.session.add(
        tb_Semana(turno[2], horario[2], domingo[2], segunda[2], terca[2], quarta[2], quinta[2], sexta[2],sabado[2]))
    db.session.add(
        tb_Semana(turno[3], horario[3], domingo[3], segunda[3], terca[3], quarta[3], quinta[3], sexta[3],sabado[3]))
    db.session.add(
        tb_Semana(turno[4], horario[4], domingo[4], segunda[4], terca[4], quarta[4], quinta[4], sexta[4], sabado[4]))
    db.session.add(
        tb_Semana(turno[5], horario[5], domingo[5], segunda[5], terca[5], quarta[5], quinta[5], sexta[5],sabado[5]))
    db.session.commit()


# Criação do arquivo CSV das tabelas
def cria_tbl_csv(tbl_csv_0, tbl_csv_1, tbl_csv_2, tbl_csv_3, tbl_csv_4, tbl_csv_5):
    vars_csv = tbl_csv_0 + tbl_csv_1 + tbl_csv_2 + tbl_csv_3 + tbl_csv_4 + tbl_csv_5
    with open('static/arquivos/tabela.csv', 'w') as f:
        f.write(vars_csv)
        f.close()


# Página d exibição da tabela
@app.route('/escala_mensal')
# @login_required Está página ficará livre para ser acessada pelos funcionários
def escala_mensal():

    # Escala da primeira semana
    page = request.args.get('page', 1, type=int)
    esc_1 = tb_Semana.query.paginate(page=page, per_page=6)
    # Escala da segunda semana
    page = request.args.get('page', 2, type=int)
    esc_2 = tb_Semana.query.paginate(page=page, per_page=6)
    # Escala da terceira semana
    page = request.args.get('page', 3, type=int)
    esc_3 = tb_Semana.query.paginate(page=page, per_page=6)
    # Escala da quarta semana
    page = request.args.get('page', 4, type=int)
    esc_4 = tb_Semana.query.paginate(page=page, per_page=6)
    # Escala da quinta semana
    page = request.args.get('page', 5, type=int)
    esc_5 = tb_Semana.query.paginate(page=page, per_page=6)

    # Quantidade de semanas
    semanas = len(lista_mes)
    print(semanas)
    # Escala da sexta semana
    page = request.args.get('page', 6, type=int)
    esc_6 = tb_Semana.query.paginate(page=page, per_page=6)

    return render_template('escala_mensal.html', mes=mes_str, esc_1=esc_1, esc_2=esc_2, esc_3=esc_3, esc_4=esc_4,
                           esc_5=esc_5, esc_6=esc_6, semanas=semanas)


@app.route('/<int:id>/atualiza_escala', methods=["GET", "POST"])
@login_required
def atualiza_escala(id):
    linha_escala = tb_Semana.query.filter_by(id=id).first()

    # Funcionários cadastrados
    page = request.args.get('page', 1, type=int)
    per_page = 50
    todos_funcionarios = tb_Funcionarios.query.paginate(page=page, per_page=per_page)

    if request.method == "POST":
        turno_db = request.form["turno_db"]
        horario_db = request.form["horario_db"]
        dom_db = request.form["dom_db"]
        seg_db = request.form["seg_db"]
        ter_db = request.form["ter_db"]
        qua_db = request.form["qua_db"]
        qui_db = request.form["qui_db"]
        sex_db = request.form["sex_db"]
        sab_db = request.form["sab_db"]
        tb_Semana.query.filter_by(id=id).update({"turno_db": turno_db, "horario_db": horario_db, "dom_db": dom_db,
                                                 "seg_db": seg_db, "ter_db": ter_db, "qua_db": qua_db, "qui_db": qui_db,
                                                 "sex_db": sex_db, "sab_db": sab_db})
        db.session.commit()
        return redirect(url_for('escala_mensal'))
    return render_template("atualiza_escala.html", linha_escala=linha_escala, funcionarios=todos_funcionarios)


# Execução da aplicação
if __name__ == "__main__":
    app.run(debug=True)
