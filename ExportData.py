"""
Export data from a set of tables in a format suitable for importing to any
Oracle database on any platform.
"""

import cx_ExportData
import cx_LoggingOptions
import cx_OptionParser
import cx_OracleUtils
import sys

import Options

# parse command line
parser = cx_OptionParser.OptionParser()
parser.AddOption(cx_OracleUtils.SchemaOption())
parser.AddOption(Options.ARRAY_SIZE)
parser.AddOption(Options.REPORT_POINT)
parser.AddOption(Options.MAX_LONG_SIZE)
parser.AddOption(Options.SET_ROLE)
parser.AddOption("--include-schema-name", action = "store_true",
        help = "include schema name in the exported table list")
parser.AddOption("--include-tables", action = "append", metavar = "LIST",
        help = "name of tables to include in the export")
parser.AddOption("--exclude-tables", action = "append", metavar = "LIST",
        help = "name of tables to exclude from the export")
parser.AddOption("--skip", metavar = "N", type = "int",
        help = "number of rows to skip before starting the export; note that "
               "this option is only really useful when exporting only one "
               "table")
parser.AddOption("--row-limit", metavar = "N", type = "int",
        help = "number of rows at which the export will stop; note that this "
               "option is only really useful when exporting only one table")
cx_LoggingOptions.AddOptions(parser)
parser.AddArgument("fileName", required = True,
        help = "the name of the file in which to place the exported data or "
               "'-' to output the exported data to stdout")
options = parser.Parse()
cx_LoggingOptions.ProcessOptions(options)

# connect to the database
connection = cx_OracleUtils.Connect(options.schema, options.setRole)
cursor = connection.cursor()
if options.arraySize:
    cursor.arraysize = options.arraySize
if options.maxLongSize:
    cursor.setoutputsize(options.maxLongSize)

# open the file for the export
if options.fileName == "-":
  outFile = sys.stdout
else:
  outFile = file(options.fileName, "wb")

# retrieve the set of tables that will make up the export
tables = []
exporter = cx_ExportData.Exporter(outFile, cursor, options.reportPoint)
if options.includeTables:
    tables = [s.upper() for v in options.includeTables for s in v.split(",")]
else:
    excludeTables = []
    if options.excludeTables:
        excludeTables = [s.upper() for v in options.excludeTables
                for s in v.split(",")]
    tables = [n for n in exporter.TablesInSchema() if n not in excludeTables]
if options.includeSchemaName:
    tables = ["%s.%s" % (connection.username, n) for n in tables]

# perform the export
for table in tables:
    exporter.ExportTable(table, options.skip, options.rowLimit)
exporter.FinalizeExport()

