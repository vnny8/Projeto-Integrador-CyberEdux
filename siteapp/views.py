from django.forms import model_to_dict
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .forms import LoginForm
from .models import Aluno, Professor, Disciplina, Aluno_tem_professor, Aluno_tem_disciplina, Pedido_Equipamento, Materiais, Plano_Ensino
from django.contrib.auth import authenticate
from django.contrib.auth import login as authLogin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.db.models import Prefetch
from django.contrib import messages
from django.conf import settings
from django.conf.urls.static import static
import json
import smtplib
import email.message

def check_professor(user):
    if (user.username[0] == 'P'):
        return (User.objects.filter(username__startswith='P').exists())
    else:
        return False
    
def check_aluno(user):
    if (user.username[0] == 'A'):
        return (User.objects.filter(username__startswith='A').exists())
    else:
        return False

def check_admin(user):
    if (user.username[0] != 'P'):
        return (User.objects.filter(username=user).exists())
    else:
        False


@login_required(login_url="login")
@user_passes_test(check_professor)
def main(request):
    username = (request.user.username)[1:]
    usuario = Professor.objects.get(cpf=username)
    materiais = Materiais.objects.filter(disciplina_id=usuario.disciplina)
    if request.method == 'POST':
        if 'action' in request.POST:
            if request.POST['action'] == 'form':
                plano_de_ensino = request.FILES.get('plano', None)
                pe = Plano_Ensino()
                pe.plano_ensino = plano_de_ensino
                pe.save()
                usuario.disciplina.planoensino = pe
                usuario.disciplina.save()
                return HttpResponseRedirect(reverse('home'))  
            
            elif request.POST['action'] == 'form2':
                material1 = request.FILES.get('material', None)
                nome = request.POST.get('nome_material')
                material = Materiais()
                material.disciplina = usuario.disciplina
                material.local = material1
                material.nome = nome
                material.save()
                return HttpResponseRedirect(reverse('home')) 
        
    return render(request, 'main.html', {'usuario': usuario, 'materiais': materiais})

@login_required(login_url="login")
@user_passes_test(check_professor)
def configuracoes(request):
    professor = Professor.objects.get(cpf=(request.user.username[1:]))
    disciplina = Disciplina.objects.get(id=professor.disciplina.id)
    if request.method == 'POST':
        if 'action' in request.POST:
            if request.POST['action'] == 'form':
                img = request.FILES.get('imagem', None)
                professor.perfil = img
                professor.save()
                return redirect('configuracoes/')
        else:
            nome = request.POST.get("nome")
            data_nascimento = request.POST.get("data")
            sexo = request.POST.get("sexo")
            celular = request.POST.get("celular")
            endereco = request.POST.get("endereco")
            cpf = request.POST.get("cpf")
            rg = request.POST.get("rg")
            email = request.POST.get("email")
            ano = request.POST.get("ano")
            
            if Professor.objects.filter(email=email).exists():
                professor1 = Professor.objects.get(email=email)
                if professor1 and professor1.id != professor.id:
                    messages.error(request, f'ERRO. Já existe professor cadastrado com o email {email}.')
                    return redirect('configuracoes/')

            professor.nome = nome
            professor.data_nascimento = data_nascimento
            professor.sexo = sexo
            professor.celular = celular
            professor.endereco = endereco
            professor.cpf = cpf
            professor.rg = rg
            professor.email = email
            professor.ano = ano
            professor.save()
            senha = request.POST.get('password')
            user = User.objects.get(username=request.user.username)
            if (senha != user.password and senha != ""):
                user.set_password(senha)
                user.save()
            messages.success(request, 'Configurações editadas com sucesso!')
            return redirect('configuracoes/')
    return render(request, 'configuracoes.html', {'professor': professor, 'disciplina': disciplina})

@login_required(login_url="login")
@user_passes_test(check_professor)
def nota_alunos(request):
    flag = 0
    if request.method == 'POST':
        professor = Professor.objects.get(cpf=(request.user.username[1:]))
        id_entrada = request.POST.get("matricula")
        aluno = Aluno.objects.get(id=id_entrada)
        aluno_tem_disciplina = Aluno_tem_disciplina.objects.get(aluno_id=aluno.id, disciplina_id=professor.disciplina_id)  
        try:
            nota = float(request.POST.get('nota'))
            aluno_tem_disciplina.nota = nota
            if 5 <= nota <= 10:
                aluno_tem_disciplina.status = 'Aprovado'
                messages.error(request, "Aluno avaliado com sucesso!")
                aluno_tem_disciplina.save()
                return redirect('nota_alunos/')
            elif 0 <= nota < 5:
                aluno_tem_disciplina.status = 'Reprovado'
                messages.error(request, "Aluno avaliado com sucesso!")
                aluno_tem_disciplina.save()
                return redirect('nota_alunos/')
            else:
                messages.error(request, "ERRO. O valor da nota deve estar entre 0 e 10.")
                return redirect('nota_alunos/')
        except:
            messages.error(request, "ERRO. O valor da nota deve estar entre 0 e 10.")
            return redirect('nota_alunos/')
        
    elif request.method == 'GET' or 'pesquisa' in request.GET:
        flag = 1
        pesquisa = request.GET.get('pesquisa', '')
    if flag:
        professor = Professor.objects.get(cpf=(request.user.username[1:]))
        alunos = Aluno.objects.prefetch_related('aluno_tem_professor_set').filter(aluno_tem_professor__professor=professor)
        disc = (Professor.objects.get(cpf=(request.user.username[1:]))).disciplina
        alunos2 = []
        for aluno in alunos:
            if aluno.status_cadastro != "Inativo":
                alunos2.append({
                    'aluno': aluno,
                    'notas': Aluno_tem_disciplina.objects.filter(disciplina_id=disc),
                })
        return render(request, 'notaAlunos.html', {'alunos': alunos2, 'pesquisa': pesquisa})
    else:
        professor = Professor.objects.get(cpf=(request.user.username[1:]))
        alunos = Aluno_tem_disciplina.objects.get(professor_id=professor)
        return render(request, 'notaAlunos.html', {'alunos': alunos, 'pesquisa': ""})

