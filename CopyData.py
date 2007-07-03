"""Copy data from the source to the destination, performing inserts and updates
as necessary to make the destination match the source. Note that deletes are
not performed, however."""

import cx_Logging
import cx_LoggingOptions
import cx_OptionParser
import cx_OracleUtils

import Options

# parse command line
parser = cx_OptionParser.OptionParser("CopyData")
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
if " " not in sourceSQL:
    if destinationTable is None:
        destinationTable = sourceSQL
    sourceInfo = cx_OracleUtils.GetObjectInfo(sourceConnection, sourceSQL)
    if sourceInfo is None:
        raise "Source table %s not found." % sourceSQL
    sourceTableOwner, sourceTableName, sourceTableType = sourceInfo
    sourceSQL = "select * from %s.%s" % \
            (cx_OracleUtils.IdentifierRepr(sourceTableOwner),
             cx_OracleUtils.IdentifierRepr(sourceTableName))
if not destinationTable:
    raise "A destination table must be specified when a source query " \
          "is used."

# verify the destination table exists
destInfo = cx_OracleUtils.GetObjectInfo(destConnection, destinationTable)
if destInfo is None:
    raise "Destination table %s not found." % destinationTable
destTableOwner, destTableName, destTableType = destInfo

# determine columns in source query
colPos = 0
sourceColumns = {}
definedVars = sourceCursor.execute(sourceSQL)
for colName, colType, colDisplaySize, colInternalSize, colPrecision, \
        colScale, colNullOk in sourceCursor.description:
    sourceColumns[colName] = (colPos, colType)
    colPos += 1

# lookup columns on destination table
cursor.execute("""
      select
        column_name,
        nullable
      from all_tab_columns
      where owner = :p_Owner
        and table_name = :p_Name""",
      p_Owner = destTableOwner,
      p_Name = destTableName)
