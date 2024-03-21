<h1>Documentação</h1>

<h3>Instruções de deploy</h3>

Fazer o deploy de um projeto web desenvolvido com Python e Django envolve vários passos e decisões importantes. Abaixo, vou destacar um processo geral e, em seguida, mencionar especificidades de alguns serviços de hospedagem populares que você mencionou.

<h3>Processo Geral de Deploy com Django</h3>
<b>Preparação do Projeto:</b> 
Certifique-se de que o seu projeto esteja utilizando um ambiente virtual e que todas as dependências estejam especificadas em um arquivo requirements.txt. Isso garante que o ambiente de produção possa ser configurado da mesma forma que o de desenvolvimento.

<b>Configurações para Produção:</b> 
Revise as configurações do seu projeto Django para garantir que ele esteja pronto para produção. Isso inclui desabilitar o modo de depuração (DEBUG = False), configurar o ALLOWED_HOSTS, configurar o banco de dados de produção, e garantir que arquivos estáticos e de mídia sejam corretamente servidos.

<b>Escolha do Serviço de Hospedagem:</b> 
A escolha do serviço de hospedagem depende de vários fatores, incluindo custo, facilidade de uso, escalabilidade e suporte para tecnologias específicas.

<h3>Serviços de Hospedagem Sugeridos</h3>

<b>Vercel:</b>
Vercel não é tradicionalmente usado para hospedar aplicações Django, pois é mais focado em front-end e aplicações serverless. Você poderia usar Vercel para hospedar o front-end da sua aplicação, mas precisaria de outro serviço para o back-end.

<h4><b>PythonAnywhere</b></h4>
PythonAnywhere é uma ótima opção para projetos Django menores ou em estágio inicial. Oferece uma configuração relativamente simples e um ambiente já preparado para Python e Django. Aqui estão os passos básicos:

<b>1.</b> Crie uma conta e escolha seu plano de hospedagem.

<b>2.</b> Use a interface do PythonAnywhere para clonar seu projeto do GitHub ou outro repositório.

<b>3.</b> Configure seu ambiente virtual e instale as dependências do seu projeto a partir do requirements.txt.

<b>4.</b> Configure seu arquivo wsgi.py no PythonAnywhere para corresponder ao seu projeto Django.

<b>5.</b> Utilize as ferramentas do PythonAnywhere para configurar o servidor web e apontar para sua aplicação.
   
<h4>AWS Elastic Beanstalk</h4>
AWS Elastic Beanstalk oferece uma solução mais escalável e robusta, mas com uma curva de aprendizado mais acentuada. É importante monitorar os custos, pois a AWS pode gerar cobranças inesperadas se não for bem configurada.

<b>1.</b> Crie uma conta na AWS e configure o Elastic Beanstalk.

<b>2.</b> Prepare seu aplicativo Django, garantindo que ele esteja pronto para produção conforme mencionado anteriormente.

<b>3.</b> Utilize a AWS CLI para fazer o deploy do seu aplicativo no Elastic Beanstalk, o qual irá automatizar o processo de provisionamento de infraestrutura.

<b>4.</b> Configure detalhes adicionais, como banco de dados, variáveis de ambiente e mais através do console do Elastic Beanstalk.


<h3>Dicas Finais</h3>
<b>Monitoramento e Manutenção:</b> Independente do serviço escolhido, é importante monitorar o desempenho e a saúde da sua aplicação e estar pronto para fazer ajustes conforme necessário.
<b>Segurança:</b> Não se esqueça de configurar aspectos de segurança, como o uso de HTTPS e a gestão cuidadosa de senhas e chaves de API.
<b>Documentação:</b> Cada serviço oferece sua própria documentação, que deve ser consultada para detalhes específicos e melhores práticas.
<b>Serviço:</b> Escolher o serviço de hospedagem certo e configurar adequadamente o ambiente de produção são etapas cruciais para o sucesso do seu projeto Django. Avalie suas necessidades, orçamento e recursos disponíveis para fazer a melhor escolha.

## Modelagem de banco de dados

Coloque aqui a modelagem do banco de dados desenvolvido no projeto. Você pode colocar diagramas conceituais e lógicos, ou até mesmo descrever textualmente o que cada uma das tabelas e atributos representam.

