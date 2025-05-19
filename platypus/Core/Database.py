import platypus.Utils.Foundation as Foundation
from platypus.Core.Vectorizer import ChunkVectorizer

class MongoDBManager(object):

    """
        Initializes MongoDB Database Handle

        Attributes:
        self.Client =: pymongo.MongoClient
        self.DB     =: Handle to Valid Database
    """
    def __init__(self, 
                 _Debug: bool, **kwargs):
        
        self.Debug    = _Debug

        # Local DB URI
        uri = f"mongodb://{Foundation.Env.DBHost}:{Foundation.Env.DBPort}/?appName={Foundation.Env.DBName}"
        
        try:

            # Connect to MongoDB Client
            self.Client = Foundation.pymongo.MongoClient(uri)

            if self.Client is not None:

                # Connect to Database
                self.DB = self.Client[Foundation.Env.DBName]

                # Check Connection
                try:

                    self.Client.admin.command('ping')
                    print(f"[Platypus][MongoDB]: Successfully connected to MongoDB!, using DB ({self.DBName})")
                    
                except Exception as e:
                    print(f"[Platypus][MongoDB]: Connection failed: {e}")

        except Exception as e:
            print(f"[Platypus][MongoDB]: Client Creation Failed! {e}")
        
        # Named Collections in Database
        self.CollectionArxiv                = "Arxiv"
        self.CollectionArxivPDFVectorized   = "ArxivVectorized"

        # Create Collection if they don't exist
        if self.CollectionArxiv not in self.DB.list_collection_names():

            self.DB.create_collection(self.CollectionArxiv)
            self.DB.create_collection(self.CollectionArxivPDFVectorized)
            
            if self.Debug:
                print(f"[Platypus][MongoDB]: Created Collection ({self.CollectionArxiv}) in {Foundation.Env.DBName}")
                print(f"[Platypus][MongoDB]: Created Collection ({self.CollectionArxivPDFVectorized}) in {Foundation.Env.DBName}")
    
    """
        Inserts a Set of Records into Initialized DB

        Args:
            _Documents:list =: Must be a valid List containing documents
            _Collection:str =: Must be one of the attribute Collection<CollectionName> in Manager    
    """
    def InsertRecords(self, _Documents:list, _Collection:str):

        if len(_Documents) <= 0:
            print("[Platypus][MongoDB]: PARAM(_Documents) must be at least of length  1!")
        
        if self.DB is not None:

            if _Collection in self.DB.list_collection_names():

                Collection = self.DB[_Collection]

                # Try inserting the Documents
                try:
                    # Store the Operations in list
                    Operations = [Foundation.pymongo.UpdateOne(
                                            filter = {"_id"   : _Document["_id"]},
                                            update = {"$set"  : _Document},
                                            upsert = True)
                                            for _Document in _Documents]
                    # bulk_write them
                    result = Collection.bulk_write(Operations)
                    
                    if self.Debug:
                        print(f"[Platypus][MongoDB]: Inserted {result.upserted_count} into {Collection.name}")
                        print(f"[Platypus][MongoDB]: Modified {result.modified_count} in {Collection.name}")

                except Exception as e:
                    print(f"[Platypus][MongoDB]: bulk_write Failed, Reason: {e}")
            
            else:
                print(f"[Platypus][MongoDB]: There was no Collection {_Collection} in {self.DB.name}!")

        else:
            print(f"[Platypus][MongoDB]: There was no Database Initialized!")

"""
    Vectorized MongoDB Manager!
"""
class MongoDBV(object):

    def __init__(self, 
                 _Vectorizer: ChunkVectorizer,
                 _Debug: bool, 
                 **kwargs):
        
        self.Debug      = _Debug
        self.DBManager  = MongoDBManager(self.Debug)
        self.Vectorizer = _Vectorizer

    def InsertOne(self,
                  document: dict,
                  vectorize_keys: dict,
                  collection: str,
                  concatenation_type: str = "add",
                  bypass_document_validation: bool = False, **kwargs):
        
        # Sanity Checks
        if document is None or collection is None or vectorize_keys is None:
            raise ValueError("one of PARAM(document, collection, vectorize_keys) is None")
        if len(vectorize_keys) <= 0 or len(document) <= 0:
            raise ValueError("one of PARAM(vectorize_keys, document) had no keys (length 0)!")
        if not all(key in document.keys() for key in vectorize_keys.keys()):
            raise ValueError("one of the key in PARAM(vectorize_keys) was not found in PARAM(document)")

        # Get collection cursor
        _Collection = self.DBManager.DB[collection]

        if _Collection is None:
            raise ValueError("Given collection doesn't exist in the DB")
        
        _ConcatenatedString = None

        for key in document.keys():
            
            if key in [key for key in vectorize_keys.keys()]:

                _ConcatenatedString += str(document[key])

        _VectorizedString = self.Vectorizer.Vectorize([_ConcatenatedString])
        
                


        


        

    
