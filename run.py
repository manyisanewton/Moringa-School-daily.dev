from backend.app import create_app
app = create_app()
if __name__ == "__main__":
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:30s} {','.join(rule.methods):20s} {rule.rule}")
    app.run(host="0.0.0.0", port=5000)