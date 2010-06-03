"""
Export data from a table in an Oracle database to an XML file.
"""

import cx_Logging
import cx_LoggingOptions
import cx_OptionParser
import cx_Oracle
import cx_OracleUtils
import cx_XML
import datetime
import sys

import Options

# parse command line
parser = cx_OptionParser.OptionParser()
parser.AddOption(cx_OracleUtils.SchemaOption())
parser.AddOption(Options.ARRAY_SIZE)
parser.AddOption(Options.REPORT_POINT)
parser.AddOption(Options.SET_ROLE)
parser.AddOption(Options.DATE_FORMAT)
parser.AddOption("--sort-by", metavar = "STR",
        help = "append an order by clause with this value to the query")
cx_LoggingOptions.AddOptions(parser)
parser.AddArgument("fileName", required = True,
        help = "the name of the file to which to write the data or "
               "'-' to write the data to stdout")
parser.AddArgument("source", required = True,
        help = "the name of the table from which to export all of the data " \
               "or the select statement which should be executed to " \
               "determine the data to export")
options = parser.Parse()
cx_LoggingOptions.ProcessOptions(options)

# connect to the database and execute the query
connection = cx_OracleUtils.Connect(options.schema, options.setRole)
cursor = connection.cursor()
if options.arraySize is not None:
    cursor.arraysize = options.arraySize
if options.source.lower().startswith("select "):
    query = options.source
else:
    query = "select * from %s" % options.source
if options.sortBy:
    query += " order by %s" % options.sortBy
cursor.execute(query)
names = [item[0] for item in cursor.description]

# write the data to the XML file
if options.fileName == "-":
    outputFile = sys.stdout
else:
    outputFile = file(options.fileName, "w")
writer = cx_XML.Writer(outputFile, numSpaces = 4)
writer.StartTag("ROWSET")
for row in cursor:
    writer.StartTag("ROW")
    for name, value in zip(names, row):
        if value is None:
            continue
        if isinstance(value, cx_Oracle.DATETIME):
            dateValue = datetime.datetime(value.year, value.month, value.day,
                    value.hour, value.minute, value.second)
            value = dateValue.strftime(options.dateFormat)
        else:
            value = str(value)
        writer.WriteTagWithValue(name, value)
    writer.EndTag()
    if options.reportPoint is not None \
            and cursor.rowcount % options.reportPoint == 0:
        cx_Logging.Trace("%s rows exported.", cursor.rowcount)
writer.EndTag()

if options.reportPoint is None or cursor.rowcount % options.reportPoint != 0:
    cx_Logging.Trace("%s rows exported.", cursor.rowcount)
cx_Logging.Trace("Done.")

