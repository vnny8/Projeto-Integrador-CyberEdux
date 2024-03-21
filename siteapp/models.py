from django.db import models

class Aluno(models.Model):
    nome = models.CharField(max_length=100, null=False, default="")
    data_nascimento = models.DateField(null=True, blank=True)
    sexo = models.CharField(max_length=50, null=False, default="")
    celular = models.CharField(max_length=30, default="")
    endereco = models.TextField(null=True)
    cpf = models.CharField(max_length=30, null=False, default="", unique=True)
    rg = models.CharField(max_length=50, null=False, default="", unique=True)
    email = models.CharField(max_length=100, null=True, unique=True)
    ano = models.IntegerField(null=False, default=0)
    turma = models.CharField(max_length=1, null=False, default="")
    perfil = models.ImageField(upload_to='fotos/', default='fotos/padrao.png')
    status_cadastro = models.CharField(max_length=100, null=False, default="Ativo")
    
class Plano_Ensino(models.Model):
    plano_ensino = models.FileField(upload_to='pdfs/', default=None)
    
class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    planoensino = models.ForeignKey(Plano_Ensino, on_delete=models.CASCADE, null=True)
    
class Materiais(models.Model):
    nome = models.CharField(max_length=100)
    local = models.FileField(upload_to='pdfs/', default=None)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    
class Aluno_tem_disciplina(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    ano = models.CharField(max_length=4, default="2023")
    status = models.CharField(max_length=10, default="Cursando")
    nota = models.FloatField(null=True, default=0.00)
    
    class Meta:
        unique_together = (('aluno', 'disciplina', 'ano'),)
    
class Professor(models.Model):
    nome = models.CharField(max_length=100, null=False, default="")
    data_nascimento = models.DateField(null=True, blank=True)
    sexo = models.CharField(max_length=50, null=False, default="")
    celular = models.CharField(max_length=30, default="")
    endereco = models.TextField(null=True)
    cpf = models.CharField(max_length=30, null=False, default="", unique="True")
    rg = models.CharField(max_length=50, null=False, default="", unique="True")
    email = models.CharField(max_length=100, null=True, unique="True")
    ano = models.IntegerField(null=False, default=0)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, default=None)
    perfil = models.ImageField(upload_to='fotos/', default='fotos/padrao.png')
    status_cadastro = models.CharField(max_length=100, null=False, default="Ativo")
    
class Pedido_Equipamento(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, default=None)
    assunto = models.CharField(max_length=100, default="")
    descricao = models.TextField(null=True)
    
class Aluno_tem_professor(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
