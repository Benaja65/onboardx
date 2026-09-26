import requests
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/produits', methods=['GET'])
def get_produits():
    """Retourne la liste des produits agricoles disponibles"""
    produits = [
        {"id": 1, "nom": "Maïs", "prix": 250},
        {"id": 2, "nom": "Mil", "prix": 180}
    ]
    return jsonify(produits)

@app.route('/api/commande', methods=['POST'])
def creer_commande():
    """Crée une nouvelle commande fournisseur"""
    return jsonify({"status": "commande créée"})

if __name__ == '__main__':
    app.run(debug=True)