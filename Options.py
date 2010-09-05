"""
Define common options used in describing objects.
"""

import cx_OptionParser
import os

ARRAY_SIZE = cx_OptionParser.Option("--array-size", type = "int",
        metavar = "N", help = "array size is <n> rows")

AS_OF_SCN = cx_OptionParser.Option("--as-of-scn", type="int", metavar = "SCN",
        help = "system change number to use for performing a flashback query")

AS_OF_TIMESTAMP = cx_OptionParser.Option("--as-of-timestamp", metavar = "TS",
        help = "timestamp expression to use for performing a flashback query")

BINARY = cx_OptionParser.Option("--binary", action = "store_true",
        help = "the column is a BLOB (or long raw), not a CLOB (or long)")

COMMIT_POINT = cx_OptionParser.Option("--commit-point", metavar = "N",
        type = "int",
        help = "number of rows after which a commit should take place")

DATE_FORMAT = cx_OptionParser.Option("--date-format", metavar = "FORMAT",
        default = "%Y-%m-%d %H:%M:%S",
        help = "use this format for importing/exporting date values; the "
               "format specifiers are the same as those used by the C "
               "function strptime")

DEFAULT_STORAGE = cx_OptionParser.Option("--default-storage", default = True,
        action = "store_false", dest = "wantStorage",
        help = "exclude the storage characteristics of the object")

DEFAULT_TABLESPACE = cx_OptionParser.Option("--default-tablespace",
        default = True, action = "store_false", dest = "wantTablespace",
        help = "exclude the tablespace in which the object is found")

DONT_MERGE_GRANTS = cx_OptionParser.Option("--dont-merge-grants",
        default = True, action = "store_false", dest = "mergeGrants",
        help = "do not merge the grants by grantee and privilege")

INCLUDE_CONTEXTS = cx_OptionParser.Option("--include-contexts",
        default = False, action = "store_true", dest = "includeContexts",
        help = "include contexts in output which reference packages owned by "
               "the schema")

INCLUDE_ROLES = cx_OptionParser.Option("--include-roles", default = False,
        action = "store_true", dest = "includeRoles",
        help = "include roles in output which are administered by the schema")

INCLUDE_SEQUENCE_VALUES = cx_OptionParser.Option("--include-sequence-values",
        default = False, action = "store_true", dest = "wantSequenceValues",
        help = "include sequence values")

INCLUDE_USERS = cx_OptionParser.Option("--include-users", default = False,
        action = "store_true", dest = "includeUsers",
        help = "include create user statements")

INCLUDE_VIEW_COLUMNS = cx_OptionParser.Option("--include-view-columns",
        default = False, action = "store_true", dest = "wantViewColumns",
        help = "include column names when describing views")

MAX_LONG_SIZE = cx_OptionParser.Option("--max-long-size", metavar = "N",
        type = "int", default = 128 * 1024,
        help = "max long size is <n> bytes")

NAME_ONLY = cx_OptionParser.Option("--object-name-only", default = False,
        action = "store_true", dest = "nameOnly",
        help = "export the name only, not the SQL to create the object")

NAMES = cx_OptionParser.Option("--name", default = [],
        action = "append", dest = "schemas", metavar = "NAME",
        help = "export objects found in schemas with the given names")

NAMES_FILE = cx_OptionParser.Option("--name-file", metavar = "FILE",
        help = "export objects found in schemas with the given names "
               "found in the specified file")

NO_COMMENTS = cx_OptionParser.Option("--no-comments", default = True,
        action = "store_false", dest = "wantComments",
        help = "exclude comments made on objects")

NO_GRANTS = cx_OptionParser.Option("--no-grants", default = True,
        action = "store_false", dest = "wantGrants",
        help = "exclude grants made on objects")

NO_QUOTAS = cx_OptionParser.Option("--no-quotas", default = True,
        action = "store_false", dest = "wantQuotas",
        help = "exclude quotas on tablespaces")

NO_RELATED = cx_OptionParser.Option("--no-related", default = True,
        action = "store_false", dest = "wantRelated",
        help = "exclude related objects")

NO_TRIGGERS = cx_OptionParser.Option("--no-triggers", default = True,
        action = "store_false", dest = "wantTriggers",
        help = "exclude related triggers")

ONLY_IF = cx_OptionParser.Option("--only-if", metavar = "CLAUSE",
        help = "only export objects which match the given criteria; this "
               "option is expected to form a where clause that can be "
               "executed against the view *_objects")

ONLY_TYPES = cx_OptionParser.Option("--only-types", default = [],
        action = "append", dest = "objectTypes", metavar = "TYPES",
        help = "only export objects of the given types")

REPORT_POINT = cx_OptionParser.Option("--report-point", type = "int",
        metavar = "N", help = "report point is <n> rows")

SET_ROLE = cx_OptionParser.Option("--set-role", metavar = "ROLE",
        help = "enable this <role> [identified by <password>] in the database "
               "immediately after connecting by calling dbms_session.set_role")

SHOW_FOREIGN_KEYS = cx_OptionParser.Option("--show-foreign-keys",
        default = False, action = "store_true", dest = "wantForeignKeys",
        help = "include the foreign keys referencing the object")

SHOW_SYNONYMS = cx_OptionParser.Option("--show-synonyms",
        default = False, action = "store_true", dest = "wantSynonyms",
        help = "include the synonyms referencing the object")

SPLIT_RELATED = cx_OptionParser.Option("--split-related", default = False,
        action = "store_true", dest = "splitRelated",
        help = "split related objects into separate files when exporting")

STATEMENT_IN_FILE = cx_OptionParser.Option("--statement-in-file",
        action = "store_true",
        help = "the statement argument is a file name in which to locate the "
               "statement to execute")

USE_DBA_VIEWS = cx_OptionParser.Option("--use-dba-views", default = False,
        action = "store_true", dest = "useDbaViews",
        help = "use DBA views to describe the objects")

