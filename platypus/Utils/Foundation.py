from sentence_transformers      import SentenceTransformer
from urllib.parse               import quote
from transformers               import pipeline, AutoModelForCausalLM, AutoTokenizer
from langchain_text_splitters   import RecursiveCharacterTextSplitter

import xml.etree.ElementTree    as ET
import numpy                    as np
import streamlit                as st

import pymupdf
import os
import requests
import time
import faiss
import huggingface_hub
import json
import pymongo
import fitz
import bson.raw_bson

PLATYPUS_SENTENCE_TRANSFORMER_DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
PLATYPUS_DEFAULT_LANGUAGE_MODEL             = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
PLATYPUS_INTERMEDIATE_DIRECTORY             = "platypus_int"
PLATYPUS_UTILS_DIRECTORY                    = "platypus_utils"

PLATYPUS_TEMP_EXTRACTED_FILE                = "ExtractedText.temp"
PLATYPUS_ARXIV_RECORD_FILE                  = "ArxivRecords.json"

PLATYPUS_FAISS_INDEX_FILE                   = "FAISSIndex.index"
PLATYPUS_METADATA_FILE                      = "IndexMetadata.npy"

"""
Environment Loader, Loads Required Credentials, Variables, Tokens and API Keys
"""
class EnvironmentLoader(object):

    def __init__(self):
        with open("Environment.json", "r") as EnvFile:
            EnvKeys = json.load(EnvFile)

        self.DBUsername = EnvKeys["DB_USERNAME"]
        self.DBName     = EnvKeys["DB_NAME"]
        self.DBCluster  = EnvKeys["DB_CLUSTER"]
        self.DBHost     = EnvKeys["DB_HOST"]
        self.DBPort     = int(EnvKeys["DB_PORT"])
        self.DBPassword = EnvKeys["DB_PASSWORD"]
        self.HFToken    = EnvKeys["HF_TOKEN"]

# Environment Object
Env = EnvironmentLoader()
# Login to Hugging Face to use Models with Constraint
huggingface_hub.login(token = Env.HFToken)

def ArxivEntriesIntoDict() -> list:

    Entries = []

    with open(os.path.join(PLATYPUS_INTERMEDIATE_DIRECTORY, PLATYPUS_ARXIV_RECORD_FILE)) as File:
        
        Entries = json.load(File)

    return Entries

"""
Searches Arxiv using the Query and Retreives _MaxResults number of Papers
TODO: Parallalize each Batch
"""
def SearchArxiv(_Query: str, _Debug: bool, _MaxResults = 1024, _BatchSize = 1024, **kwargs):
    
    BaseURL = "http://export.arxiv.org/api/query?"
    Start = 0
    Entries = []

    while Start < _MaxResults:

        MaxRetreivable = min(_BatchSize, _MaxResults - Start)
        QueryURL = f"search_query=all:{quote(_Query)}&start={Start}&max_results={MaxRetreivable}"

        Response = None

        # Send request to arxiv for papers
        try:

            Response = requests.get(BaseURL + QueryURL, timeout=10)
            Response.raise_for_status()

        except requests.exceptions.RequestException as e:

            print(f"[Platypus][DB]: HTTP Request failed: {e}")
            return []

        # Parse the metadata
        try:

            BatchEntries = []
            Root = ET.fromstring(Response.content)
            for entry in Root.findall("{http://www.w3.org/2005/Atom}entry"):

                Title = entry.find("{http://www.w3.org/2005/Atom}title").text.strip()
                Summary = entry.find("{http://www.w3.org/2005/Atom}summary").text.strip()
                Link = entry.find("{http://www.w3.org/2005/Atom}id").text.strip()
                ArxivID = Link.split("/")[-1]
                BatchEntries.append({
                    "Title"     : Title,
                    "Summary"   : Summary,
                    "URL"       : Link.replace("/abs/", "/pdf/"),
                    "PaperID"   : ArxivID
                })
            
            Entries.extend(BatchEntries)

        except ET.ParseError as e:

            print(f"[Platypus][DB]: Failed to parse XML: {e}")

        if _Debug:
            print(f"[Platypus][DB]: Retreived Batch {(int)((Start / _BatchSize)+ 1)}")
        
        Start += _BatchSize
        time.sleep(1.5)

    with open(os.path.join(PLATYPUS_INTERMEDIATE_DIRECTORY, PLATYPUS_ARXIV_RECORD_FILE), "w+") as File:
        json.dump(Entries, File)

    if _Debug:
        print(f"[Platypus][DB]: Successfully written ArxivEntries to {PLATYPUS_INTERMEDIATE_DIRECTORY}/{PLATYPUS_ARXIV_RECORD_FILE}")

def DownloadPDFArxiv(_URL:str, _Debug: bool, **kwargs):
    
    try:
        # Download Content (Stream Mode)
        Response = requests.get(_URL, stream = True)
        Response.raise_for_status()
        # 
        if not Response.content.startswith(b"%PDF"):
            raise ValueError("[Platypus][Arxiv]: Invalid PDF header")

    except Exception as e:
        print(f"[Platypus][Arxiv]: Skipping {_URL} due to download/header issue: {e}")
        return None

    if _Debug:
        print(f"[Platypus][Arxiv]: Downloaded {_URL}")

    try:
        # In-Memory PDF Processing using fitz
        PDF     = fitz.open(stream=Response.content, filetype="pdf")
        Text    = "\n".join([page.get_text() for page in PDF])
        PDF.close()

        if not Text.strip():
            raise ValueError("[Platypus][DB]: Empty text extracted from PDF")

    except Exception as e:
        print(f"[Platypus][DB]: Skipping {_URL} due to PDF parsing failure: {e}")
        return None