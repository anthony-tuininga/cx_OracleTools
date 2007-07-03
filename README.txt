cx_OracleTools
--------------
This project contains a number of Python scripts that handle Oracle databases.
Each of these scripts is self documented by the --help or -h option.
Additional documentation will be forthcoming at a later date. A brief
description of each script is provided here.

CompileSource - execute statements in a file, checking for errors
CopyData - copy data from one table or view to another
DbDebugger - allows simple debugging of PL/SQL
DescribeObject - describe objects as SQL statements for recreation
DescribeSchema - describe multiple objects as SQL statements for recreation
DumpCSV - dump the results of a select statement as comma separated values
DumpData - dump the results of a select statement as insert statements
ExportColumn - dump the data from a column into a file
ExportData - dump the data from a database into a portable dump file
ExportObjects - describe object as SQL statements for recreation in files
ExportXML - export data from a table into a simple XML file
GeneratePatch - generate SQL script to go from one set of objects to another
GenerateView - generate a view statement for a table
ImportColumn - import the contents of a file into a column in the database
ImportData - import the data dumped with ExportData
ImportXML - import data from an XML file (such as those created by ExportXML)
RebuildTable - generate SQL script to rebuild the table
RecompileSource - recompile all invalid objects in the database

This project depends on the cx_PyGenLib and cx_PyOracleLib and cx_Oracle
projects. These must be installed before using these scripts if you are
running in source mode. If you are using the binary version, these projects
can be safely ignored. The binary versions of these tools were built with
cx_Freeze. Each of these projects can be found at

http://starship.python.net/crew/atuining

This project is released under a free software license. See LICENSE.txt for
more details.