@login_required(login_url="login")
@user_passes_test(check_professor)
def alugar(request):
    if request.method == 'POST':
        username = (request.user.username)[1:]
        usuario = Professor.objects.get(cpf=username)
        pedido = Pedido_Equipamento()
        pedido.professor = usuario
        ass = request.POST.get('titulo')
        desc = request.POST.get('conteudo')
        pedido.assunto = ass
        pedido.descricao = desc
        pedido.save()
    return render(request, 'alugarProfessor.html')

def login(request):
    if request.method != 'POST':
        form = LoginForm()
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cpf = 'P' + request.POST.get('username')
            senha = request.POST.get('password')
            user = authenticate(username=cpf, password=senha)
            if user:
                authLogin(request, user)
                next_url = request.GET.get('next', '')
                if next_url == "/logout/": 
                    return redirect('home')
                return HttpResponseRedirect(reverse('home'))  
            else:
                messages.error(request, 'Usuário ou senha incorreto.')
                return redirect('login')
            
    return render(request, 'login.html', {'form': form})

@login_required(login_url="login")
@user_passes_test(check_professor)
def sair(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))
    
# ========================== DIRETOR ======================

def loginDiretor(request):
    if request.method != 'POST':
        form = LoginForm()
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cpf = request.POST.get('username')
            senha = request.POST.get('password')
            user = authenticate(username=cpf, password=senha)
            if user:
                authLogin(request, user)
                next_url = request.GET.get('next', '') 
                if next_url == "/sair/": 
                    return redirect('main')
                return HttpResponseRedirect(reverse('main'))   
            else:
                messages.error(request, 'Usuário ou senha incorreto.')
                return redirect('loginDiretor')
            
    return render(request, 'loginAdmin.html')

@login_required(login_url="loginDiretor")
@user_passes_test(check_admin)
def mainDiretor(request):
    dados_grafico1 = []
    dados_grafico2 = []
    dados_grafico3 = []
    disciplina = Disciplina.objects.all()
    aluno_disciplina = Aluno_tem_disciplina.objects.all()
    disciplina2 = disciplina
    for disc in disciplina2:
        cont = 0
        for aluno_disc in aluno_disciplina:
            if aluno_disc.disciplina.nome == disc.nome:
                cont = cont + 1
                
        if 'Educação Física' in disc.nome:
                disc.nome = 'ED' + disc.nome.split('Física')[1]
                
        if 'Língua Portuguesa' in disc.nome:
                disc.nome = 'LP' + disc.nome.split('Portuguesa')[1]
        
        if 1 <= disc.id <= 12:    
            dados_grafico1.append({"Disciplina": disc.nome, "value": cont})
        elif 13 <= disc.id <= 23:
            dados_grafico2.append({"Disciplina": disc.nome, "value": cont})
        elif 24 <= disc.id <= 34:
            dados_grafico3.append({"Disciplina": disc.nome, "value": cont})
    
    dados_grafico4 = []
    for disc in disciplina:
        cont1 = 0
        cont2 = 0
        cont3 = 0
        for aluno_disc in aluno_disciplina:
            if aluno_disc.disciplina == disc:
                if aluno_disc.status == 'Aprovado':
                    cont1 = cont1 + 1
                elif aluno_disc.status == 'Reprovado':
                    cont2 = cont2 + 1
                else:
                    cont3 = cont3 + 1
        dados_grafico4.append({"Disciplina": disc.nome, "Estado": 'Aprovado', "value": cont1})
        dados_grafico4.append({"Disciplina": disc.nome, "Estado": 'Reprovado', "value": cont2})
        dados_grafico4.append({"Disciplina": disc.nome, "Estado": 'Cursando', "value": cont3})
        
    return render(request, 'mainAdmin.html', {'dados_grafico1': dados_grafico1, 'dados_grafico2': dados_grafico2, 'dados_grafico3': dados_grafico3, 'dados_grafico4': dados_grafico4, 'lista_disciplinas': disciplina})

