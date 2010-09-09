"""
Copy data from the source to the destination, performing inserts and updates
as necessary to make the destination match the source. Note that deletes are
not performed, however.
"""

import cx_Logging
import cx_LoggingOptions
import cx_OptionParser
import cx_OracleUtils
import os

import Exceptions
import Options

# parse command line
parser = cx_OptionParser.OptionParser()
parser.AddOption(cx_OracleUtils.SchemaOption("source-schema"))
parser.AddOption(cx_OracleUtils.SchemaOption("dest-schema"))
parser.AddOption("--key-columns", metavar = "COLS",
        help = "comma separated list of columns to use for checking if the "
               "row exists")
parser.AddOption("--no-check-exists", default = 1, action = "store_false",
        dest = "checkExists",
        help = "do not check to see if the row exists in the target")
parser.AddOption("--no-check-modified", default = 1, action = "store_false",
        dest = "checkModified",
        help = "do not check to see if the row is identical to the row in the "
               "destination")
parser.AddOption("--skip", metavar = "N", type = "int",
        help = "number of rows to skip before starting the copy")
parser.AddOption("--row-limit", metavar = "N", type = "int",
        help = "number of rows at which the copy will stop")
parser.AddOption(Options.COMMIT_POINT)
parser.AddOption(Options.REPORT_POINT)
parser.AddOption(Options.ARRAY_SIZE)
parser.AddOption(Options.MAX_LONG_SIZE)
parser.AddOption("--source-role", metavar = "ROLE",
        help = "enable this <role> [identified by <password>] in the source "
               "database immediately after connecting by calling "
               "dbms_session.set_role")
parser.AddOption("--dest-role", metavar = "ROLE",
        help = "enable this <role> [identified by <password>] in the target "
               "database immediately after connecting by calling "
               "dbms_session.set_role")
cx_LoggingOptions.AddOptions(parser)
parser.AddArgument("source", required = True,
        help = "a select statement or the name of the table to query")
parser.AddArgument("destination",
        help = "the name of a table or view to perform the insert and update "
               "statements against")
options = parser.Parse()
cx_LoggingOptions.ProcessOptions(options)

# set up the source connection
sourceConnection = cx_OracleUtils.Connect(options.sourceSchema,
        options.sourceRole)
sourceCursor = sourceConnection.cursor()
if options.arraySize:
    sourceCursor.arraysize = options.arraySize
if options.maxLongSize:
    sourceCursor.setoutputsize(options.maxLongSize)

# set up the destination connection
destConnection = cx_OracleUtils.Connect(options.destSchema, options.destRole)
cursor = destConnection.cursor()

# determine query to execute
sourceSQL = options.source.strip()
destinationTable = options.destination
if not sourceSQL.lower().startswith("select ") and os.path.isfile(sourceSQL):
    sourceSQL = file(sourceSQL).read().strip()
elif " " not in sourceSQL:
    if destinationTable is None:
        destinationTable = sourceSQL
    sourceInfo = cx_OracleUtils.GetObjectInfo(sourceConnection, sourceSQL)
    if sourceInfo is None:
        raise Exceptions.SourceTableNotFound(tableName = sourceSQL)
    sourceTableOwner, sourceTableName, sourceTableType = sourceInfo
    sourceSQL = "select * from %s.%s" % \
            (cx_OracleUtils.IdentifierRepr(sourceTableOwner),
             cx_OracleUtils.IdentifierRepr(sourceTableName))
if not destinationTable:
    raise Exceptions.DestinationTableNotSpecified()

# verify the destination table exists
destInfo = cx_OracleUtils.GetObjectInfo(destConnection, destinationTable)
if destInfo is None:
    raise Exceptions.TargetTableNotFound(tableName = destinationTable)
destTableOwner, destTableName, destTableType = destInfo

# determine columns in source query
colPos = 0
sourceColumns = {}
sourceCursor.execute(sourceSQL)
sourceVars = sourceCursor.fetchvars
for colName, colType, colDisplaySize, colInternalSize, colPrecision, \
        colScale, colNullOk in sourceCursor.description:
    isLob = colType in (sourceConnection.CLOB, sourceConnection.BLOB)
    sourceColumns[colName] = (colPos, colType, isLob)
    colPos += 1

