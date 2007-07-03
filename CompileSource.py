"""Executes statements found in a file, checking for errors and optionally
recompiling all invalid source after all statements in the file are
executed."""

import cx_Logging
import cx_LoggingOptions
import cx_OptionParser
import cx_OracleUtils
import cx_SQL
import sys

# parse command line
parser = cx_OptionParser.OptionParser("CompileSource")
parser.AddOption(cx_OracleUtils.SchemaOption())
parser.AddOption("--on-error-continue", action = "store_true",
        help = "when an error occurs, continue processing")
parser.AddOption("--with-recompile", action = "store_true",
        help = "after all source compiled, recompile invalid objects")
parser.AddOption("--on-recompile-error-continue", action = "store_true",
        help = "when an error occurs during recompilation, continue "
               "recompiling")
cx_LoggingOptions.AddOptions(parser)
parser.AddArgument("sourceFileName", required = 1,
        help = "the name of the file containing statements to execute or '-' "
               "to indicate statements ought to be read from stdin. Note that "
               "if the file does not exist and does not have the extension "
               "'.sql' then an attempt is made to open a file with that "
               "extension")
options = parser.Parse()
cx_LoggingOptions.ProcessOptions(options)

# connect to the database
connection = cx_OracleUtils.Connect(options.schema)
cursor = connection.cursor()

# compile the objects in the given file
for statement in cx_SQL.ParseStatementsInFile(options.sourceFileName):
    try:
        if isinstance(statement, cx_SQL.AlterStatement):
            statement.GetConstraintTypeAndName()
        statement.Process(connection, cursor)
        logMessage = statement.LogMessage()
        if logMessage is not None:
            cx_Logging.Trace("%s", logMessage)
    except:
        cx_Logging.Error("Error at line %s", statement.i_LineNo)
        if not options.onErrorContinue:
            raise
        excType, excValue = sys.exc_info()[:2]
        if excValue:
            cx_Logging.Error("%s: %s", excType, excValue)
        else:
            cx_Logging.Error("%s", excType)

# recompile the invalid objects in the schema, if applicable
if options.withRecompile:
    cx_OracleUtils.RecompileInvalidObjects(connection,
            [connection.username.upper()],
            raiseError = not options.onRecompileErrorContinue)

