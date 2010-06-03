"""
Import data from a file into a CLOB or BLOB column in a database table.
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
               "in which case an insert statement will be attempted and if "
               "that fails with a unique constraint violation, an update "
               "statement will be attempted")
parser.AddArgument("fileName", required = True,
        help = "the name of the file from which to read the data that "
               "is to be imported")
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
    mode = "rb"
    bindType = cx_Oracle.LONG_BINARY
else:
    mode = "r"
    bindType = cx_Oracle.LONG_STRING
data = file(options.fileName, mode).read()
if options.statementInFile:
    options.statement = file(options.statement).read().strip()
options.isColumn = " " not in options.statement
if not options.isColumn:
    statement = options.statement
    options.values["data"] = data
    cursor.setinputsizes(data = bindType)
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
    updateStatement = "update %s.%s set %s = :%s where %s" % \
            (owner, table, column, column, " and ".join(clauses))
    options.values[column] = data
    names = options.values.keys()
    values = [":%s" % n for n in names]
    statement = "insert into %s.%s (%s) values (%s)" % \
            (owner, table, ",".join(names), ",".join(values))
    initialBinds = {column : bindType}
    cursor.setinputsizes(**initialBinds)

# execute the statement
try:
    cursor.execute(statement, **options.values)
except cx_Oracle.DatabaseError, e:
    e, = e.args
    if e.code == 1 and options.isColumn:
        cursor.setinputsizes(**initialBinds)
        cursor.execute(updateStatement, **options.values)
    else:
        raise
connection.commit()

print >> sys.stderr, "Column succesfully imported."