@login_required(login_url="loginDiretor")
@user_passes_test(check_admin)
def matricula(request):
    if request.method == 'POST':
        if 'action' in request.POST:
            if request.POST['action'] == 'form':
                id_aluno = request.POST.get('id')
                aluno = Aluno.objects.get(id=id_aluno)
                aluno.status_cadastro = "Ativo"
                aluno.save()
                messages.success(request, 'Aluno matriculado com sucesso!')
                return redirect('matricula')
            elif request.POST['action'] == 'form2':
                id_aluno = request.POST.get('id')
                aluno = Aluno.objects.get(id=id_aluno)
                aluno.delete()
                messages.success(request, 'Aluno rejeitado com sucesso!')
                return redirect('matricula')
            
        nome = request.POST.get("nome")
        data_nascimento = request.POST.get("data")
        sexo = request.POST.get("sexo")
        celular = request.POST.get("celular")
        endereco = request.POST.get("endereco")
        cpf = request.POST.get("cpf")
        rg = request.POST.get("rg")
        email = request.POST.get("email")
        ano = request.POST.get("ano")
        turma = request.POST.get("turma")
        
        if Aluno.objects.filter(cpf=cpf).exists():
            messages.error(request, f'ERRO. Já existe aluno cadastrado com o CPF {cpf}.')
            return redirect('matricula')
        
        if Aluno.objects.filter(rg=rg).exists():
            messages.error(request, f'ERRO. Já existe aluno cadastrado com o RG {rg}.')
            return redirect('matricula')
        
        if Aluno.objects.filter(email=email).exists():
            messages.error(request, f'ERRO. Já existe aluno cadastrado com o email {email}.')
            return redirect('matricula')
        
        aluno = Aluno()
        aluno.nome = nome
        aluno.data_nascimento = data_nascimento
        aluno.sexo = sexo
        aluno.endereco = endereco
        aluno.cpf = cpf
        aluno.rg = rg
        aluno.email = email
        aluno.celular = celular
        aluno.ano = ano
        aluno.turma = turma
        aluno.status_cadastro = "Ativo"
        aluno.save()
        senha = request.POST.get('password')
        
        try:
            professores = Professor.objects.all()
            for professor in professores:
                rg = Aluno_tem_professor()
                if int(aluno.ano) == int(professor.ano):
                    rg.professor = professor
                    rg.aluno = aluno
                    rg.save()
        except:
            pass
        disciplinas = Disciplina.objects.all()
        for disciplina in disciplinas:
            rg = Aluno_tem_disciplina()
            if int(aluno.ano) == 1 and disciplina.id <= 12:
                rg.disciplina = disciplina
                rg.aluno = aluno
                rg.save()
            elif int(aluno.ano) == 2 and 13 <= disciplina.id <= 23:
                rg.disciplina = disciplina
                rg.aluno = aluno
                rg.save()
            elif int(aluno.ano) == 3 and 24 <= disciplina.id <= 34:
                rg.disciplina = disciplina
                rg.aluno = aluno
                rg.save()
        
        user = User.objects.filter(username=aluno.cpf).first()
        if user:
            return HttpResponse('Já existe esse usuário.')
        
        user = User.objects.create_user(username=('A' + aluno.cpf), password=senha)
        messages.success(request, 'Formulário enviado com sucesso!')
        return redirect('matricula')
    
    else:
        alunos = Aluno.objects.filter(status_cadastro="Inativo")
        return render(request, 'adicionaAluno.html', {'alunos': alunos})
    
def matriculaAluno(request):
    if request.method == 'POST':
        nome = request.POST.get("nome")
        data_nascimento = request.POST.get("data")
        sexo = request.POST.get("sexo")
        celular = request.POST.get("celular")
        endereco = request.POST.get("endereco")
        cpf = request.POST.get("cpf")
        rg = request.POST.get("rg")
        email = request.POST.get("email")
        ano = request.POST.get("ano")
        turma = request.POST.get("turma")
        
        if Aluno.objects.filter(cpf=cpf).exists():
            messages.error(request, f'ERRO. Já existe aluno cadastrado com o CPF {cpf}.')
            return redirect('matricula_aluno')
        
        if Aluno.objects.filter(rg=rg).exists():
            messages.error(request, f'ERRO. Já existe aluno cadastrado com o RG {rg}.')
            return redirect('matricula_aluno')
        
        if Aluno.objects.filter(email=email).exists():
            messages.error(request, f'ERRO. Já existe aluno cadastrado com o email {email}.')
            return redirect('matricula_aluno')
        
        aluno = Aluno()
        aluno.nome = nome
        aluno.data_nascimento = data_nascimento
        aluno.sexo = sexo
        aluno.endereco = endereco
        aluno.cpf = cpf
        aluno.rg = rg
        aluno.email = email
        aluno.celular = celular
        aluno.ano = ano
        aluno.turma = turma
        aluno.status_cadastro = "Inativo"
        aluno.save()
        senha = request.POST.get('password')
        
        try:
            professores = Professor.objects.all()
            for professor in professores:
                rg = Aluno_tem_professor()
                if int(aluno.ano) == int(professor.ano):
                    rg.professor = professor
                    rg.aluno = aluno
                    rg.save()
        except:
            pass
        disciplinas = Disciplina.objects.all()
        for disciplina in disciplinas:
            rg = Aluno_tem_disciplina()
            if int(aluno.ano) == 1 and disciplina.id <= 12:
                rg.disciplina = disciplina
                rg.aluno = aluno
                rg.save()
            elif int(aluno.ano) == 2 and 13 <= disciplina.id <= 23:
                rg.disciplina = disciplina
                rg.aluno = aluno
                rg.save()
            elif int(aluno.ano) == 3 and 24 <= disciplina.id <= 34:
                rg.disciplina = disciplina
                rg.aluno = aluno
                rg.save()
        
        user = User.objects.filter(username=aluno.cpf).first()
        if user:
            return HttpResponse('Já existe esse usuário.')
        
        user = User.objects.create_user(username=('A' + aluno.cpf), password=senha)
        messages.success(request, 'Aluno matriculado com sucesso!')
        return redirect('matricula_aluno')
    
    else:
        return render(request, 'matriculaAluno.html')

