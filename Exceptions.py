"""
Exceptions used in cx_OracleTools.
"""

import cx_Exceptions

class InvalidColumnName(cx_Exceptions.BaseException):
    message = "Column name must be of the form [Owner.]Table.Column"


class ObjectNotATable(cx_Exceptions.BaseException):
    message = "Object %(name)s is not a table."

