"""Dump the results of a SQL select statement to a file in CSV format."""

import cx_LoggingOptions
import cx_OptionParser
import cx_OracleUtils
import sys

# parse command line
parser = cx_OptionParser.OptionParser("DumpCSV")
parser.AddOption("--record-sep", default = "\n", metavar = "CHAR",
        help = "record separator to use")
parser.AddOption("--field-sep", default = ",", metavar = "CHAR",
        help = "field separator to use")
parser.AddOption("--string-encloser", default = '"', metavar = "CHAR",
        help = "character to use for enclosing strings")
parser.AddOption("--escape-char", default = "\\", metavar = "CHAR",
        help = "character to use for escaping the string encloser")
parser.AddOption("--report-point", type = "int", metavar = "N",
        help = "report point is <n> rows")
parser.AddOption("--sql-in-file", action = "store_true",
        help = "SQL parameter is actually a file name in which the SQL is "
               "found")
cx_LoggingOptions.AddOptions(parser)
parser.AddArgument("connectString", required = 1,
        help = "the string to use for connecting to the database")
parser.AddArgument("sql", required = 1,
        help = "the SQL to execute or the name of a file in which the SQL "
               "is found if the --sql-in-file option is used")
parser.AddArgument("fileName", required = 1,
        help = "the name of the file in which to place the output")
options = parser.Parse()
cx_LoggingOptions.ProcessOptions(options)

# connect to database
connection = cx_OracleUtils.Connect(options.connectString)
cursor = connection.cursor()
cursor.arraysize = 50

# open output file
outFile = file(options.fileName, "w")

# determine SQL and execute it
sql = options.sql
if options.sqlInFile:
    sql = file(sql).read()
cursor.execute(sql)

# define function to return an evaluated string (to support tabs, newlines)
def EvalString(value):
    return value.replace("\\t", "\t").replace("\\n", "\n")

# define function to return a string representation of each type
def StringRep(value):
    if value is None:
        return ""
    elif isinstance(value, str):
        if not gStringEncloser:
            return value
        return gStringEncloser + value.replace(gStringEncloser, \
                gEscapeCharacter + gStringEncloser) + gStringEncloser
    return str(value)

# dump the results to the output file
gFieldSeparator = EvalString(options.fieldSep)
gRecordSeparator = EvalString(options.recordSep)
gStringEncloser = EvalString(options.stringEncloser)
gEscapeCharacter = EvalString(options.escapeChar)
while True:

    # fetch a single row
    row = cursor.fetchone()
    if not row:
        break

    # dump the row
    outFile.write(gFieldSeparator.join([StringRep(v) for v in row]))
    outFile.write(gRecordSeparator)

    # report the number of rows dumped, if desired
    if options.reportPoint and cursor.rowcount % options.reportPoint == 0:
        print >> sys.stderr, " ", cursor.rowcount, "rows dumped."

# report the total number of rows dumped
if not options.reportPoint or cursor.rowcount == 0 or \
        cursor.rowcount % options.reportPoint != 0:
    print >> sys.stderr, " ", cursor.rowcount, "rows dumped."
print >> sys.stderr, "Done."