@login_required(login_url="loginDiretor")
@user_passes_test(check_admin)
def contratar(request):
    if request.method == 'POST':
        if 'action' in request.POST:
            if request.POST['action'] == 'form':
                id_professor = request.POST.get('id')
                professor = Professor.objects.get(id=id_professor)
                professor.status_cadastro = "Ativo"
                professor.save()
                messages.success(request, 'Professor matriculado com sucesso!')
                return redirect('matricula')
            elif request.POST['action'] == 'form2':
                id_professor = request.POST.get('id')
                professor = Professor.objects.get(id=id_professor)
                professor.delete()
                messages.success(request, 'Professor rejeitado com sucesso!')
                return redirect('matricula')
            
        nome = request.POST.get("nome")
        data_nascimento = request.POST.get("data")
        sexo = request.POST.get("sexo")
        celular = request.POST.get("celular")
        endereco = request.POST.get("endereco")
        cpf = request.POST.get("cpf")
        rg = request.POST.get("rg")
        email = request.POST.get("email")
        ano = request.POST.get("ano")
        disc = request.POST.get("disciplina")
        professor = Professor()
        professor.nome = nome
        professor.data_nascimento = data_nascimento
        professor.sexo = sexo
        professor.celular = celular
        professor.endereco = endereco
        professor.cpf = cpf
        professor.rg = rg
        professor.email = email
        professor.ano = ano
        professor.status_cadastro = "Ativo"
        if disc == "Artes" and ano != '1':
            messages.error(request, 'ERRO. Só existe a matéria Artes pro 1° ano do ensino médio.')
            return redirect('contratar')
        if disc != "Artes":
            if ano == '1':
                disc = disc + " I"
            elif ano == '2':
                disc = disc + " II"
            elif ano == '3':
                disc = disc + " III"
                
        disciplina = Disciplina.objects.get(nome=disc)
                
        if Professor.objects.filter(cpf=cpf).exists():
            messages.error(request, f'ERRO. Já existe professor cadastrado com o CPF {cpf}.')
            return redirect('contratar')
        
        if Professor.objects.filter(rg=rg).exists():
            messages.error(request, f'ERRO. Já existe professor cadastrado com o RG {rg}.')
            return redirect('contratar')
        
        if Professor.objects.filter(email=email).exists():
            messages.error(request, f'ERRO. Já existe professor cadastrado com o email {email}.')
            return redirect('contratar')
        
        if Professor.objects.filter(disciplina=disciplina).exists():
            messages.error(request, f'ERRO. Já existe professor para a disciplina de {disc}.')
            return redirect('contratar')
            
        professor.disciplina = disciplina
        professor.save()    
        senha = request.POST.get('password')
        alunos = Aluno.objects.all()
        for aluno in alunos:
            rg = Aluno_tem_professor()
            if int(aluno.ano) == int(professor.ano):
                rg.professor = professor
                rg.aluno = aluno
                rg.save()
            
        user = User.objects.filter(username=professor.cpf).first()
        if user:
            return HttpResponse('Já existe esse usuário.')
        
        user = User.objects.create_user(username=('P' + professor.cpf), password=senha)
        messages.success(request, 'Professor contratado com sucesso!')
        return redirect('contratar')
    
    professores = Professor.objects.filter(status_cadastro="Inativo")
    return render(request, 'adicionaProfessor.html', {'professores': professores})

