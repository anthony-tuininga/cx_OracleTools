==============
cx_OracleTools
==============

This document covers a cross platform set of tools for working with Oracle
databases. These tools have been developed over the past number of years and
are designed to provide easier access to information or capabilities than that
provided by default with Oracle.

**NOTE:** These tools are a work in progress and are geared for people who are
reasonably comfortable with Oracle.  This means that while an attempt will be
made to maintain a stable interface for these tools, changes or extensions will
be made if there is a valid reason for it.

**NOTE:** Please see HISTORY.txt for a list of changes.

--------
Overview
--------

Environments
============

These tools have been known to work in the following environments:

Oracle Version:
    - Oracle 9i Release 2
    - Oracle 10g Release 1
    - Oracle 10g Release 2
    - Oracle 11g Release 1
    - Oracle 11g Release 2

Operating Systems:
    - Windows (32-bit and 64-bit)
    - Linux (32-bit and 64-bit)
    - SunOS 5.8
    - HP-UX 11


Conventions
===========

In the description of each tool, the following conventions are used for the
arguments and options:

    - Items enclosed in brackets ("[]") are optional.
    - Mixed and lower case items are to be typed exactly as displayed.
    - UPPERCASE items are to be replaced by the user desired value.
    - If an option is shown with an equals sign ("="), the equals sign may be
      replaced with a space
    - Special option parameter values:
        * N - a number must be entered if the option is specified.
        * SCHEMA - Oracle connect string in the format of
          ORACLELOGONID[/PASSWORD]@TNSENTRY[ AS SYSDBA|SYSOPER] If PASSWORD is
          omitted, it will be prompted for.
        * ROLE - Oracle role in the format of: ROLENAME[/PASSWORD] If the role
          requires a password and one is not specified, then the attempt to
          enable the role will fail and the tool will stop.

Common Options
==============

The following options are common to all of the tools:

+---------------------+-------------------------------------------------------+
| name                | description                                           |
+---------------------+-------------------------------------------------------+
| -h, --help          | display a brief usage description of the arguments and|
|                     | options and stop                                      |
+---------------------+-------------------------------------------------------+
| --log-file=         | the name of the file to log messages to or the words  |
|                     | ``stdout`` or ``stderr``; the default is ``stderr``   |
+---------------------+-------------------------------------------------------+
| --log-level=        | the level at which to log messages, one of debug (10),|
|                     | info (20), warning (30), error (40) or critical (50); |
|                     | the default is ``error``                              |
+---------------------+-------------------------------------------------------+
| --log-prefix=       | the prefix to use for log messages which is a mask    |
|                     | containing %i (id of the thread logging the message), |
|                     | %d (date at which the message was logged), %t (time at|
|                     | which the message was logged) or %l (level at which   |
|                     | the message was logged); the default is ``%t``        |
+---------------------+-------------------------------------------------------+
| --show-banner       | display the program name and version                  |
+---------------------+-------------------------------------------------------+
| -t, --traceback     | when an error is encountered, display an internal     |
|                     | traceback stack                                       |
+---------------------+-------------------------------------------------------+
| --version           | display the version information and stop              |
+---------------------+-------------------------------------------------------+


--------
CopyData
--------

This utility is used to copy data between “tables.”  These tables may be in the
same database or in different databases.  Also, the source table may be an SQL
query.

Usage
=====

CopyData [options] SOURCE [DESTINATION]

When you run CopyData, it connects to the source and destination databases and
optionally activates the specified non-default role specified.  It then
proceeds to read from the source and write to the destination.  This is done in
a bulk array format which is extremely efficient.  By default, it checks to see
if the row about to be written to the destination already exists and if so, if
it matches.  This means that you are able to insert new rows and only update
changed rows.

Arguments
=========

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| SOURCE              | Name of the table from which the data will be copied. |
|                     | This may be qualified with a schema.  Also, this may  |
|                     | be specified as a SQL statement. The following are    |
|                     | examples of valid source:                             |
|                     | - sourcetbl                                           |
|                     | - common.sourcetbl                                    |
|                     | - select col1,col2 from common.sourcetbl              |
+---------------------+-------------------------------------------------------+
| DESTINATION         | Name of the table or view into which the data will be |
|                     | copied.  If source is not a SQL statement, this may   |
|                     | be omitted, in which case, the source table name will |
|                     | be used.                                              |
+---------------------+-------------------------------------------------------+

Options
=======

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| -t, --traceback     | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --show-banner       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --version           | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| -h, --help          | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --source-schema=\   | Use this to connect to the database and not the       |
| SCHEMA              | environment variable ORA_USERID for the source. NOTE: |
|                     | If this (or ORA_USERID) does not contain the password,|
|                     | it will be prompted for.                              |
+---------------------+-------------------------------------------------------+
| --dest-schema=\     | Use this to connect to the database and not the       |
| SCHEMA              | environment variable ORA_USERID for the destination.  |
|                     | NOTE: If this (or ORA_USERID) does not contain the    |
|                     | password, it will be prompted for.                    |
+---------------------+-------------------------------------------------------+
| --key-columns=COLS  | Comma separated list of the name of columns that are  |
|                     | to be treated as the key.  These are used when        |
|                     | checking if the row exists and/or has been modified.  |
|                     | If a row in the destination table cannot be found     |
|                     | when using the values from the source table for these |
|                     | columns it is assumed they do not exist. Similarly,   |
|                     | if the row exists but other values differ, it is      |
|                     | assumed to be modified. NOTE: if this option is not   |
|                     | specified, an attempt is made to determine the        |
|                     | primary key or unique constraint on the destination   |
|                     | table.                                                |
+---------------------+-------------------------------------------------------+
| --no-check-exists   | Do not check to see if the row exists in the          |
|                     | destination; always insert the row from the source.   |
+---------------------+-------------------------------------------------------+
| --no-check-modified | Do not check to see if the row has been modified on   |
|                     | the destination.  That is, always update the row on   |
|                     | the destination if it exists.                         |
+---------------------+-------------------------------------------------------+
| --skip=N            | Number of rows from the source to skip before         |
|                     | starting to copy.                                     |
+---------------------+-------------------------------------------------------+
| --row-limit=N       | Number of rows to process.  This number includes the  |
|                     | number of rows skipped, if any.                       |
+---------------------+-------------------------------------------------------+
| --commit-point=N    | Issue a commit every N rows processed.  If not        |
|                     | specified, a commit will only be issued after the     |
|                     | entire table is copied.                               |
+---------------------+-------------------------------------------------------+
| --report-point=N    | Display a message every N rows processed.  If not     |
|                     | specified, no progress messages will be issued.       |
+---------------------+-------------------------------------------------------+
| --array-size=N      | This is the number of rows that will be read from the |
|                     | database at one time.  It is recommended to set this  |
|                     | to as large a value as possible without incurring     |
|                     | paging.                                               |
+---------------------+-------------------------------------------------------+
| --max-long-size=N   | Specify the maximum length of a long or long raw      |
|                     | column. This defaults to 128K.                        |
+---------------------+-------------------------------------------------------+
| --source-role=ROLE  | Enable this role after connecting to the source       |
|                     | database prior to executing any SQL on that database. |
|                     | May also be specified as role/password for password   |
|                     | required roles.                                       |
+---------------------+-------------------------------------------------------+
| --dest-role=ROLE    | Enable this role after connecting to the destination  |
|                     | database prior to executing any SQL on that database. |
|                     | May also be specified as role/password for password   |
|                     | required roles.                                       |
+---------------------+-------------------------------------------------------+
| --log-file=         | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-level=        | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-prefix=       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+


