"""
Dump data as SQL statements given a SQL query to execute.
"""

import cx_LoggingOptions
import cx_OptionParser
import cx_Oracle
import cx_OracleUtils
import datetime

# parse command line
parser = cx_OptionParser.OptionParser()
parser.AddOption(cx_OracleUtils.SchemaOption())
parser.AddOption("--sort-by", metavar = "STR",
        help = "append an order by clause with this value to the query")
parser.AddOption("--source-query", metavar = "STR",
        help = "use this query instead of ""select * from <TableName>""")
cx_LoggingOptions.AddOptions(parser)
parser.AddArgument("tableName", required = 1,
        help = "the name of the table to use as the target for the insert "
               "statements that are generated")
options = parser.Parse()
cx_LoggingOptions.ProcessOptions(options)

# perform the work of dumping the data out of the given table
connection = cx_OracleUtils.Connect(options.schema)
query = options.sourceQuery
if not query:
    query = "select * from " + options.tableName
    if options.sortBy:
        query += " order by " + options.sortBy
cursor = connection.cursor()
cursor.execute(query)
description = cursor.description
format = "insert into %s (\n  %s\n) values (\n  %s\n);\n"
sequence = range(len(description))
for row in cursor:
    names = []
    values = []
    for i in sequence:
        value = row[i]
        if value is None:
            continue
        names.append(description[i][0])
        if description[i][1] == connection.DATETIME \
                and not isinstance(value, datetime.datetime):
            value = datetime.datetime(value.year, value.month, value.day,
                    value.hour, value.minute, value.second)
        binaryData = description[i][1] in (cx_Oracle.BLOB, cx_Oracle.BINARY)
        values.append(cx_OracleUtils.GetConstantRepr(value, binaryData))
    if names:
        sql = "insert into %s (\n  %s\n) values (\n  %s\n);\n" % \
                (options.tableName, ",\n  ".join(names), ",\n  ".join(values))
        print sql
print "commit;"

