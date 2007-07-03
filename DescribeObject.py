"""Describes objects in a database in a way suitable for creating the object
in a database."""

import cx_LoggingOptions
import cx_OptionParser
import cx_OracleObject
import cx_OracleUtils
import sys

import Options

# parse command line
parser = cx_OptionParser.OptionParser("DescribeObject")
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
parser.AddOption(Options.USE_DBA_VIEWS)
parser.AddOption(Options.MAX_LONG_SIZE)
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

# open the file
if options.fileName is None or options.fileName == "-":
    outFile = sys.stdout
else:
    outFile = file(options.fileName, "w")
describer = cx_OracleObject.Describer(environment, options, outFile)

# determine the object and its owner
objectName = options.objectName
isFullyQualified = "." in objectName
if isFullyQualified:
    objectOwner, objectName = objectName.split(".")
else:
    objectOwner = connection.username.upper()

# determine the type of object
objectType = cx_OracleObject.ObjectType(environment, objectOwner, objectName)
if objectType is None:
    objectOwner = objectOwner.upper()
    objectName = objectName.upper()
    objectType = cx_OracleObject.ObjectType(environment, objectOwner,
            objectName)
if objectType is None and not isFullyQualified:
    cursor = connection.cursor()
    cursor.execute("""
            select
              table_owner,
              table_name
            from %s_synonyms
            where owner = 'PUBLIC'
              and synonym_name = :objectName""" % environment.ViewPrefix(),
            objectName = objectName)
    row = cursor.fetchone()
    if row is not None:
        objectOwner, objectName = row
        objectType = cx_OracleObject.ObjectType(environment, objectOwner,
                objectName)
if objectType is None:
    raise "Object %s.%s does not exist." % (objectOwner, objectName)

# perform the actual describe
describer.schemas = [objectOwner]
describer.RetrieveAndExportObject(objectOwner, objectName, objectType)

