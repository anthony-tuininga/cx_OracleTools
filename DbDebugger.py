"""
Display output from a different Oracle process.
"""

import cx_Logging
import cx_LoggingOptions
import cx_OptionParser
import cx_OracleDebugger
import cx_OracleUtils

# parse command line
parser = cx_OptionParser.OptionParser()
parser.AddOption("--pipe-name", default = "DbDebugger",
        metavar = "NAME", prompt = "Pipe name",
        help = "use this pipe name for communication with the database")
parser.AddOption(cx_OracleUtils.SchemaOption())
cx_LoggingOptions.AddOptions(parser)
options = parser.Parse()
cx_LoggingOptions.ProcessOptions(options)

# connect to the database
connection = cx_OracleUtils.Connect(options.schema)
cx_Logging.Trace("Connected to %s@%s", connection.username,
        connection.tnsentry)
cx_Logging.Trace("Listening on pipe %s...", options.pipeName)

# display the messages
for message in cx_OracleDebugger.MessageGenerator(connection,
        options.pipeName):
    cx_Logging.Trace("%s", message)