<h3>Código SQL em PostgreSQL</h3>
Um código SQL se refere à escrita de instruções em SQL (Structured Query Language), uma linguagem de programação projetada para gerenciar e manipular dados armazenados em sistemas de gerenciamento de banco de dados relacional (RDBMS). SQL é amplamente utilizado para inserir, consultar, atualizar e deletar dados, além de gerenciar estruturas de banco de dados e controlar o acesso aos dados.

```sql
CREATE TABLE aluno (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL DEFAULT '',
    data_nascimento DATE NULL,
    sexo VARCHAR(50) NOT NULL DEFAULT '',
    celular VARCHAR(30) DEFAULT '',
    endereco TEXT NULL,
    cpf VARCHAR(30) NOT NULL DEFAULT '' UNIQUE,
    rg VARCHAR(50) NOT NULL DEFAULT '' UNIQUE,
    email VARCHAR(100) NULL UNIQUE,
    ano INTEGER NOT NULL DEFAULT 0,
    turma CHAR(1) NOT NULL DEFAULT '',
    perfil VARCHAR DEFAULT 'fotos/padrao.png',
    status_cadastro VARCHAR(100) NOT NULL DEFAULT 'Ativo'
);

CREATE TABLE plano_ensino (
    id SERIAL PRIMARY KEY,
    plano_ensino VARCHAR DEFAULT NULL
);

CREATE TABLE disciplina (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100),
    planoensino_id INTEGER NULL REFERENCES plano_ensino(id) ON DELETE CASCADE
);

CREATE TABLE materiais (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100),
    local VARCHAR DEFAULT NULL,
    disciplina_id INTEGER NOT NULL REFERENCES disciplina(id) ON DELETE CASCADE
);

CREATE TABLE aluno_tem_disciplina (
    id SERIAL PRIMARY KEY,
    aluno_id INTEGER NOT NULL REFERENCES aluno(id) ON DELETE CASCADE,
    disciplina_id INTEGER NOT NULL REFERENCES disciplina(id) ON DELETE CASCADE,
    ano CHAR(4) DEFAULT '2023',
    status VARCHAR(10) DEFAULT 'Cursando',
    nota FLOAT DEFAULT 0.00,
    UNIQUE (aluno_id, disciplina_id, ano)
);

CREATE TABLE professor (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL DEFAULT '',
    data_nascimento DATE NULL,
    sexo VARCHAR(50) NOT NULL DEFAULT '',
    celular VARCHAR(30) DEFAULT '',
    endereco TEXT NULL,
    cpf VARCHAR(30) NOT NULL DEFAULT '' UNIQUE,
    rg VARCHAR(50) NOT NULL DEFAULT '' UNIQUE,
    email VARCHAR(100) NULL UNIQUE,
    ano INTEGER NOT NULL DEFAULT 0,
    disciplina_id INTEGER NOT NULL REFERENCES disciplina(id) ON DELETE CASCADE,
    perfil VARCHAR DEFAULT 'fotos/padrao.png',
    status_cadastro VARCHAR(100) NOT NULL DEFAULT 'Ativo'
);

CREATE TABLE pedido_equipamento (
    id SERIAL PRIMARY KEY,
    professor_id INTEGER NOT NULL REFERENCES professor(id) ON DELETE CASCADE,
    assunto VARCHAR(100) DEFAULT '',
    descricao TEXT NULL
);

CREATE TABLE aluno_tem_professor (
    aluno_id INTEGER NOT NULL REFERENCES aluno(id) ON DELETE CASCADE,
    professor_id INTEGER NOT NULL REFERENCES professor(id) ON DELETE CASCADE,
    PRIMARY KEY (aluno_id, professor_id)
);
```

<h3>Diagrama Entidade Relacional (DER)</h3>
O Diagrama Entidade-Relacional (DER) é uma ferramenta de modelagem usada para representar sistemas de informação de maneira abstrata e conceitual. Sua principal função é ajudar no projeto de bancos de dados, facilitando a compreensão das estruturas de dados, suas relações e como estas podem ser implementadas em um sistema de gerenciamento de banco de dados (SGBD).

<img src="img/DER projeto Final.jpg" width="1000px" style="border-radius: 50%;">


# DUVIDAS
*Tem duvidas? envie um email:* viniciuspadilhavieira@hotmail.com
