"""
Exceptions used in cx_OracleTools.
"""

import cx_Exceptions

class DestinationTableNotSpecified(cx_Exceptions.BaseException):
    message = "A destination table must be specified when a source query " \
              "is used."


class InvalidColumnName(cx_Exceptions.BaseException):
    message = "Column name must be of the form [Owner.]Table.Column"


class InvalidTableName(cx_Exceptions.BaseException):
    message = "Invalid table name."


class KeyColumnNotInSourceQuery(cx_Exceptions.BaseException):
    message = "Key column %(name)s not in source query."


class NoPrimaryOrUniqueConstraintOnTable(cx_Exceptions.BaseException):
    message = "No primary or unique constraint found on table."


class NotAllColumnsMatchByName(cx_Exceptions.BaseException):
    message = "All source columns or all destination columns must match by " \
              "name."


class ObjectNotATable(cx_Exceptions.BaseException):
    message = "Object %(name)s is not a table."


class SourceDirectoryNotFound(cx_Exceptions.BaseException):
    message = "Source (from directory) not found."


class SourceTableNotFound(cx_Exceptions.BaseException):
    message = "Source table %(tableName)s not found."


class TargetDirectoryNotFound(cx_Exceptions.BaseException):
    message = "Target (to directory) not found."


class TargetTableNotFound(cx_Exceptions.BaseException):
    message = "Target table %(tableName)s not found."

