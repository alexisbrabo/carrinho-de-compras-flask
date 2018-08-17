import os
from datetime import date
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import pymysql
pymysql.install_as_MySQLdb()


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:qwe123@localhost:4306/vendas_python"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), unique=True)
    
    def __init__(self, nome):
        self.nome = nome


class Listacompra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_cadastro = db.Column(db.DateTime, server_default=db.func.now())
    produtos = db.relationship("Produto")


class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), unique=True)
    valor = db.Column(db.Numeric(10,2))
    listacompra_id = db.Column(db.Integer, db.ForeignKey('listacompra.id'))

    def __init__(self, nome, valor, listacompra_id):
        self.nome = nome
        if valor is '':
            self.valor = None
        else:
            self.valor = valor
        self.listacompra_id = listacompra_id


db.create_all()
db.session.commit()


class ClienteSchema(ma.Schema):
    class Meta:
        # Campos para expor
        fields = ('id', 'nome')


class ProdutoSchema(ma.Schema):
    class Meta:
        # Campos para expor
        fields = ('id', 'nome', 'valor', 'listacompra_id')

produto_schema = ProdutoSchema()
produtos_schema = ProdutoSchema(many=True)


class ListacompraSchema(ma.Schema):
    produtos = ma.Nested('ProdutoSchema', many=True)
    class Meta:
        # Campos para expor
        fields = ('id', 'data_cadastro', 'produtos')
    

user_schema = ClienteSchema()
users_schema = ClienteSchema(many=True)
lista_schema = ListacompraSchema()
listas_schema = ListacompraSchema(many=True)


# endpoint para criar cliente
@app.route("/cliente", methods=["POST"])
def add_user():
    nome = request.json['nome']
    
    new_user = Cliente(nome)

    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user)


# endpoint para criar produto
@app.route("/produto", methods=["POST"])
def add_produto():
    nome = request.json['nome']
    valor = request.json['valor']
    listacompra_id = request.json['listacompra_id']
    
    new_produto = Produto(nome,valor,listacompra_id)

    db.session.add(new_produto)
    db.session.commit()

    return produto_schema.jsonify(new_produto)


# endpoint para atualizar produto
@app.route("/produto/<id>", methods=["PUT"])
def produto_update(id):

    produto = Produto.query.get(id)
    
    nome = request.json['nome']
    valor = request.json['valor']
    
    produto.nome = nome
    produto.valor = valor

    db.session.commit()
    return produto_schema.jsonify(produto)


# endpoint para criar lista de compras
@app.route("/listacompras", methods=["POST"])
def add_lista():
    new_lista = Listacompra()

    db.session.add(new_lista)
    db.session.commit()

    return lista_schema.jsonify(new_lista)


# endpoint para mostrar todas as listas
@app.route("/listacompras", methods=["GET"])
def get_lista():
    all_listas = Listacompra.query.all()
    result = listas_schema.dump(all_listas)
    return jsonify(result.data)


# endpoint para deletar a lista de compra
@app.route("/listacompras/<id>", methods=["DELETE"])
def produto_delete(id):
    lista = Listacompra.query.get(id)
    db.session.delete(lista)
    db.session.commit()

    return lista_schema.jsonify(lista)


# endpoint para mostrar todos os clientes
@app.route("/cliente", methods=["GET"])
def get_user():
    all_users = Cliente.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result.data)


# endpoint para buscar cliente pelo id
@app.route("/cliente/<id>", methods=["GET"])
def user_detail(id):
    user = Cliente.query.get(id)
    return user_schema.jsonify(user)


# endpoint para atualizar cliente
@app.route("/cliente/<id>", methods=["PUT"])
def cliente_update(id):
    cliente = Cliente.query.get(id).first()
    nome = request.json['nome']

    cliente.nome = nome

    db.session.commit()
    return user_schema.jsonify(cliente)


# endpoint para deletar cliente
@app.route("/cliente/<id>", methods=["DELETE"])
def user_delete(id):
    user = Cliente.query.get(id)
    db.session.delete(user)
    db.session.commit()

    return user_schema.jsonify(user)


# endpoint para mostrar todos os produtos por carrinho de vendas
@app.route("/produto/carrinho/<id_carrinho>", methods=["GET"])
def get_produto_by_carrinho(id_carrinho):
    all_produtos = Produto.query.filter_by(listacompra_id=id_carrinho).all()
    result = produtos_schema.dump(all_produtos)
    return jsonify(result.data)


# endpoint para buscar lista de compras pelo id
@app.route("/listacompras/<id>", methods=["GET"])
def lista_detail(id):
    lista = Listacompra.query.get(id)
    return lista_schema.jsonify(lista)

# endpoint para buscar produto pelo id
@app.route("/produto/<id>", methods=["GET"])
def produto_detail(id):
    produto = Produto.query.get(id)
    return produto_schema.jsonify(produto)


if __name__ == '__main__':
    app.run(debug=True)