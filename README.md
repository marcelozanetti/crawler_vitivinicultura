# TechChallenge - API Vitivinicultura

API desenvolvida para o TechChallenge do curso PosTech - Machine Learning, que realiza web scraping de dados públicos da vitivinicultura brasileira (Embrapa) utilizando Python, Flask, Selenium e JWT.

## Funcionalidades

- **Autenticação JWT**: Rotas protegidas por login.
- **Web Scraping**: Coleta de dados dinâmicos do site da Embrapa usando Selenium.
- **Rotas de API**:
  - `/login`: Autenticação e geração de token JWT.
  - `/producao`: Lista de vinhos e derivados produzidos por exercício.
  - `/comercializacao`: Lista de vinhos e derivados comercializados por exercício.
  - `/processamento`: Lista de produtos processados por exercício.
  - `/exportacao`: Lista de vinhos e derivados exportados por exercício.
- **Swagger**: Documentação interativa disponível em `/apidocs`.

## Tecnologias Utilizadas

- Python 3.12
- Flask
- Flask-JWT-Extended
- Flask-SQLAlchemy
- Selenium + webdriver-manager
- Gunicorn
- Pandas
- Flasgger (Swagger UI)

## Como rodar localmente

```bash
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo

python -m venv venv
source venv/bin/activate

pip install -r [requirements.txt](http://_vscodecontentref_/0)

python -m api.app
