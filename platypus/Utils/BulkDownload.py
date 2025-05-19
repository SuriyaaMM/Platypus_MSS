from platypus.Utils.Foundation          import requests, os, PLATYPUS_INTERMEDIATE_PATH, ArxivEntriesIntoDict, time, np
from platypus.Core.Vectorizer           import ChunkVectorizer, Embedder
from platypus.Core.Database             import MongoDBManager
from pymongo import UpdateOne
import bson
import fitz
from tqdm import tqdm
from joblib import Parallel, delayed
from multiprocessing import cpu_count
from functools import partial

def ProcessDocument(_Document: dict, _Vectorizer: ChunkVectorizer, _Debug: bool):

    URL = _Document["URL"]
        
    try:
        Response = requests.get(URL, stream = True)
        Response.raise_for_status()

        if not Response.content.startswith(b"%PDF"):
            raise ValueError("[Platypus][DB]: Invalid PDF header")

    except Exception as e:
        print(f"[Platypus][DB]: Skipping {URL} due to download/header issue: {e}")
        return None

    # if _Debug:
        # print(f"[Platypus][DB]: Downloaded {URL}")

    try:
        pdf = fitz.open(stream=Response.content, filetype="pdf")
        text = "\n".join([page.get_text() for page in pdf])
        pdf.close()

        if not text.strip():
            raise ValueError("[Platypus][DB]: Empty text extracted from PDF")

    except Exception as e:
        print(f"[Platypus][DB]: Skipping {URL} due to PDF parsing failure: {e}")
        return None    

    VectorizedChunk = _Vectorizer.Vectorize(text)

    Document = {
        "_id"               : os.path.basename(URL),
        "WholeEmbedding"    : bson.Binary(VectorizedChunk.tobytes()),
        "dtype"             : str(VectorizedChunk.dtype),
        "shape"             : VectorizedChunk.shape
    }

    # print(f"[Platypus][DB]: Processed {URL}")
    # time.sleep(0.5)

    return UpdateOne(
                filter = {"_id" : _Document["_id"]},
                update = {"$set":  Document},
                upsert = True)


def DownloadPDF(DBManager: MongoDBManager, _Documents: list, _Debug: bool, _BatchSize: int = 8, **kwargs):
    Collection = DBManager.DB[DBManager.CollectionArxivPDFVectorized]

    total_batches = (len(_Documents) + _BatchSize - 1) // _BatchSize
    Batch = 0

    with tqdm(total=total_batches, desc="[Platypus][DB]: Downloading PDFs") as pbar:
        while Batch < len(_Documents):

            print(f"[Platypus][DB]: Starting joblib parallel with {cpu_count()} workers... (Batch = {Batch/_BatchSize + 1})")
            
            Results = Parallel(n_jobs=cpu_count(), backend="loky")(
                delayed(ProcessDocument)(_Document, _Debug) for _Document in _Documents[Batch:Batch + _BatchSize]
            )

            Operations = [op for op in Results if op is not None]

            if Operations:
                try:
                    result = Collection.bulk_write(Operations)
                    print(f"[Platypus][DB]: Inserted {result.upserted_count} into {Collection.name}")
                    print(f"[Platypus][DB]: Modified {result.modified_count} into {Collection.name}")
                except Exception as e:
                    print(f"[Platypus][DB]: bulk_write Failed: {e}")
            else:
                print("[Platypus][DB]: No valid operations generated.")

            Batch += _BatchSize
            pbar.update(1)

    DBManager.Client.close()