def matriculaProfessor(request):
    if request.method == 'POST':
        nome = request.POST.get("nome")
        data_nascimento = request.POST.get("data")
        sexo = request.POST.get("sexo")
        celular = request.POST.get("celular")
        endereco = request.POST.get("endereco")
        cpf = request.POST.get("cpf")
        rg = request.POST.get("rg")
        email = request.POST.get("email")
        ano = request.POST.get("ano")
        disc = request.POST.get("disciplina")
        professor = Professor()
        professor.nome = nome
        professor.data_nascimento = data_nascimento
        professor.sexo = sexo
        professor.celular = celular
        professor.endereco = endereco
        professor.cpf = cpf
        professor.rg = rg
        professor.email = email
        professor.ano = ano
        professor.status_cadastro = "Inativo"
        if disc == "Artes" and ano != '1':
            messages.error(request, 'ERRO. Só existe a matéria Artes pro 1° ano do ensino médio.')
            return redirect('cadastro_professor')
        if disc != "Artes":
            if ano == '1':
                disc = disc + " I"
            elif ano == '2':
                disc = disc + " II"
            elif ano == '3':
                disc = disc + " III"
                
        disciplina = Disciplina.objects.get(nome=disc)
                
        if Professor.objects.filter(cpf=cpf).exists():
            messages.error(request, f'ERRO. Já existe professor cadastrado com o CPF {cpf}.')
            return redirect('cadastro_professor')
        
        if Professor.objects.filter(rg=rg).exists():
            messages.error(request, f'ERRO. Já existe professor cadastrado com o RG {rg}.')
            return redirect('cadastro_professor')
        
        if Professor.objects.filter(email=email).exists():
            messages.error(request, f'ERRO. Já existe professor cadastrado com o email {email}.')
            return redirect('cadastro_professor')
        
        if Professor.objects.filter(disciplina=disciplina).exists():
            messages.error(request, f'ERRO. Já existe professor para a disciplina de {disc}.')
            return redirect('cadastro_professor')
            
        professor.disciplina = disciplina
        professor.save()    
        senha = request.POST.get('password')
        alunos = Aluno.objects.all()
        for aluno in alunos:
            rg = Aluno_tem_professor()
            if int(aluno.ano) == int(professor.ano):
                rg.professor = professor
                rg.aluno = aluno
                rg.save()
            
        user = User.objects.filter(username=professor.cpf).first()
        if user:
            return HttpResponse('Já existe esse usuário.')
        
        user = User.objects.create_user(username=('P' + professor.cpf), password=senha)
        messages.success(request, 'Professor contratado com sucesso!')
        return redirect('cadastro_professor')
    return render(request, 'matriculaProfessor.html')

@login_required(login_url="loginDiretor")
@user_passes_test(check_admin)
def relatorio(request):
    alunos = Aluno.objects.all()
    return render(request, 'relatorioAlunos.html', {'alunos': alunos})

@login_required(login_url="loginDiretor")
@user_passes_test(check_admin)
def editar(request):
    flag = 0
    if request.method == 'POST':
        if 'action' in request.POST:
            if request.POST['action'] == 'form1':
                id_entrada = request.POST.get("matricula")
                aluno = Aluno.objects.get(id=id_entrada)
                
                nome = request.POST.get("nome")
                data_nascimento = request.POST.get("data")
                sexo = request.POST.get("sexo")
                celular = request.POST.get("celular")
                endereco = request.POST.get("endereco")
                cpf = request.POST.get("cpf")
                rg = request.POST.get("rg")
                email = request.POST.get("email")
                ano = request.POST.get("ano")
                turma = request.POST.get("turma")
                
                if Aluno.objects.filter(cpf=cpf).exists():
                    aluno1 = Aluno.objects.get(cpf=cpf)
                    if aluno1 and aluno1.id != int(id_entrada):
                        messages.error(request, f'ERRO. Já existe aluno cadastrado com o CPF {cpf}.')
                        return redirect('editar')
                
                if Aluno.objects.filter(rg=rg).exists():
                    aluno1 = Aluno.objects.get(rg=rg)
                    if aluno1 and aluno1.id != int(id_entrada):
                        messages.error(request, f'ERRO. Já existe aluno cadastrado com o RG {rg}.')
                        return redirect('editar')
        
                if Aluno.objects.filter(email=email).exists():
                    aluno1 = Aluno.objects.get(email=email)
                    if aluno1 and aluno1.id != int(id_entrada):
                        messages.error(request, f'ERRO. Já existe aluno cadastrado com o email {email}.')
                        return redirect('editar')
                
                aluno.nome = nome
                aluno.data_nascimento = data_nascimento
                aluno.sexo = sexo
                aluno.endereco = endereco
                aluno.cpf = cpf
                aluno.rg = rg
                aluno.email = email
                aluno.celular = celular
                ano2 = aluno.ano
                aluno.ano = ano
                aluno.turma = turma
                aluno.save()
                
                if ano2 != ano:
                    try:
                        professores = Professor.objects.all()
                        for professor in professores:
                            rg = Aluno_tem_professor()
                            if int(aluno.ano) == int(professor.ano):
                                rg.professor = professor
                                rg.aluno = aluno
                                rg.save()
                                
                        disciplinas = Disciplina.objects.all()
                        for disciplina in disciplinas:
                            rg = Aluno_tem_disciplina()
                            if int(aluno.ano) == 1 and disciplina.id <= 12:
                                rg.disciplina = disciplina
                                rg.aluno = aluno
                                rg.save()
                            elif int(aluno.ano) == 2 and 13 <= disciplina.id <= 23:
                                rg.disciplina = disciplina
                                rg.aluno = aluno
                                rg.save()
                            elif int(aluno.ano) == 3 and 24 <= disciplina.id <= 34:
                                rg.disciplina = disciplina
                                rg.aluno = aluno
                                rg.save()
                    except:
                        pass
                        
                messages.success(request, 'Aluno editado com sucesso!')
                return redirect('editar')
            elif request.POST['action'] == 'form2':
                id_entrada = request.POST.get("matricula")
                aluno = Aluno.objects.get(id=id_entrada)
                user = User.objects.get(username=('A' + aluno.cpf))
                aluno.delete()
                user.delete()
                messages.success(request, 'Aluno apagado com sucesso!')
                return HttpResponseRedirect('editar/')
    elif request.method == 'GET' or 'pesquisa' in request.GET:
        flag = 1
        pesquisa = request.GET.get('pesquisa', '')
    if flag:
        alunos = Aluno.objects.all()
        return render(request, 'editarAluno.html', {'alunos': alunos, 'pesquisa': pesquisa})
    else:
        alunos = Aluno.objects.all()
        return render(request, 'editarAluno.html', {'alunos': alunos, 'pesquisa': ""})
    
    
