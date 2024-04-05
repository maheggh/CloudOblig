from flask import Flask
from views import views

app = Flask(__name__)
app.register_blueprint(views, url_prefix="/views")

    
if __name__ == '__main__':
    app.run(debug=True, port=8000)


#flask install 
# python -m pip install flask
#intsal strange words
#pip install jinja2



##didnt need this:
#install pyppeteer
#pip install pyppeteer
