from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/process-keywords', methods=['POST'])
def process_keywords():
    data = request.json
    keywords = data['keywords']
    keywords = keywords.lower()
    keywordsArray = keywords.split(",")
    db_response = find_best_match(keywordsArray)

    return jsonify(db_response)

def find_best_match(keywordsArray):
    db_results = query_database()

    db_results_dict = {}
    for filePath, fileLink, keyWords in db_results:
        db_results_dict.setdefault(filePath, []).append(keyWords)
    
    best_path = None
    max_intersection = 0

    for filePath, keyWordsList in db_results_dict.items():
        intersection_size = len(set(keyWordsList).intersection(keywordsArray))

        if intersection_size > max_intersection:
            max_intersection = intersection_size
            best_path = filePath

    return best_path

def query_database():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    cursor.execute("SELECT filePath, fileLink, keyword FROM 'pre-processed data'")
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == '__main__':
    app.run(debug=True)