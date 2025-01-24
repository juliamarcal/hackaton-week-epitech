import os
import PyPDF2
import requests
import docx
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/extract-answer-from-file', methods=['POST'])
def extract_answer_from_file():
    data = request.json
    filePath = data['filePath']
    question = data['question']

    raw_text = get_raw_text_from_file(filePath)
    return get_chat_gpt_answer(raw_text, question)

def get_raw_text_from_file(filePath):
    if not os.path.exists(filePath):
        raise FileNotFoundError(f"File '{filePath}' does not exist.")

    if filePath.endswith('.pdf'):
        with open(filePath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            raw_text = ''
            for page in reader.pages:
                raw_text += page.extract_text()

    elif filePath.endswith('.docx'):
        doc = docx.Document(filePath)
        raw_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])

    else:
        raise TypeError(f"File '{filePath}' has an unsupported extension.")

    return raw_text

def get_chat_gpt_answer(raw_text, question):
    message = {
        "message": f"{raw_text} {question}",
    }

    response = requests.post("http://localhost:1000/send-question-gpt", json=message)

    if response.status_code == 200:
        answer = response.json()["answer"]
        return answer
    else:
        # The request failed
        raise Exception(f"Request failed with status code {response.status_code}")

if __name__ == '__main__':
    app.run(debug=True, port=2000)