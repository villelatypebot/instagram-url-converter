# Instagram Profile Picture Proxy

## Sobre

Este projeto resolve o problema das URLs de imagens de perfil do Instagram que contu00eam hashes e paru00e2metros que expiram, tornando difu00edcil incorporu00e1-las em sistemas como o Nifty Images para imagens dinu00e2micas.

## Demo Online

Vocu00ea pode testar o servidor em:

[https://seu-app.herokuapp.com](https://seu-app.herokuapp.com) (Substitua pelo seu URL apu00f3s o deploy)

## Como usar com Nifty Images

Use a URL no formato:

```
https://seu-app.herokuapp.com/image/nome_usuario.jpg
```

No Nifty Images:

```
https://img1.niftyimages.com/4340a5b3-51e0-4924-a98a-473713828179?image=https://seu-app.herokuapp.com/image/nome_usuario.jpg
```

## Deploy

### Heroku

```bash
git clone https://github.com/seu-usuario/instagram-profile-proxy.git
cd instagram-profile-proxy
heroku create
git push heroku main
```

### Replit

1. Crie uma conta no [Replit](https://replit.com)
2. Importe este repositu00f3rio
3. Clique em Run

## Desenvolvimento Local

```bash
# Instale as dependu00eancias
pip install -r requirements.txt

# Execute o servidor
python web_server_example.py

# Teste com o script
python test_nifty.py nome_usuario_instagram
```

## Licenu00e7a

MIT