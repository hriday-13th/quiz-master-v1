from flask import Flask, request, jsonify, redirect_url

app = Flask(__name__)

@app.route('/')
def home():
    redirect_url("/login")

@app.route('/login'):
def login():
    return "we logging here"

# Example API route (GET + POST)
@app.route('/api/data', methods=['GET', 'POST'])
def data():
    if request.method == 'GET':
        return jsonify({"message": "You sent a GET request!"})
    if request.method == 'POST':
        data = request.get_json()
        return jsonify({"message": "You sent a POST request!", "data": data})

# Run the server
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)

