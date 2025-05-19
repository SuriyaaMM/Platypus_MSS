import platypus.Utils.Foundation as Foundation

class PDFExtractor(object):

    """
        PDFExtractor(object)

        Constructs an PDF Extractor Object

        Attributes:
        self.FilePath =: Stores the File path
        self.Document =: Stores pymupdf Object
        self
    """
    def __init__(self, 
                 _FilePath: str, 
                 _Debug: bool):
        
        # Sanity checks
        if _FilePath is None:
            print("[Platypus][PDFExtractor]: PARAMETER(_FilePath) is empty!")

        if _FilePath[-4:-1] != ".pdf":
            print(f"[Platypus][PDFExtractor]: Supported File Types are only PDF!")

        self.FilePath   = _FilePath
        self.Document   = Foundation.pymupdf.open(self.FilePath)
        self.Debug      = _Debug

        # Debug info
        if self.Debug:
            print(f"[Platypus][PDFExtractor]: File To Check: {self.FilePath}")

        # Create intermediate directory
        Foundation.os.makedirs(Foundation.PLATYPUS_INTERMEDIATE_DIRECTORY, exist_ok = True)
        
        IntDirPath = Foundation.os.path.join(Foundation.PLATYPUS_INTERMEDIATE_DIRECTORY, Foundation.PLATYPUS_TEMP_EXTRACTED_FILE)

        # Write to intermediate file
        with open(IntDirPath, "wb") as File:

            for page in self.Document:
                
                File.write(page.get_text().encode("utf8"))
                File.write(bytes((12,)))

        # Read written data from intermediate file
        with open(Foundation.os.path.join(self.IntDirName, self.ExtractedTextIntFileName), "r") \
            as File:

            self.ExtractedText = File.readlines()

        # Remove the temp file
        Foundation.os.remove(IntDirPath)

        # ----- Extract abstract -----
        AbstractBeginIndex  = None
        AbstractEndIndex    = None

        for i in range(len(self.ExtractedText)):
            
            if AbstractBeginIndex is None and "Abstract" in self.ExtractedText[i].strip():
                AbstractBeginIndex = i + 1
            if AbstractEndIndex is None and "Introduction" in self.ExtractedText[i].strip():
                AbstractEndIndex = i - 1
            
        self.Abstract = self.ExtractedText[AbstractBeginIndex:AbstractEndIndex]    
        self.Abstract = "".join([line.strip() for line in self.Abstract if line.strip() != ""])

        if self.Debug:
            print("[Platypus][PDFExtractor]: Text & Abstract Extraction Successfull")
