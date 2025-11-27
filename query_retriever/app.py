from flask import Flask, Response, stream_with_context, render_template, request
import generate_embeddings
import main


app = Flask(__name__)

embedding_manager = generate_embeddings.EmbeddingManager()

@app.route("/")
def home():
    return render_template("chatbot.html")

@app.route("/get", methods=["POST"])
def chat():
    getquery = request.json.get("message")
    data = main.respond_query(getquery, embedding_manager)
    
    def generate():
        for chunk in data:
            yield chunk
        
    return Response(stream_with_context(generate()), mimetype='text/plain')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='7899', debug=False)