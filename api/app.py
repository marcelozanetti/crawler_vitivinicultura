
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from config import config
from config import logger
from models.usuarios import Usuario   
from flasgger import Swagger
from models import db  # Importa o db de models/__init__.py
from crawler_vitivinicultura import crawler_lista_producaoEComercializacao
from crawler_vitivinicultura import crawler_lista_processamento
from crawler_vitivinicultura import crawler_lista_importexport

# Inicialização da aplicação Flask
app = Flask(__name__)
app.config.from_object(config)

app.config['SWAGGER'] = {
    'title': 'API - Informações da Embrapa',
    'uiversion': 3,
    'securityDefinitions': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Insira o token JWT no formato: Bearer <seu_token>'
        }
    },
    'security': [{'Bearer': []}]
}

# Configuração do JWT, do Banco de dados e do Swagger
db.init_app(app)  # Inicializa o banco de dados com o app
jwt = JWTManager(app)
swagger = Swagger(app)

#rotas
@app.route('/login', methods=['POST'])
def login():
    """
    Faz o login do usuário e retorna um token JWT.
    ---
    tags:
      - Administracao    
    parameters:
        - in: body
          name: usuario
          description: Dados do usuário
          required: true
          schema:
            type: object
            properties:
              usuario:
                type: string
              senha:
                type: string
    responses:
        200:
            description: Login bem-sucedido, retorna o token JWT
        401:
            description: Credenciais inválidas
    """
    data = request.get_json()
    user = Usuario.query.filter_by(usuario=data['usuario']).first()
    if user and user.senha == data['senha']:
        # Converter o ID para string
        token = create_access_token(identity=str(user.id))
        return jsonify(access_token=token), 200
    return jsonify({"msg": "Credenciais inválidas"}), 401

@app.route('/usuarios', methods=['POST'])
@jwt_required()
def register_user():
    """
    Registra um novo usuário.
    ---
    tags:
      - Administracao
    parameters:
        - in: body
          name: user
          description: Dados do usuário
          required: true
          schema:
            type: object
            properties:
              usuario:
                type: string
              email:
                type: string
                format: email
              senha:
                type: string
    responses:
        201:
            description: Usuário cadastrado com sucesso
        400:
            description: Usuário já cadastrado
    security:
      - Bearer: []            
    """
    data = request.get_json()
    if Usuario.query.filter((Usuario.usuario == data['usuario']) | (Usuario.email == data['email'])).first():
        return jsonify({"msg": "Usuário ou email já cadastrado"}), 400
    new_user = Usuario(usuario=data['usuario'], email=data['email'], senha=data['senha'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "Usuário cadastrado com sucesso"}), 201

@app.route('/producao', methods=['GET'])
@jwt_required()
def endpoint_lista_produtos():
    """
    Retorna a lista de vinhos e derivados produzidos por exercício.
    ---
    tags:
      - Dados da Vitivinicultura
    parameters:
      - name: exercicio
        in: query
        type: integer
        required: true
        description: Exercício desejado      
    responses:
      200:
        description: Lista de produtos agrupados por exercício.
    security:
      - Bearer: []
    """

    exercicio = request.args.get('exercicio', type=int)
    if exercicio is None:
        return jsonify({"erro": "Parâmetro 'exercicio' é obrigatório e deve ser inteiro."}), 400
    if exercicio < 1970 or exercicio > 2023:
        return jsonify({"erro": "O parâmetro 'exercicio' deve estar entre 1970 e 2023."}), 400

    resultado = crawler_lista_producaoEComercializacao("http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_02", exercicio)
    return jsonify({"dados": resultado})

@app.route('/processamento', methods=['GET'])
@jwt_required()
def endpoint_lista_processamento():
    """
    Retorna a lista de uvas viníferas processadas por exercício.
    ---
    tags:
      - Dados da Vitivinicultura
    parameters:
      - name: exercicio
        in: query
        type: integer
        required: true
        description: Exercício desejado         
    responses:
      200:
        description: Lista de uvas viníferas processadas no exercício.
    security:
      - Bearer: []
    """
    exercicio = request.args.get('exercicio', type=int)
    if exercicio is None:
        return jsonify({"erro": "Parâmetro 'exercicio' é obrigatório e deve ser inteiro."}), 400
    if exercicio < 1970 or exercicio > 2023:
        return jsonify({"erro": "O parâmetro 'exercicio' deve estar entre 1970 e 2023."}), 400

    resultado = crawler_lista_processamento(exercicio)
    return jsonify({"dados": resultado})

@app.route('/comercializacao', methods=['GET'])
@jwt_required()
def endpoint_lista_comercializacao():
    """
    Retorna a lista de vinhos e derivados comercialização por exercício.
    ---
    tags:
      - Dados da Vitivinicultura
    parameters:
      - name: exercicio
        in: query
        type: integer
        required: true
        description: Exercício desejado           
    responses:
      200:
        description: Lista de vinhos e derivados comercializados por exercício.
    security:
      - Bearer: []
    """
    exercicio = request.args.get('exercicio', type=int)
    if exercicio is None:
        return jsonify({"erro": "Parâmetro 'exercicio' é obrigatório e deve ser inteiro."}), 400
    if exercicio < 1970 or exercicio > 2023:
        return jsonify({"erro": "O parâmetro 'exercicio' deve estar entre 1970 e 2023."}), 400

    resultado = crawler_lista_producaoEComercializacao("http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_04", exercicio)
    return jsonify({"dados": resultado})

@app.route('/importacao', methods=['GET'])
@jwt_required()
def endpoint_lista_importacao():
    """
    Retorna a lista de vinhos e derivados importados por exercício.
    ---
    tags:
      - Dados da Vitivinicultura
    parameters:
      - name: exercicio
        in: query
        type: integer
        required: true
        description: Exercício desejado           
    responses:
      200:
        description: Lista de vinhos e derivados importados por tipo de vinho e exercício.
    security:
      - Bearer: []
    """

    exercicio = request.args.get('exercicio', type=int)
    if exercicio is None:
        return jsonify({"erro": "Parâmetro 'exercicio' é obrigatório e deve ser inteiro."}), 400
    if exercicio < 1970 or exercicio > 2023:
        return jsonify({"erro": "O parâmetro 'exercicio' deve estar entre 1970 e 2023."}), 400

    resultado = crawler_lista_importexport("http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_05", exercicio)
    return jsonify({"dados": resultado})

@app.route('/exportacao', methods=['GET'])
@jwt_required()
def endpoint_lista_exportacao():
    """
    Retorna a lista de vinhos e derivados importados por exercício.
    ---
    tags:
      - Dados da Vitivinicultura
    parameters:
      - name: exercicio
        in: query
        type: integer
        required: true
        description: Exercício desejado            
    responses:
      200:
        description: Lista de vinhos e derivados importados por tipo de vinho e exercício.
    security:
      - Bearer: []
    """
    exercicio = request.args.get('exercicio', type=int)
    if exercicio is None:
        return jsonify({"erro": "Parâmetro 'exercicio' é obrigatório e deve ser inteiro."}), 400
    if exercicio < 1970 or exercicio > 2023:
        return jsonify({"erro": "O parâmetro 'exercicio' deve estar entre 1970 e 2023."}), 400

    resultado = crawler_lista_importexport("http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_06", exercicio)
    return jsonify({"dados": resultado})


#if __name__ == '__main__':
#    app.run(debug=False)