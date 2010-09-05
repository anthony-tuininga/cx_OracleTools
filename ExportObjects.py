"""
Export all of the objects in a schema as a set of directories named after
the type of object containing a set of files named after the object itself.
"""

import cx_LoggingOptions
import cx_OptionParser
import cx_OracleObject
import cx_OracleUtils

import Options

# parse command line
parser = cx_OptionParser.OptionParser()
parser.AddOption(cx_OracleUtils.SchemaOption())
parser.AddOption(Options.NO_COMMENTS)
parser.AddOption(Options.NO_GRANTS)
parser.AddOption(Options.NO_QUOTAS)
parser.AddOption(Options.NO_RELATED)
parser.AddOption(Options.NO_TRIGGERS)
parser.AddOption(Options.DONT_MERGE_GRANTS)
parser.AddOption(Options.DEFAULT_TABLESPACE)
parser.AddOption(Options.DEFAULT_STORAGE)
parser.AddOption(Options.USE_DBA_VIEWS)
parser.AddOption(Options.INCLUDE_SEQUENCE_VALUES)
parser.AddOption(Options.INCLUDE_VIEW_COLUMNS)
parser.AddOption(Options.INCLUDE_ROLES)
parser.AddOption(Options.INCLUDE_USERS)
parser.AddOption(Options.INCLUDE_CONTEXTS)
parser.AddOption(Options.SPLIT_RELATED)
parser.AddOption(Options.NAMES)
parser.AddOption(Options.NAMES_FILE)
parser.AddOption(Options.ONLY_TYPES)
parser.AddOption(Options.ONLY_IF)
parser.AddOption(Options.MAX_LONG_SIZE)
parser.AddOption(Options.AS_OF_SCN)
parser.AddOption(Options.AS_OF_TIMESTAMP)
parser.AddOption("--base-dir", default = ".", metavar = "DIR",
        help = "base directory in which to place exported objects")
parser.AddOption("--suppress-owner-dir",
        default = False,
        action = "store_true",
        help = "suppress the creation of the owner directory")
cx_LoggingOptions.AddOptions(parser)
options = parser.Parse()
cx_LoggingOptions.ProcessOptions(options)

# set up describe environment
connection = cx_OracleUtils.Connect(options.schema)
environment = cx_OracleObject.Environment(connection, options)
exporter = cx_OracleObject.Exporter(environment, options, options.baseDir)

# perform the work of exporting the objects
exporter.ExportAllObjects()

