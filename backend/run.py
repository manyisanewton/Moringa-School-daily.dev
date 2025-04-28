from app import create_app
from app.auth_routes import auth_bp

app = create_app()
app.register_blueprint(auth_bp, url_prefix='/auth')

if __name__ == "__main__":
    app.run(debug=True)