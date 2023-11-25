import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS from flask_cors

import os
import openai
import requests
from bs4 import BeautifulSoup
import re
import fitz  # PyMuPDF

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


# Function to send chunks of data to OpenAI API
def send_to_openai(data_chunks, dossier_name=None):
    full_text = ""
    for chunk in data_chunks:
        # Combine the chunk into a single string
        chunk_text = " ".join(str(item) for item in chunk if item is not None)
        full_text += chunk_text + "\n"

    # Generate an article using GPT-3
    prompt = f"Scrieți toate răspunsurile în limba română și elaborați un mic articol despre problemele legale legate de {dossier_name}. Au fost găsite următoarele cazuri:\n{full_text}Furnizați explicații detaliate pentru fiecare caz, inclusiv o descriere a situației. Imaginați-vă că scrieți un articol de știri și oferiți informații complete și bine argumentate despre fiecare caz pentru cititorii noștri."
    article = generate_article(prompt)

    return article


# Set the base URL
base_url = "https://cac.instante.justice.md/ro/pending-dossiers"


# API endpoint to get GPT-3 responses
@app.route('/get_gpt_response', methods=['GET'])
def get_gpt_response():
    dossier_name = request.args.get('dossier_name')

    # Set the initial parameters
    params = {
        'dossier_name': dossier_name,
        'dossier_type': 'Any',
        'apply_filter': '1'  # Start with the first page
    }

    # Create a list to store scraped data
    scraped_data = []

    # Set a maximum limit for the number of pages
    max_pages = 2
    page_counter = 0
    data_chunks = []

    while page_counter < max_pages:
        # Make a request with the current parameters
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all rows in the table
            rows = soup.find_all('tr')

            # Check if there are no rows, indicating no more pages
            if not rows:
                break

            # Iterate through each row
            for row in rows:
                # Find all cells in the row
                cells = row.find_all(['td', 'th'])

                # Extract data from each cell
                row_data = [cell.text.strip() for cell in cells]

                # Find and extract PDF link if available
                pdf_link = row.find('a', {'href': re.compile(r'\.pdf$', re.I)})
                pdf_url = pdf_link['href'] if pdf_link else None

                # Add PDF link to the row data
                row_data.append(pdf_url)

                # If a PDF link is present, download the PDF and extract text
                if pdf_url:
                    pdf_response = requests.get(pdf_url)
                    if pdf_response.status_code == 200:
                        with open('temp.pdf', 'wb') as pdf_file:
                            pdf_file.write(pdf_response.content)

                        # Extract text from the PDF
                        pdf_document = fitz.open('temp.pdf')
                        text = ""
                        for page_num in range(pdf_document.page_count):
                            page = pdf_document[page_num]
                            text += page.get_text()

                        row_data.append(text)

                        # Close and remove the temporary PDF file
                        pdf_document.close()
                        os.remove('temp.pdf')
                    else:
                        print(f"Failed to download PDF. Status code: {pdf_response.status_code}")

                # Append the row data to the list
                scraped_data.append(row_data)

            # Increment the page number for the next request
            params['apply_filter'] = str(int(params['apply_filter']) + 1)

            # Increment the page counter
            page_counter += 1

            # Check if the total characters exceed 4000 and send to OpenAI
            if len(str(scraped_data)) > 8000:
                response = send_to_openai(data_chunks)
                data_chunks = []

        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            break

    # Send any remaining data to OpenAI
    response = send_to_openai(data_chunks)

    return jsonify({"response": response})
