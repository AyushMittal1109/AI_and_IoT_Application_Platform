from flask import Flask, request, render_template
import threading
from flask import flash
from pymongo import MongoClient
# import schedule
# import time
# import datetime
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("temp.html")

def renderUI():
    app.use_reloader=False
    # app.run(host='0.0.0.0',port=5010)
    app.run(port=5010)


renderUI()
