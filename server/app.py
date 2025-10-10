from flask import Flask, jsonify, request
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.recommendation_routes import recommendation_bp

app = Flask(__name__)
CORS(app)  # Allow requests from frontend (React)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(recommendation_bp, url_prefix="/api/recommendations")

@app.route("/")
def home():
    return jsonify({"message": "Backend running successfully!"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
