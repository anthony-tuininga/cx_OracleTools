"""
Describes objects in a database in a way suitable for creating the object
in a database.
"""

import cx_LoggingOptions
import cx_OptionParser
import cx_OracleObject
import cx_OracleUtils
import sys

import Options

# parse command line
parser = cx_OptionParser.OptionParser()
parser.AddOption(cx_OracleUtils.SchemaOption())
parser.AddOption(Options.NO_COMMENTS)
parser.AddOption(Options.NO_GRANTS)
parser.AddOption(Options.NO_RELATED)
parser.AddOption(Options.NO_TRIGGERS)
parser.AddOption(Options.DONT_MERGE_GRANTS)
parser.AddOption(Options.DEFAULT_TABLESPACE)
parser.AddOption(Options.DEFAULT_STORAGE)
parser.AddOption(Options.SHOW_FOREIGN_KEYS)
parser.AddOption(Options.SHOW_SYNONYMS)
parser.AddOption(Options.INCLUDE_SEQUENCE_VALUES)
parser.AddOption(Options.INCLUDE_VIEW_COLUMNS)
parser.AddOption(Options.USE_DBA_VIEWS)
parser.AddOption(Options.MAX_LONG_SIZE)
parser.AddOption(Options.AS_OF_SCN)
parser.AddOption(Options.AS_OF_TIMESTAMP)
cx_LoggingOptions.AddOptions(parser)
parser.AddArgument("objectName", required = True,
        help = "the name of the object to describe")
parser.AddArgument("fileName",
        help = "the name of the file to populate with the statements or '-'"
               "to output the statements to stdout; if a file name is not "
               "specified, the statements will also be output to stdout")
options = parser.Parse()
cx_LoggingOptions.ProcessOptions(options)

# set up describe environment
connection = cx_OracleUtils.Connect(options.schema)
environment = cx_OracleObject.Environment(connection, options)

# determine the owner, name and type of the object
objectOwner, objectName, objectType = \
        environment.ObjectInfo(options.objectName)

# open the file
if options.fileName is None or options.fileName == "-":
    outFile = sys.stdout
else:
    outFile = file(options.fileName, "w")
describer = cx_OracleObject.Describer(environment, options, outFile)

# perform the actual describe
describer.schemas = [objectOwner]
describer.RetrieveAndExportObject(objectOwner, objectName, objectType)