destColumns = {}
for name, nullable in cursor.fetchall():
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
                where owner = :p_Owner
                  and table_name = :p_Name
                  and constraint_type in ('P', 'U')
                order by constraint_type""",
                p_Owner = destTableOwner,
                p_Name = destTableName)
        row = cursor.fetchone()
        if not row:
            raise "No primary or unique constraint found on table"
        constraintName, = row
        cursor.execute("""
                select column_name
                from all_cons_columns
                where owner = :p_Owner
                  and constraint_name = :p_Name""",
                p_Owner = destTableOwner,
                p_Name = constraintName)
        keyColumns = [n for n, in cursor.fetchall()]
    for name in keyColumns:
        if name not in sourceColumns:
            raise "Key column %s not in source query" % name

# match the columns; all of the source or all of the destination columns must
# match for a valid copy
bindVariables = {}
keyBindVariables = {}
bindVariableXref = []
destBindVariableXref = []
for name in sourceColumns:
    if name in destColumns:
        colPos, colType = sourceColumns[name]
        bindVarName = "p_Val_%d" % colPos
        isLob = str(definedVars[colPos]).startswith("<Lob")
        if options.checkExists or isLob:
            bindVariables[bindVarName] = colType
            bindVariableXref.append((colPos, bindVarName, isLob))
        else:
            bindVariables[bindVarName] = definedVars[colPos]
        destBindVariableXref.append((name, ":%s" % bindVarName))
        if options.checkExists and name in keyColumns:
            keyBindVariables[bindVarName] = bindVariables[bindVarName]
if len(bindVariables) not in (len(sourceColumns), len(destColumns)):
    raise "All source columns or all destination columns must match by name"

# set up insert cursor
insertNames = [cx_OracleUtils.IdentifierRepr(n) \
        for n, v in destBindVariableXref]
insertValues = [v for n, v in destBindVariableXref]
statement = "insert into %s.%s (%s) values (%s)" % \
        (cx_OracleUtils.IdentifierRepr(destTableOwner),
         cx_OracleUtils.IdentifierRepr(destTableName),
         ",".join(insertNames), ",".join(insertValues))
insertCursor = cursor
insertCursor.bindarraysize = sourceCursor.arraysize
insertCursor.prepare(statement)
vars = insertCursor.setinputsizes(**bindVariables)
insertVars = [(definedVars[p], vars[n], b) for p, n, b in bindVariableXref]

# set up exists cursor
if options.checkExists:
    whereClauses = [cx_OracleUtils.WhereClause(n, v, destColumns[n], 1) \
            for n, v in destBindVariableXref if n in keyColumns]
    statement = "select count(1) from %s.%s where %s" % \
            (cx_OracleUtils.IdentifierRepr(destTableOwner),
             cx_OracleUtils.IdentifierRepr(destTableName),
             " and ".join(whereClauses))
    existsCursor = destConnection.cursor()
    existsCursor.prepare(statement)
    vars = existsCursor.setinputsizes(**keyBindVariables)
    existsVars = [(definedVars[p], vars[n], b) \
            for p, n, b in bindVariableXref if n in vars]

# set up update cursor
updateCursor = None
if options.checkExists and len(keyColumns) != len(bindVariables):
    setClauses = [cx_OracleUtils.IdentifierRepr(n) + " = " + v \
            for n, v in destBindVariableXref if n not in keyColumns]
    statement = "update %s.%s set %s where %s" % \
            (cx_OracleUtils.IdentifierRepr(destTableOwner),
             cx_OracleUtils.IdentifierRepr(destTableName),
             ",".join(setClauses), " and ".join(whereClauses))
    if options.checkModified:
        additionalWhereClauses = \
                [cx_OracleUtils.WhereClause(n, v, destColumns[n], 0) \
                for n, v in destBindVariableXref if n not in keyColumns]
        statement += " and (%s)" % " or ".join(additionalWhereClauses)
    updateCursor = destConnection.cursor()
    updateCursor.bindarraysize = sourceCursor.arraysize
    updateCursor.prepare(statement)
    vars = updateCursor.setinputsizes(**bindVariables)
    updateVars = [(definedVars[p], vars[n], b) for p, n, b in bindVariableXref]

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
iter = range(sourceCursor.arraysize)
reportPoint = options.reportPoint
commitPoint = options.commitPoint
if reportPoint is None and commitPoint is not None:
    reportPoint = commitPoint

# perform the copy
while True:
    rowsFetched = sourceCursor.fetchraw()
    if not rowsFetched:
        break
    if not insertVars:
        insertPos = rowsFetched
    else:
        if rowsFetched != sourceCursor.arraysize:
            iter = range(rowsFetched)
        for pos in iter:
            exists = 0
            if options.checkExists:
                for definedVar, boundVar, isLob in existsVars:
                    boundVar.copy(definedVar, pos, 0)
                vars = existsCursor.execute(None)
                existsCursor.fetchraw()
                exists = vars[0].getvalue()
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
            for definedVar, boundVar, isLob in targetVars:
                if isLob:
                    boundVar.setvalue(targetPos,
                           definedVar.getvalue(pos).read())
                else:
                    boundVar.copy(definedVar, pos, targetPos)
    if insertPos:
        insertCursor.executemanyprepared(insertPos)
        insertedRows += insertPos
        insertPos = 0
    if updatePos:
        updateCursor.executemanyprepared(updatePos)
        modifiedRows += updateCursor.rowcount
        unmodifiedRows += (updatePos - updateCursor.rowcount)
        updatePos = 0
    if reportPoint and sourceCursor.rowcount - lastReported >= reportPoint:
        lastReported = sourceCursor.rowcount
        cx_Logging.Trace("  %s rows processed", sourceCursor.rowcount)
    if commitPoint and sourceCursor.rowcount - lastCommitted >= commitPoint:
        lastCommitted = sourceCursor.rowcount
        destConnection.commit()
destConnection.commit()

# print out final statistics
cx_Logging.Trace("%s rows retrieved from source.", sourceCursor.rowcount)
cx_Logging.Trace("%s rows created in destination.", insertedRows)
cx_Logging.Trace("%s rows modified in destination.", modifiedRows)
cx_Logging.Trace("%s rows unmodified in destination.", unmodifiedRows)

