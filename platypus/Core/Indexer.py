from platypus.Core.Vectorizer import ChunkVectorizer, Embedder

import platypus.Utils.Foundation as Foundation

class FAISSIndexer(object):

    def __init__(self, 
                 _Vectorizer: ChunkVectorizer, 
                 _Debug: bool, **kwargs):
        
        # Embedder
        self.EmbeddingEngine    = _Vectorizer.ChunkEmbedder
        # Indexer
        self.FAISSIndex         = Foundation.faiss.IndexFlatL2(self.EmbeddingEngine.STModel.get_sentence_embedding_dimension())
        # ChunkVectorizer
        self.Vectorizer         = _Vectorizer
        # Required Keys in Document
        self.RequiredKeys       = ["_id", "URL", "Summary", "Title"]
        # List to store Metadata
        self.Metadata           = []
        # List to store Embeddings
        self.StackedEmbeddings  = []
        # Debug Flag
        self.Debug              = _Debug

        if _Debug:
            print("[Platypus][DB]: Initialized Indexer Instance")

    """
        Builds the FAISS index and collects metadata from a list of documents,
        then saves them to files.

        Args:
            _Documents: A list of document dictionaries.
                        Each dictionary is expected to have keys: "_id", "URL", "Summary", "Title".
    """
    def BuildIndices(self, _Documents):

        # ----- Process Documents -----
        for i, Document in enumerate(_Documents):

            # Document shouldn't be None
            if Document is None:
                print(f"[Platypus][SSIndexer]: Document at index({i}) is None!")
            # Document should be a dict
            if not isinstance(Document, dict):
                print(f"[Platypus][SSIndexer]: Document at index({i}) is not a dict!")
            # Document should have all the RequiredKeys
            if not all (key in Document.keys() for key in self.RequiredKeys):
                print(f"[Platypus][SSIndexer]: Document at index ({i}) doesn't have one or more of the {self.RequiredKeys} keys!")

            # Concetenate Title & Summary
            ConcatenatedText = Document["Title"] + Document["Summary"]
            # Convert Title & Summary into Vectorized Chunks
            VectorizedChunks = self.Vectorizer.Vectorize(ConcatenatedText)

            if VectorizedChunks is not None:

                # Average all the Chunks (IN THIS CASE it is just 2-3 vectors)
                VectorizedChunks = Foundation.np.mean(VectorizedChunks.VectorizedChunk, axis = 0)
                # Append the Embeddings to StackedEmbeddings
                self.StackedEmbeddings.append(VectorizedChunks)
                # Metadata is a dict if {"Title" & "URL"}
                self.Metadata.append({"Title": Document["Title"], "URL": Document["URL"]})
            
            else:
                print(f"[Platypus][SSIndexer]: No valid vectors generated for document at index({i}). Skipping.")
        
        if self.Debug:
            print("[Platypus][SSIndexer]: Embedded Documents!")

        # ----- Append these Embeddings to Indexer -----
        if not self.StackedEmbeddings:
            print(f"[Platypus][SSIndexer]: No Embeddings were Generated to add to Index!")

        # Vertically stack them
        self.StackedEmbeddings = Foundation.np.vstack(self.StackedEmbeddings)
        # Normalize the StackedEmbeddings
        Foundation.faiss.normalize_L2(self.StackedEmbeddings)
        # Add to Indexer
        self.FAISSIndex.add(self.StackedEmbeddings)
        
        if self.Debug:
            print(f"[Platypus][SSIndexer]: Index built with {self.FAISSIndex.ntotal}")

        # ------- Save Indices and Metadata to File -----
        try: 

            Foundation.os.makedirs(Foundation.PLATYPUS_UTILS_DIRECTORY, exist_ok=True)
            # Save Indices & Metadata
            Foundation.faiss.write_index(self.FAISSIndex, Foundation.os.path.join(Foundation.PLATYPUS_UTILS_DIRECTORY, Foundation.PLATYPUS_FAISS_INDEX_FILE))
            Foundation.np.save(Foundation.os.path.join(Foundation.PLATYPUS_UTILS_DIRECTORY, Foundation.PLATYPUS_METADATA_FILE), self.Metadata)
            
            print(f"[Platypus][SSIndexer]: Written Indices & Metadata to Directory {Foundation.PLATYPUS_UTILS_DIRECTORY}")
        
        except Exception as e:
            print(f"[Platypus][SSIndexer]: Writing Indices & Metadata Failed! ({e})")

    """
        Loads the FAISS index and metadata from files.

        Returns:
            True if loaded successfully, False otherwise.
    """
    def LoadIndices(self):

        IndexPath       = Foundation.os.path.join(Foundation.PLATYPUS_UTILS_DIRECTORY, Foundation.PLATYPUS_FAISS_INDEX_FILE)
        MetadataPath    = Foundation.os.path.join(Foundation.PLATYPUS_UTILS_DIRECTORY, Foundation.PLATYPUS_METADATA_FILE)

        # ----- Loading Indices -----
        if Foundation.os.path.exists(IndexPath) and Foundation.os.path.exists(MetadataPath):
            
            print(f"[Platypus][SSIndexer]: Loading FAISS index from {IndexPath} and metadata from {MetadataPath}...")
            
            try:
                self.FAISSIndex = Foundation.faiss.read_index(IndexPath)
                self.Metadata   = Foundation.np.load(MetadataPath, allow_pickle=True).tolist()
                
                if self.Debug:
                    print("[Platypus][SSIndexer]: Index and metadata loaded successfully.")
                    print(f"[Platypus][SSIndexer]: Loaded FAISS Index size: {self.FAISSIndex.ntotal}, Loaded Metadata size: {len(self.Metadata)}")
                
                return True

            except Exception as e:
                print(f"[Platypus][SSIndexer]: Error loading index or metadata: {e}")
                self.FAISSIndex = None
                self.Metadata = []
                return False
        else:
            print(f"[Platypus][SSIndexer]: Index or metadata file not found.")
            return False
