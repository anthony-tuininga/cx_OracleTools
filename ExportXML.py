"""Export data from a table in an Oracle database to an XML file."""

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
cx_LoggingOptions.AddOptions(parser)
parser.AddArgument("fileName", required = True,
        help = "the name of the file to which to write the data or "
               "'-' to write the data to stdout")
parser.AddArgument("tableName", required = True,
        help = "the name of the table from which to export the data")
options = parser.Parse()
cx_LoggingOptions.ProcessOptions(options)

# connect to the database
connection = cx_OracleUtils.Connect(options.schema, options.setRole)
cursor = connection.cursor()
if options.arraySize is not None:
    cursor.arraysize = options.arraySize
cursor.execute("select * from %s" % options.tableName)
names = [item[0] for item in cursor.description]

# write the data to the XML file
if options.fileName == "-":
    outputFile = sys.stdout
else:
    outputFile = file(options.fileName, "w")
writer = cx_XML.Writer(outputFile, numSpaces = 4)
writer.StartTag("ROWSET")
for row in cursor:
    writer.StartTag("ROW", num = cursor.rowcount)
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
        print >> sys.stderr, cursor.rowcount, "rows exported."
writer.EndTag()

if options.reportPoint is None or cursor.rowcount % options.reportPoint != 0:
    print >> sys.stderr, cursor.rowcount, "rows exported."
print >> sys.stderr, "Done."

