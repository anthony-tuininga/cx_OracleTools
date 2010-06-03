"""
Recompile all of the invalid source objects in an Oracle database.
"""

import cx_LoggingOptions
import cx_OptionParser
import cx_OracleUtils

# parse command line
parser = cx_OptionParser.OptionParser()
parser.AddOption(cx_OracleUtils.SchemaOption())
parser.AddOption("--on-error-continue", action = "store_false",
        dest = "raiseError", default = True,
        help = "when an error occurs, continue processing")
parser.AddOption("--connect-as-owner", action = "store_true", default = False,
        help = "connect as the owner of the invalid object")
parser.AddOption("--include", metavar = "LIST", action = "append",
        help = "list of schemas to recompile instead of the entire database")
parser.AddOption("--include-file", metavar = "FILE",
        help = "recompile objects found in schemas with the given names "
               "found in the specified file")
parser.AddOption("--exclude", metavar = "LIST", action = "append",
        help = "list of schemas to exclude from recompile")
cx_LoggingOptions.AddOptions(parser)
options = parser.Parse()
cx_LoggingOptions.ProcessOptions(options)

# connect to the database
connection = cx_OracleUtils.Connect(options.schema)

# massage the list of schemas to include
if options.include:
    includeSchemas = [s.upper() for v in options.include for s in v.split(",")]
elif options.includeFile:
    includeSchemas = [s.strip() for s in open(options.includeFile)]
else:
    cursor = connection.cursor()
    cursor.arraysize = 25
    cursor.execute("""
            select username
            from dba_users u
            where exists
              ( select owner
                from dba_objects
                where owner = u.username
              )""")
    includeSchemas = [n for n, in cursor]

# massage the list of schemas to exclude
excludeSchemas = []
if options.exclude:
    excludeSchemas = [s.upper() for v in options.exclude for s in v.split(",")]

# perform the recompile
cx_OracleUtils.RecompileInvalidObjects(connection, includeSchemas,
        excludeSchemas, raiseError = options.raiseError,
        connectAsOwner = options.connectAsOwner)

