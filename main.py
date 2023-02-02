from Website import create_app

app = create_app()

if __name__ == '__main__':
    app.secret_key = "my_secret_key"
    app.run(debug=True)
