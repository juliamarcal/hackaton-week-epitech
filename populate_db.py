import os
import spacy
from database import Session

from database.preProcessedData import PreProcessedData

def list_files_recursive(folder_path):
    npl = spacy.load("fr_core_news_sm")
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if ".png" in file_name:
                continue
            for token in get_unique_tokens(file_name, npl):
                new_doc = PreProcessedData(token, os.path.join(root, file_name), os.path.join(root, file_name))
                print("%s ---> '%s' %s"%(token, new_doc.keyword, new_doc.filePath))
                session.add(new_doc)
            session.commit()

def get_unique_tokens(file_name, npl):

    doc = npl(file_name.replace(".docx", "").replace(".pdf", ""))

    unique_tokens = [token.text.lower() for token in doc if not token.pos_ in ["PART", "SYM", "PUNCT", "ADP", "CCONJ", "DET", "NUM"]]

    unique_tokens = list(dict.fromkeys(unique_tokens))

    return unique_tokens

# Example: Replace 'your_folder_path' with the actual path of the folder you want to traverse
folder_path = 'raw_data/'
session = Session()
list_files_recursive(folder_path)
session.commit()
