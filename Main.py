from platypus.Core.Vectorizer   import ChunkVectorizer, Embedder
from platypus.Core.Database     import MongoDBManager
from platypus.Utils.Foundation  import SearchArxiv, ArxivEntriesIntoDict, faiss, np
from platypus.Core.Indexer      import FAISSIndexer

if __name__ == "__main__":

    _Debug = True

    EmbeddingEngine = Embedder()
    Vectorizer      = ChunkVectorizer(EmbeddingEngine, _Debug)
    DBManager       = MongoDBManager(_Debug)
    CursorArxiv     = DBManager.DB[DBManager.CollectionArxiv]
    Indexer         = FAISSIndexer(Vectorizer, _Debug)
    Documents       = CursorArxiv.find()

    # Indexer.BuildIndices(Documents)
    Indexer.LoadIndices()

    Query = "Attention is all You Need!"

    QueryVec = EmbeddingEngine.STModel.encode([Query])
    faiss.normalize_L2(QueryVec)

    D, I = Indexer.FAISSIndex.search(QueryVec, k = 5)

    for rank, index in enumerate(I[0]):
        print(f"\nResult {rank + 1}")
        print(f"FAISS Index: {index}") 
        print(f"Distance: {D[0][rank]}")
        print(f"Title: {Indexer.Metadata[index]['Title']}")
        print(f"URL: {Indexer.Metadata[index]['URL']}")