@login_required(login_url="loginDiretor")
@user_passes_test(check_admin)
def editarProfessor(request):
    flag = 0
    if request.method == 'POST':
        if 'action' in request.POST:
            if request.POST['action'] == 'form1':
                id_entrada = request.POST.get("matricula")
                professor = Professor.objects.get(id=id_entrada)
                
                nome = request.POST.get("nome")
                data_nascimento = request.POST.get("data")
                sexo = request.POST.get("sexo")
                celular = request.POST.get("celular")
                endereco = request.POST.get("endereco")
                cpf = request.POST.get("cpf")
                rg = request.POST.get("rg")
                email = request.POST.get("email")
                if Professor.objects.filter(cpf=cpf).exists():
                    professor1 = Professor.objects.get(cpf=cpf)
                    if professor1 and professor1.id != int(id_entrada):
                        messages.error(request, f'ERRO. Já existe professor cadastrado com o CPF {cpf}.')
                        return redirect('editar_professor/')
                    
                if Professor.objects.filter(rg=rg).exists():
                    professor1 = Professor.objects.get(rg=rg)
                    if professor1 and professor1.id != int(id_entrada):
                        messages.error(request, f'ERRO. Já existe professor cadastrado com o RG {rg}.')
                        return redirect('editar_professor/')
                    
                if Professor.objects.filter(email=email).exists():
                    professor1 = Professor.objects.get(email=email)
                    if professor1 and professor1.id != int(id_entrada):
                        messages.error(request, f'ERRO. Já existe professor cadastrado com o email {email}.')
                        return redirect('editar_professor/')
        
        

                professor.nome = nome
                professor.data_nascimento = data_nascimento
                professor.sexo = sexo
                professor.endereco = endereco
                professor.cpf = cpf
                professor.rg = rg
                professor.email = email
                professor.celular = celular

                professor.save()
                messages.success(request, 'Professor editado com sucesso!')
                return HttpResponseRedirect('editar_professor/')
            elif request.POST['action'] == 'form2':
                id_entrada = request.POST.get("matricula")
                professor = Professor.objects.get(id=id_entrada)
                user = User.objects.get(username=('P' + professor.cpf))
                professor.delete()
                user.delete()
                messages.success(request, 'Professor apagado com sucesso!')
                return HttpResponseRedirect('editar_professor/')
    elif request.method == 'GET' or 'pesquisa' in request.GET:
        flag = 1
        pesquisa = request.GET.get('pesquisa', '')
    if flag:
        professores = Professor.objects.all()
        return render(request, 'editarProfessor.html', {'professores': professores, 'pesquisa': pesquisa})
    else:
        professores = Professor.objects.all()
        return render(request, 'editarProfessor.html', {'professores': professores, 'pesquisa': ""})
    