# lookup columns on destination table
cursor.execute("""
      select
        column_name,
        nullable
      from all_tab_columns
      where owner = :owner
        and table_name = :name""",
      owner = destTableOwner,
      name = destTableName)
destColumns = {}
for name, nullable in cursor:
    destColumns[name] = (nullable == "Y")

# determine the list of key columns to use, if necessary
keyColumns = []
if options.checkExists:
    if options.keyColumns:
        keyColumns = options.keyColumns.upper().split(",")
    else:
        cursor.execute("""
                select constraint_name
                from all_constraints
                where owner = :owner
                  and table_name = :name
                  and constraint_type in ('P', 'U')
                order by constraint_type""",
                owner = destTableOwner,
                name = destTableName)
        row = cursor.fetchone()
        if not row:
            raise Exceptions.NoPrimaryOrUniqueConstraintOnTable()
        constraintName, = row
        cursor.execute("""
                select column_name
                from all_cons_columns
                where owner = :owner
                  and constraint_name = :name""",
                owner = destTableOwner,
                name = constraintName)
        keyColumns = [n for n, in cursor]
    for name in keyColumns:
        if name not in sourceColumns:
            raise Exceptions.KeyColumnNotInSourceQuery(name = name)

# match the columns; all of the source or all of the destination columns must
# match for a valid copy
matchingColumns = [n for n in sourceColumns if n in destColumns]
if len(matchingColumns) not in (len(sourceColumns), len(destColumns)):
    raise Exceptions.NotAllColumnsMatchByName()

# set up insert cursor
insertNames = [cx_OracleUtils.IdentifierRepr(n) for n in matchingColumns]
insertValues = [":%s" % (i + 1) for i, n in enumerate(matchingColumns)]
statement = "insert into %s.%s (%s) values (%s)" % \
        (cx_OracleUtils.IdentifierRepr(destTableOwner),
         cx_OracleUtils.IdentifierRepr(destTableName),
         ",".join(insertNames), ",".join(insertValues))
insertCursor = cursor
insertCursor.bindarraysize = sourceCursor.arraysize
insertCursor.prepare(statement)
vars = []
insertVars = []
for name in matchingColumns:
    colPos, colType, isLob = sourceColumns[name]
    sourceVar = sourceVars[colPos]
    if options.checkExists or isLob:
        targetVar = insertCursor.var(colType, sourceVar.maxlength)
        insertVars.append((sourceVar, targetVar, isLob))
    else:
        targetVar = sourceVar
    vars.append(targetVar)
insertCursor.setinputsizes(*vars)

# set up exists cursor
if options.checkExists:
    method = cx_OracleUtils.WhereClause
    whereClauses = [method(n, ":%s" % (i + 1), destColumns[n], True) \
            for i, n in enumerate(keyColumns)]
    statement = "select count(*) from %s.%s where %s" % \
            (cx_OracleUtils.IdentifierRepr(destTableOwner),
             cx_OracleUtils.IdentifierRepr(destTableName),
             " and ".join(whereClauses))
    existsCursor = destConnection.cursor()
    existsCursor.prepare(statement)
    vars = []
    existsVars = []
    for name in keyColumns:
        colPos, colType, isLob = sourceColumns[name]
        sourceVar = sourceVars[colPos]
        targetVar = existsCursor.var(colType, sourceVar.maxlength)
        vars.append(targetVar)
        existsVars.append((sourceVar, targetVar, isLob))
    existsCursor.setinputsizes(*vars)

