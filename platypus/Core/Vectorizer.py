import platypus.Utils.Foundation as Foundation

"""
Initializes Sentence Transformer

Default Sentence Transformer is set by PLATYPUS_DEFAULT_SENTENCE_TRANSFORMER_MODEL
"""
class Embedder(object):

    def __init__(self, 
                 _ModelName: str = Foundation.PLATYPUS_SENTENCE_TRANSFORMER_DEFAULT_MODEL):

        self.STModelName    = _ModelName
        self.STModel        = Foundation.SentenceTransformer(self.STModelName)

"""
Given a Text Chunk, Vectorizes using the Embedder
"""
class ChunkVectorizer(object):

    def __init__(self, 
                 _Embedder: Embedder,
                 _Debug: bool,
                 _Size: int = 128,
                 _Overlap: int= 4, **kwargs):
        
        # Sanity Checks
        
        if not isinstance(_Embedder, Embedder):
            print("PARAM(_Embedder) must of of type platypus.Core.Vectorizer.Embedder!")

        # Attributes Initialization
        self.ChunkEmbedder      = _Embedder
        self.ChunkSize          = _Size
        self.ChunkOverlap       = _Overlap
    
    """
        Vectorizes a Given list of Text

        Params:
            _ExtractedText (list) =: Valid list containing str
    """
    def Vectorize(self, _ExtractedText: list, **kwargs):

        # Sanity checks
        if len(_ExtractedText) == 0:
            print("[Platypus][VectorizeChunk]: PARAM(_ExtractedText) cannot be empty!")

        # Use langchain's RecursiveCharacterTextSplitter
        TextSplitter = Foundation.RecursiveCharacterTextSplitter(
            chunk_size          = self.ChunkSize,
            chunk_overlap       = self.ChunkOverlap,
            length_function     = len,
            add_start_index     = False)

        Chunks = TextSplitter.split_text(_ExtractedText)
        
        # return the encoded chunks as np.array
        return Foundation.np.array(self.ChunkEmbedder.STModel.encode(Chunks))