@login_required(login_url="loginDiretor")
@user_passes_test(check_admin)
def alugar_sala(request):
    if request.method == 'POST':
        if 'action' in request.POST:
            if request.POST['action'] == 'form':
                # Pedido aprovado
                id_entrada = request.POST.get("id")
                pedido = Pedido_Equipamento.objects.get(id=id_entrada)
                corpo_email = f"""
                <!DOCTYPE html>
                <html>
                <head>
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        color: #333;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        background-color: #fff;
                        border: 1px solid #ddd;
                        border-radius: 8px;
                        padding: 20px;
                        max-width: 600px;
                        margin: auto;
                    }}
                    h2, h3 {{
                        color: #0056b3;
                    }}
                    p {{
                        font-size: 16px;
                        line-height: 1.5;
                    }}
                    .bold {{
                        font-weight: bold;
                    }}
                </style>
                </head>
                <body>
                <div class="container">
                    <h2><b>Gestão Escolar Integrada</b></h2>
                    <h3><b>Pedido para alugar equipamentos ou sala</b></h3>
                    <h3 style="color: green;"><b>PEDIDO APROVADO!</b></h3>
                    <p><span class="bold">Professor:</span> {pedido.professor.nome}</p>
                    <p><span class="bold">Descrição:</span> {pedido.descricao}</p>
                </div>
                </body>
                </html>
                """

                msg = email.message.Message()
                msg['Subject'] = f'Pedido N°{pedido.id} ' + pedido.assunto
                msg['From'] = 'alugarequip5@gmail.com'
                msg['To'] = pedido.professor.email
                password = 'gohjrzflrcofzhdg' 
                msg.add_header('Content-Type', 'text/html; charset=UTF-8')
                msg.set_payload(corpo_email)

                s = smtplib.SMTP('smtp.gmail.com: 587')
                s.starttls()
                # Login Credenciais para enviar o email
                s.login(msg['From'], password)
                s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
                
                corpo_email2 = f"""
                <!DOCTYPE html>
                <html>
                <head>
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        color: #333;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        background-color: #fff;
                        border: 1px solid #ddd;
                        border-radius: 8px;
                        padding: 20px;
                        max-width: 600px;
                        margin: auto;
                    }}
                    h2, h3 {{
                        color: #0056b3;
                    }}
                    p {{
                        font-size: 16px;
                        line-height: 1.5;
                    }}
                    .bold {{
                        font-weight: bold;
                    }}
                </style>
                </head>
                <body>
                <div class="container">
                    <h2><b>Gestão Escolar Integrada</b></h2>
                    <h3><b>Pedido para alugar equipamentos ou sala</b></h3>
                    
                    <p><span class="bold">Professor:</span> {pedido.professor.nome}</p>
                    <p><span class="bold">Descrição:</span> {pedido.descricao}</p>
                </div>
                </body>
                </html>
                """
                
                msg = email.message.Message()
                msg['Subject'] = f'Pedido N°{pedido.id} ' + pedido.assunto
                msg['From'] = 'alugarequip5@gmail.com'
                msg['To'] = 'pedidosescola8@gmail.com'
                password = 'gohjrzflrcofzhdg' 
                msg.add_header('Content-Type', 'text/html; charset=UTF-8')
                msg.set_payload(corpo_email2)

                s = smtplib.SMTP('smtp.gmail.com: 587')
                s.starttls()
                # Login Credenciais para enviar o email
                s.login(msg['From'], password)
                s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
                pedido.delete()
                return HttpResponseRedirect('alugar_sala/')
            elif request.POST['action'] == 'form2':
                # Pedido negado
                id_entrada = request.POST.get("id")
                pedido = Pedido_Equipamento.objects.get(id=id_entrada)
                corpo_email = f"""
                <!DOCTYPE html>
                <html>
                <head>
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        color: #333;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        background-color: #fff;
                        border: 1px solid #ddd;
                        border-radius: 8px;
                        padding: 20px;
                        max-width: 600px;
                        margin: auto;
                    }}
                    h2, h3 {{
                        color: #0056b3;
                    }}
                    p {{
                        font-size: 16px;
                        line-height: 1.5;
                    }}
                    .bold {{
                        font-weight: bold;
                    }}
                </style>
                </head>
                <body>
                <div class="container">
                    <h2><b>Gestão Escolar Integrada</b></h2>
                    <h3><b>Pedido para alugar equipamentos ou sala</b></h3>
                    <h3 style="color: red;"><b>PEDIDO REJEITADO!</b></h3>
                    <p><span class="bold">Professor:</span> {pedido.professor.nome}</p>
                    <p><span class="bold">Descrição:</span> {pedido.descricao}</p>
                </div>
                </body>
                </html>
                """

                msg = email.message.Message()
                msg['Subject'] = f'Pedido N°{pedido.id} ' + pedido.assunto
                msg['From'] = 'alugarequip5@gmail.com'
                msg['To'] = pedido.professor.email
                password = 'gohjrzflrcofzhdg' 
                msg.add_header('Content-Type', 'text/html; charset=UTF-8')
                msg.set_payload(corpo_email )

                s = smtplib.SMTP('smtp.gmail.com: 587')
                s.starttls()
                # Login Credenciais para enviar o email
                s.login(msg['From'], password)
                s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
                pedido.delete()
                return HttpResponseRedirect('alugar_sala/')
    pedidos = Pedido_Equipamento.objects.all()
    return render(request, 'alugar_sala.html', {'pedidos': pedidos})

@login_required(login_url="loginDiretor")
@user_passes_test(check_admin)
def sairDiretor(request):
    logout(request)
    return HttpResponseRedirect(reverse('main'))


# ============================= ALUNO ======================================================


@login_required(login_url="aluno")
@user_passes_test(check_aluno)
def mainAluno(request):
    username = (request.user.username)[1:]
    usuario = Aluno.objects.get(cpf=username)
    return render(request, 'mainAluno.html', {'usuario': usuario})

def loginAluno(request):
    if request.method != 'POST':
        form = LoginForm()
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                cpf = 'A' + request.POST.get('username')
                senha = request.POST.get('password')
                user = authenticate(username=cpf, password=senha)
                aluno = Aluno.objects.get(cpf=request.POST.get('username'))
                if aluno.status_cadastro == "Inativo":
                    messages.error(request, 'O usuário está inativo.')
                    return redirect('aluno')
                
                if user:
                    authLogin(request, user)
                    next_url = request.GET.get('next', '')
                    if next_url == "/deslogar/": 
                        return redirect('ambiente')
                    return HttpResponseRedirect(reverse('ambiente'))  
                else:
                    messages.error(request, 'Usuário ou senha incorreto.')
                    return redirect('aluno')
            except:
                messages.error(request, 'Usuário ou senha incorreto.')
                return redirect('aluno')
            
    return render(request, 'loginAluno.html', {'form': form})

@login_required(login_url="aluno")
@user_passes_test(check_aluno)
def sairAluno(request):
    logout(request)
    return HttpResponseRedirect(reverse('aluno'))