# set up update cursor
updateCursor = None
if options.checkExists and len(keyColumns) != len(matchingColumns):
    updateColumns = [n for n in matchingColumns if n not in keyColumns] + \
            keyColumns
    setClauses = ["%s = :%s" % (cx_OracleUtils.IdentifierRepr(n), i + 1) \
            for i, n in enumerate(updateColumns) if n not in keyColumns]
    whereClauses = [method(n, ":%s" % (i + 1), destColumns[n], True) \
            for i, n in enumerate(updateColumns) if n in keyColumns]
    statement = "update %s.%s set %s where %s" % \
            (cx_OracleUtils.IdentifierRepr(destTableOwner),
             cx_OracleUtils.IdentifierRepr(destTableName),
             ",".join(setClauses), " and ".join(whereClauses))
    if options.checkModified:
        additionalWhereClauses = \
                [method(n, ":%s" % (i + 1), destColumns[n], False) \
                for i, n in enumerate(updateColumns) if n not in keyColumns]
        statement += " and (%s)" % " or ".join(additionalWhereClauses)
    updateCursor = destConnection.cursor()
    updateCursor.bindarraysize = sourceCursor.arraysize
    updateCursor.prepare(statement)
    vars = []
    updateVars = []
    for name in updateColumns:
        colPos, colType, isLob = sourceColumns[name]
        sourceVar = sourceVars[colPos]
        targetVar = updateCursor.var(colType, sourceVar.maxlength)
        updateVars.append((sourceVar, targetVar, isLob))
        vars.append(targetVar)
    updateCursor.setinputsizes(*vars)

# tell user what is happening
cx_Logging.Trace("Copying data...")
cx_Logging.Trace("  Source: %s", sourceSQL)
cx_Logging.Trace("  Destination: %s", destinationTable)

# skip rows that are not of interest
while options.skip:
    cx_Logging.Trace("  Rows left to skip: %s", options.skip)
    rowsToFetch = min(sourceCursor.arraysize, options.skip)
    options.skip -= sourceCursor.fetchraw(rowsToFetch)

# initialize counters used in performing the copy
insertedRows = 0
modifiedRows = 0
unmodifiedRows = 0
insertPos = 0
updatePos = 0
lastCommitted = 0
lastReported = 0
totalRowsFetched = 0
iter = range(sourceCursor.arraysize)
reportPoint = options.reportPoint
commitPoint = options.commitPoint
rowLimit = options.rowLimit
if reportPoint is None and commitPoint is not None:
    reportPoint = commitPoint

# perform the copy
while True:
    rowsFetched = sourceCursor.fetchraw()
    if rowLimit is not None and totalRowsFetched + rowsFetched > rowLimit:
        rowsFetched = rowLimit - totalRowsFetched
    if not rowsFetched:
        break
    totalRowsFetched += rowsFetched
    if not insertVars:
        insertPos = rowsFetched
    else:
        if rowsFetched != sourceCursor.arraysize:
            iter = range(rowsFetched)
        for pos in iter:
            exists = 0
            if options.checkExists:
                for sourceVar, targetVar, isLob in existsVars:
                    targetVar.copy(sourceVar, pos, 0)
                existsCursor.execute(None, [])
                exists, = existsCursor.fetchone()
            if not exists:
                targetPos = insertPos
                targetVars = insertVars
                insertPos += 1
            elif updateCursor:
                targetPos = updatePos
                targetVars = updateVars
                updatePos += 1
            else:
                unmodifiedRows += 1
                targetVars = []
            for sourceVar, targetVar, isLob in targetVars:
                if isLob:
                    lob = sourceVar.getvalue(pos)
                    targetVar.setvalue(targetPos,
                           lob and lob.read())
                else:
                    targetVar.copy(sourceVar, pos, targetPos)
    if insertPos:
        insertCursor.executemanyprepared(insertPos)
        insertedRows += insertPos
        insertPos = 0
    if updatePos:
        updateCursor.executemanyprepared(updatePos)
        modifiedRows += updateCursor.rowcount
        unmodifiedRows += (updatePos - updateCursor.rowcount)
        updatePos = 0
    if reportPoint and totalRowsFetched - lastReported >= reportPoint:
        lastReported = totalRowsFetched
        cx_Logging.Trace("  %s rows processed", totalRowsFetched)
    if commitPoint and totalRowsFetched - lastCommitted >= commitPoint:
        lastCommitted = totalRowsFetched
        destConnection.commit()
destConnection.commit()

# print out final statistics
cx_Logging.Trace("%s rows retrieved from source.", totalRowsFetched)
cx_Logging.Trace("%s rows created in destination.", insertedRows)
cx_Logging.Trace("%s rows modified in destination.", modifiedRows)
cx_Logging.Trace("%s rows unmodified in destination.", unmodifiedRows)