----------
DbDebugger
----------

This utility is used in conjunction with the pkg_Debug package to provide real
time messaging from PL/SQL procedure to an outside process.

Usage
=====

DbDebugger [options]

When you run DbDebugger, it will wait for messages from pkg_Debug where the
pipename specified matches.  You should not run more than one DbDebugger for a
given pipename on a database as it is undefined which DbDebugger will get each
line of output.

Options
=======

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| -t, --traceback     | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --show-banner       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| -p, --prompt        | Prompts the user for the pipename and database        |
|                     | connect string.                                       |
+---------------------+-------------------------------------------------------+
| --version           | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| -h, --help          | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --pipe-name=NAME    | Name of pipe to listen on.  If omitted, defaults to   |
|                     | DbDebugger.  Note: NAME is not case sensitive.        |
+---------------------+-------------------------------------------------------+
| --schema            | Use this to connect to the database and not the       |
|                     | environment variable ORA_USERID.  Note: If this (or   |
|                     | ORA_USERID) does not contain the password, it will be |
|                     | prompted for.                                         |
+---------------------+-------------------------------------------------------+
| --log-file=         | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-level=        | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-prefix=       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+


--------------
DescribeObject
--------------

This utility is used to show the DDL necessary to recreate an object in the
database.

Usage
=====

DescribeObject [options] OBJECTNAME [FILENAME]

When you run DescribeObject it will describe the specific object with the
specified options.

Arguments
=========

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| OBJECTNAME          | Name of the object to be described.  This may be      |
|                     | qualified by a schema; however, unless DBA views are  |
|                     | used the description may not be complete.             |
+---------------------+-------------------------------------------------------+
| FILENAME            | Name of the file to put the description of the object |
|                     | into.  If omitted or specified as '-', then the output|
|                     | will be shown on the screen (stdout).                 |
+---------------------+-------------------------------------------------------+

Options
=======

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| -t, --traceback     | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --show-banner       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --version           | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| -h, --help          | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --schema=SCHEMA     | Use this to connect to the database and not the       |
|                     | environment variable ORA_USERID.  Note: If this (or   |
|                     | ORA_USERID) does not contain the password, it will be |
|                     | prompted for.                                         |
+---------------------+-------------------------------------------------------+
| --no-comments       | Do not include object comments in the description.    |
+---------------------+-------------------------------------------------------+
| --no-grants         | Do not include the grants in the description.         |
+---------------------+-------------------------------------------------------+
| --no-related        | Do not include related objects in the description     |
|                     | (e.g. the body of a package, the indexes and          |
|                     | constraints for a table, etc.).                       |
+---------------------+-------------------------------------------------------+
| --no-triggers       | Do not include related triggers in the description.   |
+---------------------+-------------------------------------------------------+
| --dont-merge-grants | Show each grant as a separate statement.  In the case |
|                     | where multiple privileges are granted to the same     |
|                     | user/role, each one will be a separate statement.     |
+---------------------+-------------------------------------------------------+
| --default-tablespace| Do not include tablespace specifications.             |
+---------------------+-------------------------------------------------------+
| --default-storage   | Do not include storage specifications.                |
+---------------------+-------------------------------------------------------+
| --show-foreign-keys | Include all accessible foreign keys that reference the|
|                     | object being described.                               |
+---------------------+-------------------------------------------------------+
| --show-synonyms     | Include synonyms referencing the object.              |
+---------------------+-------------------------------------------------------+
| --include-sequence-\| When describing a sequence include its current value. |
| values              |                                                       |
+---------------------+-------------------------------------------------------+
| --include-view-\    | Include column names when describing views.           |
| columns             |                                                       |
+---------------------+-------------------------------------------------------+
| --use-dba-views     | Use dba_xxx views for retrieving the information      |
|                     | about the object.  If the connecting user does not    |
|                     | have security to see them, an error will result.      |
+---------------------+-------------------------------------------------------+
| --max-long-size=N   | Specify the maximum length of a view or trigger. This |
|                     | defaults to 128K.                                     |
+---------------------+-------------------------------------------------------+
| --as-of-scn=SCN     | All queries performed to retrieve information about   |
|                     | the object will use a flashback query to the specified|
|                     | system change number.                                 |
+---------------------+-------------------------------------------------------+
| --as-of-timestamp=TS| All queries performed to retrieve information about   |
|                     | the object will use a flashback query to the specified|
|                     | timestamp expression.                                 |
+---------------------+-------------------------------------------------------+
| --log-file=         | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-level=        | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-prefix=       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+


--------------
DescribeSchema
--------------

