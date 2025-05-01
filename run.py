from app import create_app

app = create_app()

if _name_ == "_main_":
    app.run(host="0.0.0.0", port=5000)
