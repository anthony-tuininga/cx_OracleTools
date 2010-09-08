"""
Dump the results of a SQL select statement to a file in CSV format.
"""

import csv
import cx_Logging
import cx_LoggingOptions
import cx_OptionParser
import cx_OracleUtils
import sys

import Options

# parse command line
parser = cx_OptionParser.OptionParser()
parser.AddOption(cx_OracleUtils.SchemaOption())
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
parser.AddArgument("sql", required = True,
        help = "the SQL to execute or the name of a file in which the SQL "
               "is found if the --sql-in-file option is used")
parser.AddArgument("fileName",
        help = "the name of the file in which to place the output")
options = parser.Parse()
cx_LoggingOptions.ProcessOptions(options)

# connect to database
connection = cx_OracleUtils.Connect(options.schema)
cursor = connection.cursor()
cursor.arraysize = 50

# open output file
if options.fileName is None or options.fileName == "-":
    outFile = sys.stdout
else:
    outFile = file(options.fileName, "w")

# determine SQL and execute it
sql = options.sql
if options.sqlInFile:
    sql = file(sql).read()
cursor.execute(sql)

# define function to return an evaluated string (to support tabs, newlines)
def EvalString(value):
    return value.replace("\\t", "\t").replace("\\n", "\n")

# dump the results to the output file
fieldSeparator = EvalString(options.fieldSep)
recordSeparator = EvalString(options.recordSep)
stringEncloser = EvalString(options.stringEncloser)
escapeCharacter = EvalString(options.escapeChar)
writer = csv.writer(outFile, delimiter = fieldSeparator,
        quotechar = stringEncloser, escapechar = escapeCharacter,
        lineterminator = recordSeparator)
for row in cursor:
    writer.writerow(row)
    if options.reportPoint and cursor.rowcount % options.reportPoint == 0:
        cx_Logging.Trace("%s rows dumped.", cursor.rowcount)

# report the total number of rows dumped
if not options.reportPoint or cursor.rowcount == 0 or \
        cursor.rowcount % options.reportPoint != 0:
    cx_Logging.Trace("%s rows dumped.", cursor.rowcount)
cx_Logging.Trace("Done.")