This utility is used to describe all objects within one or more schemas.

Usage
=====

DescribeSchema [options] [FILENAME]

When you run DescribeSchema it will describe all the objects within the
specified schema into the specified file.

Arguments
=========

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| FILENAME            | Name of the file in which the output will be placed.  |
|                     | If omitted or specified as '-', then the output will  |
|                     | be shown on the screen (stdout).                      |
+---------------------+-------------------------------------------------------+

Options
=======

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| -t, --traceback     | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --show-banner       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --version           | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| -h, --help          | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --schema=SCHEMA     | Use this to connect to the database and not the       |
|                     | environment variable ORA_USERID.  Note: If this (or   |
|                     | ORA_USERID) does not contain the password, it will be |
|                     | prompted for.                                         |
+---------------------+-------------------------------------------------------+
| --no-comments       | Do not include object comments in the description.    |
+---------------------+-------------------------------------------------------+
| --no-grants         | Do not include the grants in the description.         |
+---------------------+-------------------------------------------------------+
| --no-quotas         | Do not include quotas on tablespaces.                 |
+---------------------+-------------------------------------------------------+
| --dont-merge-grants | Show each grant as a separate statement.  In the case |
|                     | where multiple privileges are granted to the same     |
|                     | user/role, each one will be a separate statement.     |
+---------------------+-------------------------------------------------------+
| --default-tablespace| Do not include tablespace specifications.             |
+---------------------+-------------------------------------------------------+
| --default-storage   | Do not include storage specifications.                |
+---------------------+-------------------------------------------------------+
| --include-sequence-\| When describing a sequence include its current value. |
| values              |                                                       |
+---------------------+-------------------------------------------------------+
| --include-view-\    | Include column names when describing views.           |
| columns             |                                                       |
+---------------------+-------------------------------------------------------+
| --object-name-only  | Do not include the DDL statements necessary to create |
|                     | the objects; only show the object names.              |
+---------------------+-------------------------------------------------------+
| --name=NAME         | Include the objects in the schema(s) with the         |
|                     | specified name(s).  This option may be specified      |
|                     | multiple times and/or multiple names may be specified |
|                     | separated by commas.                                  |
+---------------------+-------------------------------------------------------+
| --name-file=FILE    | This option behaves the same as --name except that    |
|                     | the argument to the option is the name of a file      |
|                     | containing the names of schemas to export, one per    |
|                     | line.                                                 |
+---------------------+-------------------------------------------------------+
| --only-types=TYPES  | Only include objects of the specified type(s).  This  |
|                     | may be specified multiple times and/or the types may  |
|                     | be separated by commas.  The supported types are those|
|                     | valid for user_objects, all_objects, or dba_objects.  |
|                     | If the type contains blanks you can either enclose    |
|                     | the type within quotation marks or replace the blanks |
|                     | with underscores.                                     |
+---------------------+-------------------------------------------------------+
| --only-if=CLAUSE    | Only include objects which match the specified        |
|                     | criteria.  The criteria is added to the where clause  |
|                     | of the select statement that is executed against      |
|                     | user_objects, all_objects, or dba_objects.            |
+---------------------+-------------------------------------------------------+
| --use-dba-views     | Use dba_xxx views for retrieving the information      |
|                     | about the object.  If the connecting user does not    |
|                     | have security to see them, an error will result.      |
+---------------------+-------------------------------------------------------+
| --include-roles     | Include all roles that this schema has been granted   |
|                     | "with admin option."                                  |
+---------------------+-------------------------------------------------------+
| --include-users     | Include a create user statement for each schema.      |
+---------------------+-------------------------------------------------------+
| --include-contexts  | Include contexts in output which reference packages   |
|                     | owned by the schema(s).                               |
+---------------------+-------------------------------------------------------+
| --max-long-size=N   | Specify the maximum length of a view or trigger. This |
|                     | defaults to 128K.                                     |
+---------------------+-------------------------------------------------------+
| --as-of-scn=SCN     | All queries performed to retrieve information about   |
|                     | the object will use a flashback query to the specified|
|                     | system change number.                                 |
+---------------------+-------------------------------------------------------+
| --as-of-timestamp=TS| All queries performed to retrieve information about   |
|                     | the object will use a flashback query to the specified|
|                     | timestamp expression.                                 |
+---------------------+-------------------------------------------------------+
| --log-file=         | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-level=        | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-prefix=       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+


-------
DumpCSV
-------

This utility is used to dump information from the database into a comma
separated file.

Usage
=====

DumpCSV [options] SQL [FILENAME]

When you run DumpCSV it will connect to the database, execute the SQL statement
and place the results in the specified file.

Arguments
=========

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| SQL                 | The SQL statement that is to be used to select the    |
|                     | data to be dumped.  This will normally be enclosed in |
|                     | quotes. When the --sql-in-file option is specified,   |
|                     | however, it contains the name of a file containing    |
|                     | the SQL statement.                                    |
+---------------------+-------------------------------------------------------+
| FILENAME            | Name of the file in which the output will be placed.  |
|                     | If omitted or specified as '-', then the output will  |
|                     | be shown on the screen (stdout).                      |
+---------------------+-------------------------------------------------------+

