class TableDefinition:

    def __init__(self, name, databasename):
        self.name = name
        self.columns = list[str]()
        self.databaseName = databasename


class QueryRequest:
    def __init__(self, result, columnName, blacklistedWord, table, db):
        self.result = result
        self.columnName = columnName
        self.blacklistedWord = blacklistedWord
        self.table = table
        self.db = db

