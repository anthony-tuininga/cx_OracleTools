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

The following options are common to most of the tools:

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
|                     | - “select col1,col2 from common.sourcetbl”            |
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
| --report-point=N    | Display a message every n rows processed.  If not     |
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

