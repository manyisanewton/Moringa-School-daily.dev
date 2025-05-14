from app import create_app

# Create the app and socketio instances
app, socketio = create_app()

if __name__ == "__main__":
    for rule in app.url_map.iter_rules():
        methods = ",".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
        print(f"{rule.endpoint:30s} {methods:20s} {rule.rule}")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)