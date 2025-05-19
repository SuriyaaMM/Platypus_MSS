from platypus.Core.Database.Database import DatabaseManager
from platypus.Utils.Foundation import ArxivEntriesIntoDict, SearchArxiv
from platypus.Scripts.BulkDownload import DownloadPDF

# SearchArxiv("Machine Learning", True, 2 * 1024)

Entries = ArxivEntriesIntoDict()

Documents = [{
            "_id"       : _PaperInfo["PaperID"],
            "Title"     : _PaperInfo["Title"],
            "Summary"   : _PaperInfo["Summary"],
            "URL"       : _PaperInfo["URL"]

        }for _PaperInfo in Entries]

DBManager = DatabaseManager(True)

DBManager.InsertRecords(Documents, DBManager.CollectionArxiv)

DownloadPDF(DBManager, Documents[0:25], True)