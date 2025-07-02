from flask import Flask, request, jsonify, send_file
import os
import json
import math
from collections import Counter

app = Flask(__name__)
DATA_FILE = "dataset.json"

# Carrega o dataset ou inicia vazio
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        dataset = json.load(f)
else:
    dataset = []

def cosine_similarity_manual(a, b):
    a_words = a.lower().split()
    b_words = b.lower().split()
    a_count = Counter(a_words)
    b_count = Counter(b_words)
    all_words = set(a_count.keys()) | set(b_count.keys())
    dot_product = sum(a_count[w] * b_count[w] for w in all_words)
    a_norm = math.sqrt(sum(a_count[w]**2 for w in all_words))
    b_norm = math.sqrt(sum(b_count[w]**2 for w in all_words))
    if a_norm == 0 or b_norm == 0:
        return 0.0
    return dot_product / (a_norm * b_norm)

def responder(pergunta):
    if not dataset:
        return "Ainda não aprendi nada."
    melhor_score = 0
    melhor_resposta = "Não entendi. Pode ensinar?"
    for item in dataset:
        score = cosine_similarity_manual(pergunta, item["pergunta"])
        if score > melhor_score:
            melhor_score = score
            melhor_resposta = item["resposta"]
    if melhor_score < 0.3:
        return "Não entendi. Pode ensinar?"
    return melhor_resposta

@app.route("/")
def index():
    return send_file("index.html")

@app.route("/ensinar", methods=["POST"])
def ensinar():
    dados = request.json
    pergunta = dados.get("pergunta", "").strip()
    resposta = dados.get("resposta", "").strip()

    if pergunta and resposta:
        dataset.append({"pergunta": pergunta, "resposta": resposta})
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        return jsonify({"status": "ok", "mensagem": "Aprendido com sucesso!"})
    return jsonify({"status": "erro", "mensagem": "Campos vazios."}), 400

@app.route("/perguntar", methods=["POST"])
def perguntar():
    dados = request.json
    pergunta = dados.get("pergunta", "").strip()

    if pergunta:
        resposta = responder(pergunta)
        return jsonify({"resposta": resposta})
    return jsonify({"resposta": "Pergunta inválida."}), 400

if __name__ == "__main__":
    app.run(debug=True)
