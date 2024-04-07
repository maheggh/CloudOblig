from flask import Blueprint, render_template

views = Blueprint(__name__, "views")

@views.route("/")
def home():
    return render_template("index.html", name="bitchasss")

#flask install 
# python -m pip install flask
#pip install markdown2 pdfkit
#pip install markdown2 weasyprint - no work
# pip install mdpdf - trenger ikke denne
#pip install markdown2pdf - funka ikke
#pip install md2pdf - newer funka fortsatt ikke
#intsal strange words
#pip install jinja2
#didnt need this:
#install pyppeteer
#pip install pyppeteer


# pip install xelatex
#pip install pypandoc
#pip install pdflatex
#pip install md2pdf
#pip install weasyprint
#pip install markdown2 fpdf
#pip install reportlab