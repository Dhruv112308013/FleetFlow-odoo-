from app import create_app

app = create_app()

if __name__ == '__main__':
    # Ensure port and host are suitable for dev
    app.run(debug=True, port=5000)
