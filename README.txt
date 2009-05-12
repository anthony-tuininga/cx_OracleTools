cx_OracleTools
--------------
This project contains a number of Python scripts that handle Oracle databases.
Each of these scripts is self documented by the --help or -h option.
Additional documentation will be forthcoming at a later date. A brief
description of each script is provided here.

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
PatchDB - execute statements in files, checking for errors
RebuildTable - generate SQL script to rebuild the table
RecompileSource - recompile all invalid objects in the database

This project depends on the following projects if used in source mode. If you
are using the binary version these dependencies can be safely ignored.

cx_PyGenLib - http://cx-pygenlib.sourceforge.net
cx_PyOracleLib - http://cx-pyoraclelib.sourceforge.net
cx_Oracle - http://cx-oracle.sourceforge.net

The binary versions of these tools were built with cx_Freeze.

cx_Freeze - http://cx-freeze.sourceforge.net

This project is released under a free software license. See LICENSE.txt for
more details.