@app.route('/get_predictions', methods=['GET'])
def get_predictions():
    # Your CSV data
    csv_data = """,,Year,Whole country,Chisinau,North,Balti,Briceni,Donduseni,Drochia,Edinet,Falesti,Floresti,Glodeni,Ocnita,Riscani,Singerei,Soroca,Centre,Anenii Noi,.Calaras,Criuleni,.Dubasar,Hincesti,Ialoveni,Nisporeni,Orhei,Rezina,Straseni,Soldanesti,Telenesti,Ungheni,South,Basarabeasca,..Cahu,Cantemir,Causeni,Cimislia,Leova,Stefan Voda,Taraclia,Gagauzia,,2000,215,25,37,5,-,2,2,3,1,7,2,3,3,4,5,76,4,10,5,1,6,5,5,14,1,13,1,7,4,38,-,10,8,5,5,4,4,2,10,,2001,189,16,29,5,1,1,2,3,6,2,3,-,1,3,2,78,8,6,5,2,3,12,4,17,2,7,3,5,4,29,2,6,4,1,2,10,3,1,5,,2002,204,28,50,10,1,1,6,6,5,2,2,3,4,3,7,79,2,5,6,3,11,10,5,18,1,9,3,3,3,36,1,8,7,5,2,4,5,4,4,,2003,320,40,66,9,1,3,9,6,4,3,5,4,3,12,7,91,8,9,4,2,9,8,4,21,4,5,5,6,6,52,1,19,3,8,4,5,5,7,19,,2004,336,55,80,14,3,7,7,7,5,6,1,2,5,11,12,124,14,11,11,1,13,16,7,16,5,7,2,5,16,58,4,13,6,11,7,5,12,-,15,,2005,280,46,68,12,4,2,2,7,4,7,3,3,6,9,9,99,9,18,9,3,6,3,4,11,1,9,3,9,14,52,2,11,10,10,6,3,8,2,13,,2006,268,46,69,6,-,10,9,5,4,8,2,5,7,7,6,87,7,8,4,4,5,6,3,13,4,15,-,11,7,58,1,18,9,13,6,-,9,2,8,,2007,281,40,67,17,2,5,3,6,4,13,2,3,3,4,5,96,9,5,4,2,10,14,6,10,3,17,-,7,9,69,5,10,13,14,7,5,10,5,10,,2008,306,53,68,11,1,-,6,3,5,7,5,2,10,6,12,101,13,10,6,2,11,8,2,11,4,14,3,6,11,65,6,14,11,13,9,5,5,2,14,,2009,264,26,85,13,1,4,6,6,5,5,7,6,12,8,12,93,5,10,8,1,7,10,8,13,4,9,-,6,12,52,1,10,11,11,8,6,3,2,5,,2010,368,45,81,12,6,2,8,7,3,4,8,5,8,3,15,130,7,6,17,10,10,18,4,10,2,25,4,8,10,92,8,12,19,20,9,2,14,8,14,,2011,291,44,64,13,4,3,3,2,5,4,2,2,7,7,12,102,6,5,15,4,19,6,11,10,5,7,-,6,9,75,2,17,15,16,6,4,12,3,5,,2012,360,56,91,4,3,3,10,4,7,8,9,3,15,16,9,138,11,7,20,2,15,9,6,11,10,12,8,14,13,63,3,7,8,15,11,6,10,3,8,,2013,349,44,92,22,8,4,12,1,9,5,10,2,4,5,10,127,11,16,12,2,11,8,12,13,4,10,4,9,15,70,3,13,17,14,12,4,6,1,9,,2014,338,40,77,13,6,1,3,7,8,4,3,6,3,8,15,130,11,13,14,8,16,14,10,10,6,4,3,11,10,74,4,15,15,22,8,2,6,2,16,,2015,301,49,77,7,5,5,6,2,12,4,6,4,9,11,6,112,6,13,5,5,16,9,11,11,4,6,2,12,12,48,6,11,11,4,6,2,6,2,15,,2016,329,53,61,7,9,3,8,3,3,6,3,3,4,5,7,107,8,7,10,3,13,12,11,10,7,6,9,5,6,87,3,28,10,7,11,7,15,6,16,,2017,287,47,71,7,6,6,6,5,2,7,5,3,3,13,8,108,8,9,15,3,10,9,6,23,5,5,4,7,4,51,-,12,14,9,-,8,5,3,8,,2018,266,35,61,6,2,7,4,4,7,7,4,1,4,3,12,84,7,6,9,1,10,11,10,5,5,5,4,7,4,75,6,10,11,23,4,6,8,7,11,,2019,331,54,72,9,5,4,7,7,8,5,2,8,5,5,7,122,9,10,7,4,14,11,19,11,5,7,5,9,11,78,7,7,20,17,9,7,9,2,5,,2020,254,26,65,6,5,7,4,C,6,5,6,9,6,6,C,92,9,7,10,5,12,7,10,7,C,8,C,8,5,59,C,18,12,6,4,6,9,C,10,,2021,227,24,47,-,4,4,7,5,5,C,4,C,4,6,C,76,5,4,6,C,17,10,4,7,4,C,4,7,4,71,6,23,8,11,C,10,9,C,7"""

    # Generate a prompt for OpenAI based on CSV data
    prompt = f"bsed on this csv prease return data prediciton for next years in a json format {csv_data}"

    # Generate predictions using OpenAI
    predictions = generate_article(prompt)

    return jsonify({"predictions": predictions})



if __name__ == '__main__':
    app.run(port=5000)
