"""Generate a script for rebuilding a table."""

import cx_LoggingOptions
import cx_OptionParser
import cx_OracleObject
import cx_OracleUtils
import sys

import Options

# parse command line
parser = cx_OptionParser.OptionParser("RebuildTable")
parser.AddOption(cx_OracleUtils.SchemaOption())
parser.AddOption(Options.NO_COMMENTS)
parser.AddOption(Options.NO_GRANTS)
parser.AddOption(Options.NO_RELATED)
parser.AddOption(Options.NO_TRIGGERS)
parser.AddOption(Options.DONT_MERGE_GRANTS)
parser.AddOption(Options.DEFAULT_TABLESPACE)
parser.AddOption(Options.DEFAULT_STORAGE)
parser.AddOption(Options.USE_DBA_VIEWS)
parser.AddOption(Options.MAX_LONG_SIZE)
parser.AddOption("--with-copydata", action = "store_true",
        help = "rebuilding the table is done with CopyData")
cx_LoggingOptions.AddOptions(parser)
parser.AddArgument("tableName", required = 1,
        help = "the name of the table to rebuild")
options = parser.Parse()
cx_LoggingOptions.ProcessOptions(options)

# set up describe environment
connection = cx_OracleUtils.Connect(options.schema)
environment = cx_OracleObject.Environment(connection, options)
describer = cx_OracleObject.Describer(environment, options)

# determine the object and its owner
tableName = options.tableName.upper()
if "." in tableName:
  tableOwner, tableName = tableName.split(".")
else:
  tableOwner = connection.username.upper()

# determine the type of object
cursor = connection.cursor()
cursor.execute("""
        select object_type
        from %s_objects
        where owner = :p_Owner
          and object_name = :p_Name
          and instr(object_type, 'BODY') = 0""" % environment.ViewPrefix(),
        p_Owner = tableOwner,
        p_Name = tableName)
row = cursor.fetchone()
if not row:
    raise "Object %s.%s does not exist." % (tableOwner, tableName)
objType, = row
if objType != "TABLE":
    raise "Object %s.%s is not a table." % (tableOwner, tableName)

# perform the describe
table = cx_OracleObject.ObjectByType(environment, tableOwner, tableName,
        objType)
cursor.execute("""
        select column_name
        from %s_tab_columns
        where owner = :p_Owner
          and table_name = :p_Name
        order by column_id""" % environment.ViewPrefix(),
        p_Owner = tableOwner,
        p_Name = tableName)
columnNames = [n for n, in cursor.fetchall()]

# produce the output
print "whenever sqlerror exit failure"
print "whenever oserror exit failure"
print
print "rename", tableName, "to bk;"
print
table.Export(sys.stdout, options.wantTablespace, options.wantStorage)
if options.wantGrants:
    table.ExportPrivileges(sys.stdout, options.mergeGrants)
if options.withCopydata:
    selectClauses = ", ".join(columnNames)
    print "!CopyData --no-check-exists --commit-point 250 --array-size 250",
    print "'select %s from bk'" % selectClauses,
    print tableName
else:
    selectClauses = ",\n  ".join(columnNames)
    print "insert /*+ append */ into", tableName, "nologging"
    print "select\n  %s\nfrom bk;" %  selectClauses
    print
    print "commit;"
print
print "drop table bk cascade constraints;"
print
constraints = []
if options.wantComments:
    table.ExportComments(sys.stdout)
if options.wantRelated:
    for constraint in table.Constraints():
        constraints.append((constraint.owner, constraint.name))
        describer.ExportObject(constraint)
    for index in table.Indexes():
        describer.ExportObject(index)
if options.wantTriggers:
    for trigger in table.Triggers():
        describer.ExportObject(trigger)
for constraint in table.ReferencedConstraints():
    if (constraint.owner, constraint.name) not in constraints:
        describer.ExportObject(constraint)

