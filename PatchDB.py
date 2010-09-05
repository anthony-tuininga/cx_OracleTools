"""
Performs commands to modify the contents of a database using scripts.
"""

import cx_LoggingOptions
import cx_OptionParser
import cx_OracleUtils
import cx_PatchCommands

# parse command line
parser = cx_OptionParser.OptionParser()
parser.AddOption(cx_OracleUtils.SchemaOption())
parser.AddOption("--on-error-continue", action = "store_true",
        help = "when an error occurs, continue processing")
parser.AddOption("--with-recompile", action = "store_true",
        help = "after all scripts have been run, recompile invalid objects")
parser.AddOption("--on-recompile-error-continue", action = "store_true",
        help = "when an error occurs during recompilation, continue "
               "recompiling")
cx_LoggingOptions.AddOptions(parser)
parser.AddArgument("fileName", variable = True, required = True,
        help = "the name of the file(s) containing statements to execute or "
               "'-' to indicate statements ought to be read from stdin. Note "
               "that if the file does not exist and does not have the "
               "extension '.sql' then an attempt is made to open a file with "
               "that extension")
options = parser.Parse()
cx_LoggingOptions.ProcessOptions(options)

# connect to the database
connection = cx_OracleUtils.Connect(options.schema)

# process each file
processor = cx_PatchCommands.Processor(connection, options.onErrorContinue)
for fileName in options.fileName:
    processor.ProcessFile(fileName)

# recompile the invalid objects in the schema, if applicable
if options.withRecompile:
    cx_OracleUtils.RecompileInvalidObjects(connection,
            [connection.username.upper()],
            raiseError = not options.onRecompileErrorContinue)

