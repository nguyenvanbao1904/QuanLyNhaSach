from app.index import app

if __name__ == '__main__':
    from app import admin
    app.run(debug=True)
