from django.contrib import admin
from django.urls import path
from siteapp import views
from django.http import HttpResponseRedirect
from django.conf import settings
from django.conf.urls.static import static

def redirecionar(request, pagina):
    pagina = "/" + pagina + "/"
    print(pagina)
    return HttpResponseRedirect(pagina)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.main, name="home"),
    path('login/', views.login, name="login"),
    path('login/<str:pagina>/', redirecionar),
    path('configuracoes/', views.configuracoes),
    path('nota_alunos/', views.nota_alunos),
    path('alugar/', views.alugar),
    path('home/<str:pagina>/', redirecionar),
    path('configuracoes/<str:pagina>/', redirecionar),
    path('alugar/<str:pagina>/', redirecionar),
    path('nota_alunos/<str:pagina>/', redirecionar),
    path('logout/', views.sair, name="sair"),
    
    path('diretor/', views.loginDiretor, name="loginDiretor"),
    path('diretor/<str:pagina>/', redirecionar),
    path('main/', views.mainDiretor, name="main"),
    path('matricula/', views.matricula, name="matricula"),
    path('contratar/', views.contratar, name="contratar"),
    path('relatorio/', views.relatorio),
    path('alugar_sala/', views.alugar_sala),
    path('editar/', views.editar, name="editar"),
    path('editar/<str:pagina>/', redirecionar),
    path('editar_professor/', views.editarProfessor, name="editarProfessor"),
    path('editar_professor/<str:pagina>/', redirecionar),
    path('main/<str:pagina>/', redirecionar),
    path('matricula/<str:pagina>/', redirecionar),
    path('contratar/<str:pagina>/', redirecionar),
    path('relatorio/<str:pagina>/', redirecionar),
    path('alugar_sala/<str:pagina>/', redirecionar),
    path('sair/', views.sairDiretor, name="sair2"),
    
    path('aluno/', views.loginAluno, name="aluno"),
    path('aluno/<str:pagina>/', redirecionar),
    path('ambiente/', views.mainAluno, name="ambiente"),
    path('deslogar/', views.sairAluno, name="deslogar"),
    path('ambiente/<str:pagina>/', redirecionar),
    path('conta/', views.contaAluno),
    path('conta/<str:pagina>/', redirecionar),
    path('plano_ensino/', views.planoEnsinoAluno),
    path('plano_ensino/<str:pagina>/', redirecionar),
    path('notas/', views.notas, name="notas"),
    path('notas/<str:pagina>/', redirecionar),
    path('mensagem/', views.alunoMensagem, name="mensagem"),
    path('mensagem/<str:pagina>/', redirecionar),
    
    path('', views.principal),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