@login_required(login_url="aluno")
@user_passes_test(check_aluno)
def contaAluno(request):
    aluno = Aluno.objects.get(cpf=(request.user.username[1:]))
    if request.method == 'POST':
        if 'action' in request.POST:
            if request.POST['action'] == 'form':
                img = request.FILES.get('imagem', None)
                aluno.perfil = img
                aluno.save()
                return redirect('conta/')
        else:
            nome = request.POST.get("nome")
            data_nascimento = request.POST.get("data")
            sexo = request.POST.get("sexo")
            celular = request.POST.get("celular")
            img = request.FILES.get('imagem_de_perfil', None)
            endereco = request.POST.get("endereco")
            cpf = request.POST.get("cpf")
            rg = request.POST.get("rg")
            email = request.POST.get("email")
            ano = request.POST.get("ano")
            if Aluno.objects.filter(email=email).exists():
                aluno1 = Aluno.objects.get(email=email)
                if aluno1 and aluno1.id != aluno.id:
                    messages.error(request, f'ERRO. Já existe aluno cadastrado com o email {email}.')
                    return redirect('conta/')

            aluno.nome = nome
            aluno.data_nascimento = data_nascimento
            aluno.sexo = sexo
            aluno.celular = celular
            aluno.endereco = endereco
            aluno.cpf = cpf
            aluno.rg = rg
            aluno.email = email
            aluno.ano = ano
            if img != None:
                aluno.perfil = img
            aluno.save()
            senha = request.POST.get('password')
            user = User.objects.get(username=request.user.username)
            if (senha != user.password and senha != ""):
                user.set_password(senha)
                user.save()
            
            messages.success(request, 'Aluno editado com sucesso!')
            return redirect('conta/')
    return render(request, 'configuracoesAluno.html', {'aluno': aluno})

@login_required(login_url="aluno")
@user_passes_test(check_aluno)
def planoEnsinoAluno(request):
    return render(request, 'planoEnsinoAluno.html')

@login_required(login_url="aluno")
@user_passes_test(check_aluno)
def notas(request):
    aluno = Aluno.objects.get(cpf=request.user.username[1:])
    disciplinas_do_aluno = Aluno_tem_disciplina.objects.filter(aluno_id=aluno.id).select_related('disciplina')
    context = []
    for ad in disciplinas_do_aluno:
        professor = Professor.objects.filter(disciplina=ad.disciplina).first()
        materiais = Materiais.objects.filter(disciplina=ad.disciplina)
        context.append({
            'disciplina_nome': ad.disciplina.nome,
            'status': ad.status,
            'nota': ad.nota,
            'professor_nome': professor.nome if professor else 'Sem professor na Disciplina',
            'disciplina_plano': ad.disciplina.planoensino if ad.disciplina else None,
            'materiais': materiais,
        })
    return render(request, 'notaDisciplinas.html', {'context': context})

def principal(request):
    return render(request, 'principal.html')

def alunoMensagem(request):
    aluno = Aluno.objects.get(cpf=(request.user.username[1:]))
    professores = Professor.objects.prefetch_related('aluno_tem_professor_set').filter(aluno_tem_professor__aluno=aluno)
    if request.method == 'POST':
        professor = request.POST.get('professor')
        titulo = request.POST.get('titulo')
        mensagem = request.POST.get('mensagem')
        disc = Disciplina.objects.get(nome=(professor.split(' - ')[1]))
        professor = Professor.objects.get(disciplina=disc)
        print(professor.nome)
        corpo_email = f"""
                <!DOCTYPE html>
                <html>
                <head>
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        color: #333;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        background-color: #fff;
                        border: 1px solid #ddd;
                        border-radius: 8px;
                        padding: 20px;
                        max-width: 600px;
                        margin: auto;
                    }}
                    h2, h3 {{
                        color: #0056b3;
                    }}
                    p {{
                        font-size: 16px;
                        line-height: 1.5;
                    }}
                    .bold {{
                        font-weight: bold;
                    }}
                </style>
                </head>
                <body>
                <div class="container">
                    <h2><b>Gestão Escolar Integrada</b></h2>
                    <h3><b>Mensagem para o professor {professor.nome}</b></h3>
                    <h3><b>Aluno: {aluno.nome}</b></h3>
                    <h3><b>Turma: {aluno.turma}</b></h3>
                    <h3><b>Email de contato: {aluno.email}</b></h3>
                    <p><span class="bold">Mensagem:</span> {mensagem}</p>
                </div>
                </body>
                </html>
                """

        msg = email.message.Message()
        msg['Subject'] = titulo
        msg['From'] = 'alugarequip5@gmail.com'
        msg['To'] = professor.email
        password = 'gohjrzflrcofzhdg' 
        msg.add_header('Content-Type', 'text/html; charset=UTF-8')
        msg.set_payload(corpo_email )

        s = smtplib.SMTP('smtp.gmail.com: 587')
        s.starttls()
        # Login Credenciais para enviar o email
        s.login(msg['From'], password)
        s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
        return HttpResponseRedirect('mensagem/')
        
    return render(request, 'contactarProfessor.html', {'professores': professores})