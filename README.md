# Instagram URL Converter

Esta aplicação ajuda a obter URLs diretas de imagens de perfil do Instagram, solucionando o problema das URLs dinâmicas com hashes que o Facebook/Meta introduziu, dificultando seu uso em serviços de imagens dinâmicas como o Nifty Images.

## Funcionalidades

- Obtém URLs diretas de imagens de perfil do Instagram, sempre terminando com `.jpg`
- Fornece endpoints de API para integração com outros serviços
- Interface web simples para testar e obter URLs
- Cache de imagens para melhorar a performance
- Suporta múltiplos formatos de saída (URL, JSON, Base64)
- Desenvolvido para ser facilmente hospedado em serviços como Heroku, Render, Railway

## Como Usar

### Interface Web

1. Acesse a aplicação web
2. Digite o nome de usuário do Instagram
3. Clique em "Obter URLs"
4. Use as URLs fornecidas conforme necessário

### API

#### Obter URL direta da imagem:
```
GET /image/{username}.jpg
```

#### Obter dados JSON com a URL:
```
GET /api/profile-pic/{username}
```

#### Obter imagem em formato Base64:
```
GET /api/profile-pic/{username}?format=base64
```

## Hospedagem

### Heroku

1. Crie uma conta no [Heroku](https://heroku.com/)
2. Instale o [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. Clone este repositório e acesse a pasta do projeto
4. Execute os seguintes comandos:

```bash
# Login no Heroku
heroku login

# Criar um novo app no Heroku
heroku create instagram-url-converter

# Enviar o código para o Heroku
git push heroku main

# Abrir a aplicação no navegador
heroku open
```

### Render

1. Crie uma conta no [Render](https://render.com/)
2. Crie um novo Web Service
3. Conecte ao seu repositório GitHub
4. Configure:
   - Nome: instagram-url-converter
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn main:app`
5. Clique em "Create Web Service"

### Railway

1. Crie uma conta no [Railway](https://railway.app/)
2. Crie um novo projeto
3. Selecione "Deploy from GitHub repo"
4. Conecte ao seu repositório GitHub
5. Configure as variáveis de ambiente se necessário
6. Railway detectará automaticamente o Procfile e requirements.txt

## Executando Localmente

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar o servidor
python main.py
```

O servidor estará disponível em `http://localhost:5000`

## Estrutura do Projeto

- `main.py` - Aplicação web Flask principal
- `get_profile_pic.py` - Módulo que extrai imagens de perfil do Instagram
- `requirements.txt` - Dependências do projeto
- `Procfile` - Configuração para hospedagem (Heroku, etc.)

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Nota Legal

Esta aplicação é destinada a uso educacional e pessoal. O uso desta ferramenta deve estar em conformidade com os Termos de Serviço do Instagram/Meta. 