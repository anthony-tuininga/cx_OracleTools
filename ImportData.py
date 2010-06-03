"""
Import data from an export file into tables in an Oracle database.
"""

import cx_ImportData
import cx_Logging
import cx_LoggingOptions
import cx_OptionParser
import cx_OracleUtils
import sys

import Options

# parse command line
parser = cx_OptionParser.OptionParser()
parser.AddOption(cx_OracleUtils.SchemaOption())
parser.AddOption(Options.ARRAY_SIZE)
parser.AddOption(Options.COMMIT_POINT)
parser.AddOption(Options.REPORT_POINT)
parser.AddOption(Options.SET_ROLE)
parser.AddOption("--include-tables", action = "append", metavar = "LIST",
        help = "name of tables to include in the import")
parser.AddOption("--exclude-tables", action = "append", metavar = "LIST",
        help = "name of tables to exclude from the import")
cx_LoggingOptions.AddOptions(parser)
parser.AddArgument("fileName", required = 1,
        help = "the name of the file from which to read the exported data or "
               "'-' to read the exported data from stdin")
options = parser.Parse()
cx_LoggingOptions.ProcessOptions(options)

# set up an importer
connection = cx_OracleUtils.Connect(options.schema, options.setRole)
importer = cx_ImportData.Importer(connection)
if options.arraySize:
    importer.cursor.arraysize = options.arraySize
importer.OpenFile(options.fileName)
if options.reportPoint:
    importer.reportPoint = options.reportPoint
if options.commitPoint:
    importer.commitPoint = options.commitPoint
    if options.reportPoint is None:
        importer.reportPoint = options.commitPoint

# set the list of tables for import
if options.includeTables:
    options.includeTables = [s.upper() for v in options.includeTables
            for s in v.split(",")]
if options.excludeTables:
    options.excludeTables = [s.upper() for v in options.excludeTables
            for s in v.split(",")]

# import all of the data
for tableName, columnNames in importer:
    checkName = tableName.upper()
    if options.includeTables and checkName not in options.includeTables \
            or options.excludeTables and checkName in options.excludeTables:
        cx_Logging.Trace("Skipping table %s...", tableName)
        importer.SkipTable()
    else:
        cx_Logging.Trace("Importing table %s...", tableName)
        importer.ImportTable()

