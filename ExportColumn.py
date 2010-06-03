"""
Export data from a CLOB or BLOB column in a database table to a file.
"""

import cx_LoggingOptions
import cx_OptionParser
import cx_OracleUtils
import cx_Oracle
import sys

import Exceptions
import Options

# parse command line
parser = cx_OptionParser.OptionParser()
parser.AddOption(cx_OracleUtils.SchemaOption())
parser.AddOption(Options.BINARY)
parser.AddOption(Options.STATEMENT_IN_FILE)
cx_LoggingOptions.AddOptions(parser)
parser.AddArgument("statement", required = True,
        help = "the statement to execute OR the name of the file containing "
               "the statement to execute if the --statement-in-file option "
               "is specified OR the name of the column in which to import "
               "the contents of the file in the form [Owner.]Table.Column "
               "in which case a select statement will be fabricated with the "
               "values argument making up the where clause")
parser.AddArgument("fileName", required = True,
        help = "the name of the file to write the data that is to be exported")
parser.AddArgument("values", keywords = True,
        help = "any number of values of the form name=value which will be "
               "turned into bind variables which will be bound to the "
               "statement that is to be executed")
options = parser.Parse()
cx_LoggingOptions.ProcessOptions(options)

# connect to the database
connection = cx_OracleUtils.Connect(options.schema)
cursor = connection.cursor()
 
# verify options
if options.binary:
    mode = "wb"
else:
    mode = "w"
if options.statementInFile:
    options.statement = file(options.statement).read().strip()
options.isColumn = " " not in options.statement
if not options.isColumn:
    statement = options.statement
else:
    parts = options.statement.upper().split(".")
    if len(parts) < 2 or len(parts) > 3:
        raise Exceptions.InvalidColumnName()
    if len(parts) == 2:
        owner = connection.username.upper()
        table, column = parts
    else:
        owner, table, column = parts
    clauses = ["%s = :%s" % (n, n) for n in options.values]
    whereClause = ""
    if clauses:
        whereClause = " where " + " and ".join(clauses)
    statement = "select %s from %s.%s%s" % (column, owner, table, whereClause)

# execute the statement and retrieve the data
lob, = cursor.executeandfetchone(statement, **options.values)
file(options.fileName, mode).write(lob.read())
print >> sys.stderr, "Column successfully exported."

