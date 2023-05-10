from root import create_app
from dotenv import load_dotenv
load_dotenv('.env')
app = create_app("prod")
if __name__=="__main__":
    app.run(debug=False)