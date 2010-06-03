"""
Generate views based on tables in a database.
"""

import cx_LoggingOptions
import cx_OptionParser
import cx_Oracle
import cx_OracleObject
import cx_OracleUtils
import sys

import Exceptions

# parse command line
parser = cx_OptionParser.OptionParser()
parser.AddOption(cx_OracleUtils.SchemaOption())
parser.AddOption("--add-prefix", metavar = "STR",
        help = "add prefix to name of table to create view")
parser.AddOption("--remove-prefix", metavar = "STR",
        help = "remove prefix from name of table to create view")
parser.AddOption("--add-suffix", metavar = "STR",
        help = "add suffix to name of table to create view")
parser.AddOption("--remove-suffix", metavar = "STR",
        help = "remove suffix from name of table to create view")
parser.AddOption("--include-tables", action = "append", metavar = "LIST",
        help = "name of tables to include in the export")
parser.AddOption("--exclude-tables", action = "append", metavar = "LIST",
        help = "name of tables to exclude from the export")
cx_LoggingOptions.AddOptions(parser)
options = parser.Parse()
cx_LoggingOptions.ProcessOptions(options)

# connect to the database
connection = cx_OracleUtils.Connect(options.schema)
cursor = connection.cursor()

# determine the list of tables to generate the views for
tables = []
if options.includeTables:
    tables = [s.upper() for v in options.includeTables for s in v.split(",")]
else:
    excludeTables = []
    if options.excludeTables:
        excludeTables = [s.upper() for v in options.excludeTables
                for s in v.split(",")]
    cursor.execute("select table_name from user_tables order by table_name")
    tables = [n for n, in cursor if n not in excludeTables]

# prepare the cursor for retrieving the columns for the table
cursor.prepare("""
        select column_name
        from user_tab_columns
        where table_name = :p_TableName
        order by column_id""")
cursor.setinputsizes(p_TableName = cx_Oracle.STRING)

# output the view syntax for each table
for tableName in tables:
    print >> sys.stderr, "Generating view for table", tableName + "..."
    fromClause = "from %s;" % tableName.lower()
    cursor.execute(None, p_TableName = tableName)
    columnNames = ["  " + n.lower() for n, in cursor]
    if not columnNames:
        raise Exceptions.InvalidTableName()
    if options.removePrefix \
            and tableName.startswith(options.removePrefix.upper()):
        tableName = tableName[len(options.removePrefix):]
    if options.addPrefix:
        tableName = options.addPrefix + tableName
    if options.removeSuffix \
            and tableName.endswith(options.removeSuffix.upper()):
        tableName = tableName[:-len(options.removeSuffix)]
    if options.addSuffix:
        tableName += options.addSuffix
    print "create or replace view " + tableName.lower() + " as"
    print "select"
    print ",\n".join(columnNames)
    print fromClause
    print
print >> sys.stderr, "Done."