Options
=======

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| -t, --traceback     | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --show-banner       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --version           | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| -h, --help          | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --schema=SCHEMA     | Use this to connect to the database and not the       |
|                     | environment variable ORA_USERID.  Note: If this (or   |
|                     | ORA_USERID) does not contain the password, it will be |
|                     | prompted for.                                         |
+---------------------+-------------------------------------------------------+
| --record-sep=CHAR   | Use the specified character as the separator          |
|                     | character between records (rows).  If not specified a |
|                     | new line will be started for each row.                |
+---------------------+-------------------------------------------------------+
| --field-sep=CHAR    | Use the specified character as the separator          |
|                     | character between fields (columns).  If not           |
|                     | specified, a comma is used.                           |
+---------------------+-------------------------------------------------------+
| --string-encloser=\ | Use the specified character around string fields.  If |
| CHAR                | not specified, quotation marks (") will be used.      |
+---------------------+-------------------------------------------------------+
| --escape-char=CHAR  | Use the specified character before any string         |
|                     | encloser characters in a string field.  If not        |
|                     | specified, a back slash (\) will be used.             |
+---------------------+-------------------------------------------------------+
| --report-point=N    | Display a message every N rows processed.  If not     |
|                     | specified, no progress messages will be issued.       |
+---------------------+-------------------------------------------------------+
| --sql-in-file       | Specifies that the SQL parameter is the name of a     |
|                     | file which contains the SQL statement to be executed. |
|                     | This allows for long SQL statements to be easily      |
|                     | passed to DumpCSV.                                    |
+---------------------+-------------------------------------------------------+
| --log-file=         | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-level=        | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-prefix=       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+


--------
DumpData
--------

This utility is used to dump data from an Oracle table in the form of insert
SQL statements that can be used to load the data elsewhere.

Usage
=====

DumpData [options] TABLENAME

When you run DumpData it will connect to the database and display the data from
the specified table as insert statements.

Arguments
=========

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| TABLENAME           | The name of the table to dump and insert into.  If    |
|                     | --source-query is specified, then this is only the    |
|                     | name of the table to use in the insert statements.    |
+---------------------+-------------------------------------------------------+

Options
=======

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| -t, --traceback     | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --show-banner       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --version           | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| -h, --help          | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --schema=SCHEMA     | Use this to connect to the database and not the       |
|                     | environment variable ORA_USERID.  Note: If this (or   |
|                     | ORA_USERID) does not contain the password, it will be |
|                     | prompted for.                                         |
+---------------------+-------------------------------------------------------+
| --sort-by=STR       | Append an "order by" clause with this value to the    |
|                     | query.                                                |
+---------------------+-------------------------------------------------------+
| --source-query=STR  | Use the specified SQL instead of doing a select *     |
|                     | from Table.  NOTE: the query does not need to select  |
|                     | from Table; however the insert statements that are    |
|                     | generated will always insert into Table.              |
+---------------------+-------------------------------------------------------+
| --log-file=         | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-level=        | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-prefix=       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+


------------
ExportColumn
------------

This utility is used to dump the contents of a column from an Oracle table into
the specified file.

Usage
=====

ExportColumn [options] STATEMENT FILENAME [VALUES ...]

When you run ExportColumn it will connect to the database, select the column
specified and place the contents of that column into the specified file.

Arguments
=========

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| STATEMENT           | Specifies the column to be exported.  This is either  |
|                     | a SQL statement to execute, the name of the file      |
|                     | containing the statement to execute if the            |
|                     | --statement-in-file option is specified, or the name  |
|                     | of the column which is to be exported in the form     |
|                     | [Owner.]Table.Column (in this case a select statement |
|                     | will be fabricated with the values argument making up |
|                     | the where clause).                                    |
+---------------------+-------------------------------------------------------+
| FILENAME            | The name of the file into which the column is to be   |
|                     | dumped.                                               |
+---------------------+-------------------------------------------------------+
| VALUES              | This is a space separated list of name=VALUE which    |
|                     | will be used for bind variables if a SQL statement is |
|                     | specified or will be used in the where clause if      |
|                     | [Owner.]Table.Column is specified for STATEMENT.      |
+---------------------+-------------------------------------------------------+

Options
=======

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| -t, --traceback     | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --show-banner       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --version           | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| -h, --help          | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --schema=SCHEMA     | Use this to connect to the database and not the       |
|                     | environment variable ORA_USERID.  Note: If this (or   |
|                     | ORA_USERID) does not contain the password, it will be |
|                     | prompted for.                                         |
+---------------------+-------------------------------------------------------+
| --binary            | The column to be exported is a BLOB or LONG RAW and   |
|                     | not a CLOB or LONG.                                   |
+---------------------+-------------------------------------------------------+
| --statement-in-file | The argument STATEMENT is to be taken as the name of  |
|                     | a file from which to get the SQL statement to execute.|
+---------------------+-------------------------------------------------------+
| --log-file=         | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-level=        | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-prefix=       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+


----------
ExportData
----------

This utility is used to export data from the database in a transportable
format.  It is reloaded using the ImportData utility.  This is an alternative
to Oracle’s import and export utilities for the movement of data. These
utilities do not import or export object definitions, however.

Usage
=====

ExportData [options] FILENAME

When you run ExportData it will connect to the database and export the data
from the tables for the specified schema into the specified file.

Arguments
=========

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| FILENAME            | The name of the file where the export will be placed. |
+---------------------+-------------------------------------------------------+

Options
=======

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| -t, --traceback     | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --show-banner       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --version           | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| -h, --help          | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --schema=SCHEMA     | Use this to connect to the database and not the       |
|                     | environment variable ORA_USERID.  Note: If this (or   |
|                     | ORA_USERID) does not contain the password, it will be |
|                     | prompted for.                                         |
+---------------------+-------------------------------------------------------+
| --array-size=N      | This is the number of rows that will be read from the |
|                     | database at one time.  It is recommended to set this  |
|                     | to as large a value as possible without incurring     |
|                     | paging.                                               |
+---------------------+-------------------------------------------------------+
| --report-point=N    | Display a message every N rows processed.  If not     |
|                     | specified, no progress messages will be issued during |
|                     | the export of a table.                                |
+---------------------+-------------------------------------------------------+
| --max-long-size=N   | Specify the maximum length of a long or long raw      |
|                     | column. This defaults to 128K.                        |
+---------------------+-------------------------------------------------------+
| --set-role=ROLE     | Enable this role after connecting to the database and |
|                     | prior to executing any SQL on that database.          |
+---------------------+-------------------------------------------------------+
| --include-schema-\  | Store the name of the schema being exported along     |
| name                | with the table name in the export file. This is       |
|                     | useful for multiple schema exports.                   |
+---------------------+-------------------------------------------------------+
| --include-tables=\  | Only export the tables specified in the list.  This   |
| LIST                | option may be specified multiple times and/or         |
|                     | multiple tables may be specified separated by commas. |
+---------------------+-------------------------------------------------------+
| --exclude-tables=\  | Export all tables for the schema except for the       |
| LIST                | tables specified in the list.  This option may be     |
|                     | specified multiple times and/or multiple tables may   |
|                     | be specified separated by commas. NOTE: only one of   |
|                     | --include-tables and --exclude-tables is used. If both|
|                     | are specified, then --include-tables is used.         |
+---------------------+-------------------------------------------------------+
| --skip=N            | Number of rows to skip before starting export.  NOTE: |
|                     | If you are exporting more than one table, this limit  |
|                     | will be applied independently to each table that is   |
|                     | exported.                                             |
+---------------------+-------------------------------------------------------+
| --row-limit=N       | Number of rows to export.  NOTE: if you are exporting |
|                     | more than one table, this limit will be applied       |
|                     | independently to each table that is exported.         |
+---------------------+-------------------------------------------------------+
| --log-file=         | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-level=        | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-prefix=       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+


-------------
ExportObjects
-------------

This utility is used to extract the syntax of all objects in the specified
schemas.  Each object will be extracted into its own file within
sub-directories of the specified directory.

Usage
=====

ExportObjects [options]

This utility connects to the database and determines the objects that match the
selection criteria (owner, type).  It then proceeds to create a sub-directory
for each owner and a sub-directory under that for each type of object.  It then
describes the syntax for each object into a separate file within the type
sub-directory.

Options
=======

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| -t, --traceback     | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --show-banner       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --version           | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| -h, --help          | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --schema=SCHEMA     | Use this to connect to the database and not the       |
|                     | environment variable ORA_USERID.  Note: If this (or   |
|                     | ORA_USERID) does not contain the password, it will be |
|                     | prompted for.                                         |
+---------------------+-------------------------------------------------------+
| --no-comments       | Do not include object comments in the description.    |
+---------------------+-------------------------------------------------------+
| --no-grants         | Do not include the grants in the description.         |
+---------------------+-------------------------------------------------------+
| --no-quotas         | Do not include quotas on tablespaces.                 |
+---------------------+-------------------------------------------------------+
| --no-related        | Do not include related objects in the description     |
|                     | (e.g. the body of a package, the indexes and          |
|                     | constraints for a table, etc.).                       |
+---------------------+-------------------------------------------------------+
| --no-triggers       | Do not include related triggers in the description.   |
+---------------------+-------------------------------------------------------+
| --dont-merge-grants | Show each grant as a separate statement.  In the case |
|                     | where multiple privileges are granted to the same     |
|                     | user/role, each one will be a separate statement.     |
+---------------------+-------------------------------------------------------+
| --default-tablespace| Do not include tablespace specifications.             |
+---------------------+-------------------------------------------------------+
| --default-storage   | Do not include storage specifications.                |
+---------------------+-------------------------------------------------------+
| --use-dba-views     | Use dba_xxx views for retrieving the information      |
|                     | about the object.  If the connecting user does not    |
|                     | have security to see them, an error will result.      |
+---------------------+-------------------------------------------------------+
| --include-sequence-\| When describing a sequence include its current value. |
| values              |                                                       |
+---------------------+-------------------------------------------------------+
| --include-view-\    | Include column names when describing views.           |
| columns             |                                                       |
+---------------------+-------------------------------------------------------+
| --include-roles     | Include all roles that the schema(s) have been        |
|                     | granted  "with admin option."                         |
+---------------------+-------------------------------------------------------+
| --include-users     | Include a create user statement for each schema.      |
+---------------------+-------------------------------------------------------+
| --include-contexts  | Include contexts in output which reference packages   |
|                     | owned by the schema(s).                               |
+---------------------+-------------------------------------------------------+
| --split-related     | When describing objects do not include related        |
|                     | objects in the same file as their parent; instead,    |
|                     | put each related object in its own file.              |
+---------------------+-------------------------------------------------------+
| --name=NAME         | Include the objects in the schema(s) with the         |
|                     | specified name(s).  This option may be specified      |
|                     | multiple times and/or multiple names may be specified |
|                     | separated by commas.                                  |
+---------------------+-------------------------------------------------------+
| --name-file=FILE    | This option behaves the same as --name except that    |
|                     | the argument to the option is the name of a file      |
|                     | containing the names of schemas to export, one per    |
|                     | line.                                                 |
+---------------------+-------------------------------------------------------+
| --only-types=TYPES  | Only include objects of the specified type(s).  This  |
|                     | may be specified multiple times and/or the types may  |
|                     | be separated by commas.  The supported types are those|
|                     | valid for user_objects, all_objects, or dba_objects.  |
|                     | If the type contains blanks you can either enclose    |
|                     | the type within quotation marks or replace the blanks |
|                     | with underscores.                                     |
+---------------------+-------------------------------------------------------+
| --only-if=CLAUSE    | Only include objects which match the specified        |
|                     | criteria.  The criteria is added to the where clause  |
|                     | of the select statement that is executed against      |
|                     | user_objects, all_objects, or dba_objects.            |
+---------------------+-------------------------------------------------------+
| --max-long-size=N   | Specify the maximum length of a view or trigger. This |
|                     | defaults to 128K.                                     |
+---------------------+-------------------------------------------------------+
| --as-of-scn=SCN     | All queries performed to retrieve information about   |
|                     | objects will use a flashback query to the specified   |
|                     | system change number.                                 |
+---------------------+-------------------------------------------------------+
| --as-of-timestamp=TS| All queries performed to retrieve information about   |
|                     | objects will use a flashback query to the specified   |
|                     | timestamp expression.                                 |
+---------------------+-------------------------------------------------------+
| --base-dir=DIR      | Use this directory as the base where the extract is   |
|                     | to be done rather than the default of the current     |
|                     | directory.                                            |
+---------------------+-------------------------------------------------------+
| --suppress-owner-dir| When creating the directories to put the object in,   |
|                     | do not include the schema name in the path.           |
+---------------------+-------------------------------------------------------+
| --log-file=         | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-level=        | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-prefix=       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+


---------
ExportXML
---------

This utility is used to export data from the database in an XML format.

Usage
=====

ExportXML [options] FILENAME SOURCE

When you run ExportXML it will connect to the database and export the data from
the table or view for the specified schema into the specified file.

Arguments
=========

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| FILENAME            | Name of the file in which the output will be placed.  |
|                     | If omitted or specified as '-' the output will be     |
|                     | shown on the screen (stdout).                         |
+---------------------+-------------------------------------------------------+
| SOURCE              | Name of the table or view to be exported as XML.      |
|                     | This may be qualified by a schema.                    |
+---------------------+-------------------------------------------------------+

Options
=======

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| -t, --traceback     | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --show-banner       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --version           | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| -h, --help          | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --schema=SCHEMA     | Use this to connect to the database and not the       |
|                     | environment variable ORA_USERID.  Note: If this (or   |
|                     | ORA_USERID) does not contain the password, it will be |
|                     | prompted for.                                         |
+---------------------+-------------------------------------------------------+
| --array-size=N      | This is the number of rows that will be read from the |
|                     | database at one time.  It is recommended to set this  |
|                     | to as large a value as possible without incurring     |
|                     | paging.                                               |
+---------------------+-------------------------------------------------------+
| --report-point=N    | Display a message every N rows processed.  If not     |
|                     | specified, no progress messages will be issued.       |
+---------------------+-------------------------------------------------------+
| --set-role=ROLE     | Enable this role after connecting to the database and |
|                     | prior to executing any SQL on that database.          |
+---------------------+-------------------------------------------------------+
| --date-format=FORMAT| This is the format that is applied when exporting     |
|                     | dates.  The allowable options match those of the      |
|                     | C/C++ strptime routine and default to                 |
|                     | ‘%Y-%m-%d %H:%M:%S’.                                  |
+---------------------+-------------------------------------------------------+
| --sort-by=STR       | Append an "order by" clause with this value to the    |
|                     | query.                                                |
+---------------------+-------------------------------------------------------+
| --log-file=         | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-level=        | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-prefix=       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+


-------------
GeneratePatch
-------------

This utility is used to create a script that will upgrade one set of objects to
match another set.

Usage
=====

GeneratePatch [options] FROMDIR TODIR

Before you run GeneratePatch, you should do an ExportObjects on the source and
target databases into separate directories.  You then run GeneratePatch
specifying these two directories and a script will be generated to stdout.  You
should redirect the output to a file using the standard redirection character
'>'.

Arguments
=========

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| FROMDIR             | Name of the directory containing the source objects.  |
+---------------------+-------------------------------------------------------+
| TODIR               | Name of the directory containing the target objects   |
|                     | that need to be transformed to match the source       |
|                     | objects.                                              |
+---------------------+-------------------------------------------------------+

Options
=======

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| -t, --traceback     | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --show-banner       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --version           | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| -h, --help          | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --schema=SCHEMA     | Use this to connect to the database and not the       |
|                     | environment variable ORA_USERID.  Note: If this (or   |
|                     | ORA_USERID) does not contain the password, it will be |
|                     | prompted for.                                         |
+---------------------+-------------------------------------------------------+
| --no-comments       | Do not include object comments in the description.    |
+---------------------+-------------------------------------------------------+
| --no-grants         | Do not include the grants in the description.         |
+---------------------+-------------------------------------------------------+
| --use-dba-views     | Use dba_xxx views for retrieving the information      |
|                     | about the object.  If the connecting user does not    |
|                     | have security to see them, an error will result.      |
+---------------------+-------------------------------------------------------+
| --log-file=         | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-level=        | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-prefix=       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+


------------
GenerateView
------------

This utility is used to create a view that matches the columns of each table in
a schema.

Usage
=====

GenerateView [options]

Options
=======

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| -t, --traceback     | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --show-banner       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --version           | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| -h, --help          | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --schema=SCHEMA     | Use this to connect to the database and not the       |
|                     | environment variable ORA_USERID.  Note: If this (or   |
|                     | ORA_USERID) does not contain the password, it will be |
|                     | prompted for.                                         |
+---------------------+-------------------------------------------------------+
| --add-prefix=STR    | Add the string prefix to the start of the name of     |
|                     | each table when generating the name of the view.      |
+---------------------+-------------------------------------------------------+
| --remove-prefix=STR | Remove the string prefix from the start of the name   |
|                     | of each table when generating the name of the view.   |
|                     | If the table does not have the string prefix at the   |
|                     | start of its name, nothing is done to the name when   |
|                     | generating the name for the view.                     |
+---------------------+-------------------------------------------------------+
| --add-suffix=STR    | Add the string suffix to the end of the name of each  |
|                     | table when generating the name of the view.           |
+---------------------+-------------------------------------------------------+
| --remove-suffix=STR | Remove the string suffix from the end of the name of  |
|                     | each table when generating the name of the view.  If  |
|                     | the table does not have the string suffix at the end  |
|                     | of its name, nothing is done to the name when         |
|                     | generating the name for the view.                     |
+---------------------+-------------------------------------------------------+
| --include-tables=\  | Only generate views for the tables specified in the   |
| LIST                | list.  This option may be specified multiple times    |
|                     | and/or multiple tables may be specified separated by  |
|                     | commas.                                               |
+---------------------+-------------------------------------------------------+
| --exclude-tables=\  | Generate views for all tables for the schema except   |
| LIST                | for the tables specified in the list.  This option    |
|                     | may be specified multiple times and/or multiple       |
|                     | tables may be specified separated by commas.          |
+---------------------+-------------------------------------------------------+
| --log-file=         | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-level=        | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-prefix=       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+


------------
ImportColumn
------------

This utility is used to load a column in an Oracle table from the contents of
the specified file.

Usage
=====

ImportColumn [options] STATEMENT FILENAME [VALUES ...]

When you run ImportColumn it will connect to the database and load the
specified column with the contents of the specified file.

Arguments
=========

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| STATEMENT           | Specifies the column to be imported.  This is either  |
|                     | a SQL statement to execute, the name of the file      |
|                     | containing the statement to execute if the            |
|                     | --statement-in-file option is specified, or the name  |
|                     | of the column which is to be imported in the form     |
|                     | [Owner.]Table.Column (in this case insert and update  |
|                     | statements will be fabricated using the VALUES        |
|                     | argument for the insert items or where clause).       |
+---------------------+-------------------------------------------------------+
| FILENAME            | The name of the file from which the column is to be   |
|                     | loaded.                                               |
+---------------------+-------------------------------------------------------+
| VALUES              | This is a space separated list of name=VALUE which    |
|                     | will be used for bind variables if a SQL statement is |
|                     | specified or will be used in the where clause if      |
|                     | [Owner.]Table.Column is specified for STATEMENT.      |
+---------------------+-------------------------------------------------------+

Options
=======

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| -t, --traceback     | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --show-banner       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --version           | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| -h, --help          | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --schema=SCHEMA     | Use this to connect to the database and not the       |
|                     | environment variable ORA_USERID.  Note: If this (or   |
|                     | ORA_USERID) does not contain the password, it will be |
|                     | prompted for.                                         |
+---------------------+-------------------------------------------------------+
| --binary            | The column to be imported is a BLOB or LONG RAW and   |
|                     | not a CLOB or LONG.                                   |
+---------------------+-------------------------------------------------------+
| --statement-in-file | The argument STATEMENT is to be taken as the name of  |
|                     | a file from which to get the SQL statement to execute.|
+---------------------+-------------------------------------------------------+
| --log-file=         | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-level=        | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-prefix=       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+


-----------
ImportData
-----------

This utility is used to import data into the database that has been exported
via ExportData.  ExportData and ImportData are an alternative to Oracle’s
import and export utilities for the movement of data.  These utilities do not
import or export object definitions, however.

Usage
=====

ImportData [options] FILENAME

When you run ImportData it will connect to the database and read from the
specified file and import the data from it into existing tables in the
database.

Arguments
=========

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| FILENAME            | The name of the file that ImportData will read.  To   |
|                     | use stdin specify as '-'.                             |
+---------------------+-------------------------------------------------------+

Options
=======

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| -t, --traceback     | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --show-banner       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --version           | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| -h, --help          | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --schema=SCHEMA     | Use this to connect to the database and not the       |
|                     | environment variable ORA_USERID.  Note: If this (or   |
|                     | ORA_USERID) does not contain the password, it will be |
|                     | prompted for.                                         |
+---------------------+-------------------------------------------------------+
| --array-size=N      | This is the number of rows that will be read from the |
|                     | database at one time.  It is recommended to set this  |
|                     | to as large a value as possible without incurring     |
|                     | paging.                                               |
+---------------------+-------------------------------------------------------+
| --commit-point=N    | Issue a commit every N rows processed.  If not        |
|                     | specified, a commit will only be issued after all the |
|                     | data has been imported.                               |
+---------------------+-------------------------------------------------------+
| --report-point=N    | Display a message every N rows processed.  If not     |
|                     | specified, no progress messages will be issued for    |
|                     | each table imported.                                  |
+---------------------+-------------------------------------------------------+
| --set-role=ROLE     | Enable this role after connecting to the database and |
|                     | prior to executing any SQL on that database.          |
+---------------------+-------------------------------------------------------+
| --include-tables=\  | Only import the tables specified in the list.  This   |
| LIST                | option may be specified multiple times and/or         |
|                     | multiple tables may be specified separated by commas. |
+---------------------+-------------------------------------------------------+
| --exclude-tables=\  | Import all tables in the file except for the tables   |
| LIST                | specified in the list.  This option may be specified  |
|                     | multiple times and/or multiple tables may be          |
|                     | specified separated by commas.                        |
+---------------------+-------------------------------------------------------+
| --log-file=         | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-level=        | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-prefix=       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+


---------
ImportXML
---------

This utility is used to import XML format data into the database.

Usage
=====

ImportXML [options] FILENAME TABLENAME

When you run ImportXML it will connect to the database and import the data from
the specified file into the table or view in the specified schema.

Arguments
=========

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| FILENAME            | Name of the file which is to be imported.  If         |
|                     | specified as '-' then the input will be via stdin.    |
+---------------------+-------------------------------------------------------+
| TABLENAME           | Name of the table or view to be imported as XML.      |
|                     | This may be qualified by a schema.                    |
+---------------------+-------------------------------------------------------+

Options
=======

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| -t, --traceback     | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --show-banner       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --version           | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| -h, --help          | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --schema=SCHEMA     | Use this to connect to the database and not the       |
|                     | environment variable ORA_USERID.  Note: If this (or   |
|                     | ORA_USERID) does not contain the password, it will be |
|                     | prompted for.                                         |
+---------------------+-------------------------------------------------------+
| --array-size=N      | This is the number of rows that will be read from the |
|                     | database at one time.  It is recommended to set this  |
|                     | to as large a value as possible without incurring     |
|                     | paging.                                               |
+---------------------+-------------------------------------------------------+
| --commit-point=N    | Issue a commit every N rows processed.  If not        |
|                     | specified, a commit will only be issued after the     |
|                     | entire file is imported.                              |
+---------------------+-------------------------------------------------------+
| --report-point=N    | Display a message every N rows processed.  If not     |
|                     | specified, no progress messages will be issued.       |
+---------------------+-------------------------------------------------------+
| --set-role=ROLE     | Enable this role after connecting to the database and |
|                     | prior to executing any SQL on that database.          |
+---------------------+-------------------------------------------------------+
| --date-format=FORMAT| This is the format that is applied when importing     |
|                     | dates.  The allowable options match those of the      |
|                     | C/C++ strptime routine and default to                 |
|                     | ‘%Y-%m-%d %H:%M:%S’.                                  |
+---------------------+-------------------------------------------------------+
| --log-file=         | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-level=        | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-prefix=       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+


-------
PatchDB  
-------

This utility is used to modify the contents of a database using scripts with
error checking. Currently all that is supported is SQL scripts which consist of
any number of valid Oracle statements. Blank lines are preserved for all PL/SQL
sources unlike SQL*Plus.

Usage
=====

PatchDB [options] FILENAME

When you run PatchDB, the statements in the specified file are executed in
order with error checking taking place after each statement is executed. The
file may contain any valid Oracle statements (DDL, DML, or PL/SQL blocks).

Arguments
=========

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| FILENAME            | The name of the file containing the statements to     |
|                     | execute or '-' to indicate that the statements are to |
|                     | be read from stdin.  NOTE: if the file specified does |
|                     | not exist and does not have the extension ".sql",     |
|                     | then an attempt will be made to read from the file    |
|                     | after appending the extension ".sql".                 |
+---------------------+-------------------------------------------------------+

Options
=======

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| -t, --traceback     | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --show-banner       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --version           | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| -h, --help          | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --schema=SCHEMA     | Use this to connect to the database and not the       |
|                     | environment variable ORA_USERID.  Note: If this (or   |
|                     | ORA_USERID) does not contain the password, it will be |
|                     | prompted for.                                         |
+---------------------+-------------------------------------------------------+
| --on-error-continue | If an error is encountered continue processing the    |
|                     | script.                                               |
+---------------------+-------------------------------------------------------+
| --with-recompile    | After the script is finished do a recompile of all    |
|                     | the invalid objects in the current schema.            |
+---------------------+-------------------------------------------------------+
| --on-recompile-\    | If an error is encountered during recompile continue  |
| error-continue      | to recompile all other invalid objects.               |
+---------------------+-------------------------------------------------------+
| --log-file=         | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-level=        | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-prefix=       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+


------------
RebuildTable
------------

This utility is used to generate the DDL necessary to recreate a table
including all indexes, foreign keys and referencing foreign keys.

Usage
=====

RebuildTable [options] TABLENAME

When you run RebuildTable it will generate the statements necessary to rebuild
the specified table with the specified options.  The output of RebuildTable
should be redirected to a file using the standard redirection character '>'.

Arguments
=========

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| TABLENAME           | Name of the table that you wish to rebuild.  This may |
|                     | be qualified by a schema.  However, unless DBA views  |
|                     | are used, foreign keys from other schemas that refer  |
|                     | to this table may not be properly included.           |
+---------------------+-------------------------------------------------------+

Options
=======

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| -t, --traceback     | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --show-banner       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --version           | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| -h, --help          | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --schema=SCHEMA     | Use this to connect to the database and not the       |
|                     | environment variable ORA_USERID.  Note: If this (or   |
|                     | ORA_USERID) does not contain the password, it will be |
|                     | prompted for.                                         |
+---------------------+-------------------------------------------------------+
| --no-comments       | Do not include object comments in the description.    |
+---------------------+-------------------------------------------------------+
| --no-grants         | Do not include the grants in the description.         |
+---------------------+-------------------------------------------------------+
| --no-related        | Do not include related objects in the description     |
|                     | (e.g. the body of a package, the indexes and          |
|                     | constraints for a table, etc.).                       |
+---------------------+-------------------------------------------------------+
| --no-triggers       | Do not include related triggers in the description.   |
+---------------------+-------------------------------------------------------+
| --dont-merge-grants | Show each grant as a separate statement.  In the case |
|                     | where multiple privileges are granted to the same     |
|                     | user/role, each one will be a separate statement.     |
+---------------------+-------------------------------------------------------+
| --default-tablespace| Do not include tablespace specifications.             |
+---------------------+-------------------------------------------------------+
| --default-storage   | Do not include storage specifications.                |
+---------------------+-------------------------------------------------------+
| --use-dba-views     | Use dba_xxx views for retrieving the information      |
|                     | about the object.  If the connecting user does not    |
|                     | have security to see them, an error will result.      |
+---------------------+-------------------------------------------------------+
| --max-long-size=N   | Specify the maximum length of a view or trigger. This |
|                     | defaults to 128K.                                     |
+---------------------+-------------------------------------------------------+
| --with-copydata     | The script will use the CopyData tool to move the     |
|                     | data from the current table to the rebuilt table;     |
|                     | otherwise an insert statement will be generated.      |
+---------------------+-------------------------------------------------------+
| --log-file=         | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-level=        | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-prefix=       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+


---------------
RecompileSource
---------------

This utility is used to recompile invalid objects in a database.

Usage
=====

RecompileSource [options]

When you run RecompileSource, it will connect to the database, find all invalid
objects (optionally filtering on owner), and proceed to recompile them
iteratively until a complete pass shows no changes in the list of invalid
objects.

Options
=======

+---------------------+-------------------------------------------------------+
| Name                | Description                                           |
+---------------------+-------------------------------------------------------+
| -t, --traceback     | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --show-banner       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --version           | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| -h, --help          | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --schema=SCHEMA     | Use this to connect to the database and not the       |
|                     | environment variable ORA_USERID.  Note: If this (or   |
|                     | ORA_USERID) does not contain the password, it will be |
|                     | prompted for.                                         |
+---------------------+-------------------------------------------------------+
| --on-error-continue | If an error is encountered during the recompile of an |
|                     | object continue processing with the next object.      |
+---------------------+-------------------------------------------------------+
| --connect-as-owner  | When recompiling an object, establish a connection to |
|                     | the database as the owner of that object, using the   |
|                     | password of the initially established connection as   |
|                     | the password for the owning schema.                   |
+---------------------+-------------------------------------------------------+
| --include=LIST      | Only recompile invalid objects in the specified       |
|                     | schemas.  This option may be specified multiple times |
|                     | and/or multiple schemas may be specified separated by |
|                     | commas.                                               |
+---------------------+-------------------------------------------------------+
| --include-file=FILE | As --include except that the list of schemas is found |
|                     | in the specified file.                                |
+---------------------+-------------------------------------------------------+
| --exclude=LIST      | Do not recompile invalid objects in the specified     |
|                     | schemas.  This option may be specified multiple times |
|                     | and/or multiple schemas may be specified separated by |
|                     | commas.                                               |
+---------------------+-------------------------------------------------------+
| --log-file=         | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-level=        | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+
| --log-prefix=       | see `Common Options`_                                 |
+---------------------+-------------------------------------------------------+

