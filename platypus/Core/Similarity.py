import platypus.Utils.Foundation as Foundation

from platypus.Core.Vectorizer   import ChunkVectorizer
from platypus.Core.Indexer      import FAISSIndexer

class AbstractBasedDetector(object):

    def __init__(self,
                 _VectorizedAbstract: Foundation.np.array,
                 _Index : FAISSIndexer,
                 _Debug: bool):
        
        self.Debug              = _Debug
        self.Index              = _Index
        self.VectorizerAbstract = _VectorizedAbstract
        self.SimilarDocuments   = self.__SearchSimilarDocuments()
        self.Report             = []

    def __SearchSimilarDocuments(self):

        distance, I = self.Index.FAISSIndex.search(self.VectorizerAbstract, k = 5)

        for rank, index in enumerate(I[0]):
            self.SimilarDocuments.append(self.Index.Metadata[index]["URL"])
