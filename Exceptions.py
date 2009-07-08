"""
Exceptions used in cx_OracleTools.
"""

import cx_Exceptions

class InvalidColumnName(cx_Exceptions.BaseException):
    message = "Column name must be of the form [Owner.]Table.Column"


class InvalidTableName(cx_Exceptions.BaseException):
    message = "Invalid table name."


class ObjectNotATable(cx_Exceptions.BaseException):
    message = "Object %(name)s is not a table."


class SourceDirectoryNotFound(cx_Exceptions.BaseException):
    message = "Source (from directory) not found."


class TargetDirectoryNotFound(cx_Exceptions.BaseException):
    message = "Target (to directory) not found."

