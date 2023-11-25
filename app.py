from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # Import CORS from flask_cors

import os
import openai
import requests
from bs4 import BeautifulSoup
import re
import fitz  # PyMuPDF
from flask_mysqldb import MySQL

app = Flask(__name__)
CORS(app)
# Set your OpenAI API key
openai.api_key = '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'


# Function to generate an article using OpenAI GPT-3
def generate_article(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=800  # Adjust the number of tokens as needed
    )
    return response.choices[0].text.strip()


def page_not_found(e):
  return render_template('404.html'), 404


app = Flask(__name__)
app.secret_key = 'xyzsdfg'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'test'

mysql = MySQL(app)


def generate_article(query):
    base_url = "https://cac.instante.justice.md/ro/pending-dossiers?dossier_type=Any&apply_filter=1"
    prompt = f"Scrieți toate răspunsurile în limba română și elaborați un mic articol despre problemele legale legate de {query}. Au fost găsite următoarele cazuri in Republica Moldova:\n{query}Furnizați explicații detaliate pentru fiecare caz, inclusiv o descriere a situației. Imaginați-vă că scrieți un articol de știri și oferiți informații complete și bine argumentate despre fiecare caz pentru cititorii noștri. {query}. Au fost gДѓsite urmДѓtoarele cazuri in Republica Moldova:"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=800  # Adjust the number of tokens as needed
    )
    return response.choices[0].text.strip()


@app.route('/', methods=["GET", "POST"])
@app.route('/gov1', methods=["GET", "POST"])
def gov1():
    try:
        if request.method == 'POST':
            query = request.form['gov1']
            print("Query:", query)

            # Call the function to generate an article using GPT-3
            prompt = f"Scrieți toate răspunsurile în limba română și elaborați un mic articol despre problemele legale legate de {query}. Au fost găsite următoarele cazuri in Republica Moldova:\n{query}Furnizați explicații detaliate pentru fiecare caz, inclusiv o descriere a situației. Imaginați-vă că scrieți un articol de știri și oferiți informații complete și bine argumentate despre fiecare caz pentru cititorii noștri. {query}. Au fost gДѓsite urmДѓtoarele cazuri in Republica Moldova."

            openAIAnswer = generate_article(prompt)

            print("Debug: prompt =", prompt)
            print("Debug: openAIAnswer =", openAIAnswer)

            return render_template('gov1.html', **locals())

    except KeyError:
        return render_template('gov1.html', prompt="", openAIAnswer="")

    return render_template('gov1.html', prompt="", openAIAnswer="")


@app.route('/gov2', methods=["GET", "POST"])
def gov2():
    return render_template('gov2.html', **locals())


@app.route('/gov2_1', methods=["GET", "POST"])
def gov2_1():
    try:
        if request.method == 'POST':
            query = request.form['gov1']
            print("Query:", query)

            # Call the function to generate an article using GPT-3
            prompt = f"Scrieți toate răspunsurile în limba română și elaborați un mic articol despre problemele legale legate de {query}. Au fost găsite următoarele cazuri in Republica Moldova:\n{query}Furnizați explicații detaliate pentru fiecare caz, inclusiv o descriere a situației. Imaginați-vă că scrieți un articol de știri și oferiți informații complete și bine argumentate despre fiecare caz pentru cititorii noștri. {query}. Au fost gДѓsite urmДѓtoarele cazuri in Republica Moldova:"

            openAIAnswer = generate_article(prompt)

            print("Debug: prompt =", prompt)
            print("Debug: openAIAnswer =", openAIAnswer)

            return render_template('gov2_1.html', **locals())

    except KeyError:
        return render_template('gov2_1.html', prompt="", openAIAnswer="")

    return render_template('gov2_1.html', prompt="", openAIAnswer="")


@app.route('/gov2_2', methods=["GET", "POST"])
def gov2_2():
    return render_template('gov2_2.html', **locals())


@app.route('/gov2_3', methods=["GET", "POST"])
def gov2_3():
    return render_template('gov2_3.html', **locals())


@app.route('/gov3', methods=["GET", "POST"])
def gov3():
    return render_template('gov3.html', **locals())


@app.route('/gov3_1', methods=["GET", "POST"])
def gov3_1():
    try:
        if request.method == 'POST':
            query = request.form['gov1']
            print("Query:", query)

            # Call the function to generate an article using GPT-3
            prompt = f"Scrieți toate răspunsurile în limba română și elaborați un mic articol despre problemele legale legate de {query}. Au fost găsite următoarele cazuri in Republica Moldova:\n{query}Furnizați explicații detaliate pentru fiecare caz, inclusiv o descriere a situației. Imaginați-vă că scrieți un articol de știri și oferiți informații complete și bine argumentate despre fiecare caz pentru cititorii noștri. {query}. Au fost gДѓsite urmДѓtoarele cazuri in Republica Moldova:"

            openAIAnswer = generate_article(prompt)

            print("Debug: prompt =", prompt)
            print("Debug: openAIAnswer =", openAIAnswer)

            return render_template('gov3_1.html', **locals())

    except KeyError:
        return render_template('gov3_1.html', prompt="", openAIAnswer="")

    return render_template('gov3_1.html', prompt="", openAIAnswer="")

@app.route('/gov3_2', methods=["GET", "POST"])
def gov3_2():
    return render_template('gov3_2.html', **locals())


@app.route('/gov3_3', methods=["GET", "POST"])
def gov3_3():
    return render_template('gov3_3.html', **locals())



if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8888', debug=True)
