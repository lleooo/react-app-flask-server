from app import create_app


app = create_app()

# client = MongoClient('')

if __name__ == "__main__":
    app.debug = True
    app.run()
