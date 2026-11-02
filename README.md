# Dashboard Financeiro

Uma aplicação web simples de controle financeiro que eu desenvolvi para praticar o desenvolvimento de uma solução completa com Python, JavaScript e armazenamento em JSON.

O projeto nasceu da ideia de organizar, em uma única tela, quanto entra de dinheiro, quais são os gastos fixos e quais pagamentos ainda estão pendentes. Minha prioridade aqui foi criar uma interface limpa, responsiva e fácil de usar, mantendo o projeto leve e acessível tanto no computador quanto em dispositivos móveis.

## Sobre o projeto

O Dashboard Financeiro permite que o usuário:

- crie uma conta e faça login;
- informe sua renda mensal;
- registre gastos obrigatórios de água, luz e internet;
- adicione pagamentos pendentes e seus respectivos valores;
- acompanhe o total de entradas, gastos e saldo disponível;
- visualize imediatamente quando o saldo está positivo ou negativo;
- utilize os dados localmente, com informações armazenadas em um arquivo JSON;
- acesse a aplicação pela rede local, além de executá-la diretamente no próprio computador.

A interface usa preto, branco, verde para valores positivos e vermelho para valores negativos. Também adicionei transições suaves, animações discretas e uma experiência responsiva pensada principalmente para notebook e celular.

## Tecnologias utilizadas

- Python
- HTML5
- CSS3
- JavaScript
- API HTTP com `http.server`
- JSON como banco de dados local
- `ThreadingHTTPServer`

Nenhuma instalação externa de Python é necessária para executar o projeto básico.

## Estrutura

```text
Dashboard/
├── app.py
├── database.json
├── README.md
├── requirements.txt
└── static/
    ├── index.html
    ├── styles.css
    └── app.js
```

## Como executar

1. Entre na pasta do projeto:

```bash
cd Dashboard
```

2. Execute o servidor:

```bash
python3 app.py
```

3. Abra o endereço exibido no terminal, normalmente:

```text
http://localhost:5469
```

Para acessar em outro dispositivo conectado à mesma rede, utilize o endereço IP do computador no lugar de `localhost`, por exemplo:

```text
http://192.168.1.10:5469
```

## Armazenamento dos dados

Todas as informações são mantidas no arquivo `database.json`. Ele funciona como o banco de dados local deste projeto e guarda usuários, senhas, rendas, contas obrigatórias e pagamentos pendentes.

## Segurança — ponto importante

**A segurança não é o foco deste projeto.** Ele foi criado principalmente para estudo, prática e desenvolvimento da interface e da lógica financeira.

Neste momento, o sistema:

- armazena a senha diretamente no `database.json`, sem hash;
- mantém as sessões em memória, sem um sistema persistente de autenticação;
- não possui criptografia de dados em disco;
- não está preparado para produção;
- não deve ser exposto publicamente na internet sem alterações importantes;
- não deve armazenar senhas ou informações financeiras reais e sensíveis.

Esse README deixa explícito que o objetivo do projeto é demonstrar uma aplicação funcional de forma simples. Antes de considerar uma versão pública ou de produção, eu recomendaria implementar hash de senhas, HTTPS, proteção contra abuso, validação robusta, variáveis de ambiente, banco de dados apropriado e mecanismos de autorização seguros.

## Possíveis melhorias

Algumas ideias que pretendo explorar em versões futuras são:

- cadastrar novas categorias de gastos;
- separar entradas recorrentes e pontuais;
- adicionar histórico mensal;
- criar gráficos e relatórios;
- configurar datas de vencimento;
- exibir alertas de contas próximas do vencimento;
- exportar os dados em CSV;
- adicionar modo claro;
- migrar o banco JSON para SQLite ou outro banco persistente;
- melhorar completamente a autenticação e a segurança.

## Objetivo

Eu fiz este projeto para estudar integração entre front-end e back-end, desenvolvimento de APIs em Python sem frameworks, manipulação de arquivos JSON, criação de interfaces responsivas e organização de dados financeiros.

## Autor

**Pablo Emidio dos Santos**

Projeto desenvolvido como parte dos meus estudos e experimentos com programação.

---

Projeto criado para fins educacionais e de demonstração. Não utilize em produção com dados reais sem implementar os cuidados de segurança necessários.
