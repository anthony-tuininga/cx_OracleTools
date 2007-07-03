"""Import data from an XML file into a table in an Oracle database."""

import cx_LoggingOptions
import cx_OptionParser
import cx_Oracle
import cx_OracleUtils
import cx_XML
import _strptime
import sys
import time
import xml.sax

import Options

# parse command line
parser = cx_OptionParser.OptionParser("ImportXML")
parser.AddOption(cx_OracleUtils.SchemaOption())
parser.AddOption(Options.ARRAY_SIZE)
parser.AddOption(Options.COMMIT_POINT)
parser.AddOption(Options.REPORT_POINT)
parser.AddOption(Options.SET_ROLE)
parser.AddOption(Options.DATE_FORMAT)
cx_LoggingOptions.AddOptions(parser)
parser.AddArgument("fileName", required = True,
        help = "the name of the file from which to read the data or "
               "'-' to read the exported data from stdin")
parser.AddArgument("tableName", required = True,
        help = "the name of the table into which to import the data")
options = parser.Parse()
cx_LoggingOptions.ProcessOptions(options)

# define class for managing the import
class Handler(cx_XML.Parser):

    def __init__(self, options):
        self.connection = cx_OracleUtils.Connect(options.schema,
                options.setRole)
        self.cursor = self.connection.cursor()
        if options.arraySize:
            self.cursor.arraysize = options.arraySize
        self.commitPoint = options.commitPoint
        self.reportPoint = options.reportPoint
        self.dateFormat = options.dateFormat
        self.cursor.execute("select * from %s" % options.tableName)
        self.columnIndexes = {}
        self.dateColumns = {}
        bindVars = []
        bindVarNames = []
        columnNames = []
        for item in self.cursor.description:
            name, dataType, size, internalSize, prec, scale, nullsOk = item
            if dataType == cx_Oracle.DATETIME:
                self.dateColumns[name.upper()] = None
            else:
                dataType = cx_Oracle.STRING
            self.columnIndexes[name.upper()] = len(bindVars)
            bindVars.append(self.cursor.var(dataType, size))
            columnNames.append(name)
            bindVarNames.append(":%s" % len(bindVars))
        sql = "insert into %s (%s) values (%s)" % \
                (options.tableName, ",".join(columnNames),
                 ",".join(bindVarNames))
        self.cursor.prepare(sql)
        self.cursor.setinputsizes(*bindVars)
        self.allowCustomTags = False
        self.columnValue = None
        self.rowsImported = 0

    def characters(self, data):
        if self.columnValue is not None:
            self.columnValue += data

    def endElement(self, name):
        if self.columnValue is not None:
            value = self.columnValue
            if not value:
                value = None
            name = name.upper()
            columnIndex = self.columnIndexes[name]
            if value is not None and name in self.dateColumns:
                dateValue = time.strptime(self.columnValue, self.dateFormat)
                value = cx_Oracle.Timestamp(*dateValue[:6])
            else:
                value = str(self.columnValue)
            self.row[columnIndex] = value
            self.columnValue = None
            self.allowCustomTags = True
        else:
            cx_XML.Parser.endElement(self, name)

    def end_ROW(self):
        self.rowsImported += 1
        commit = (self.commitPoint \
                and self.rowsImported % self.commitPoint == 0)
        if commit or len(self.rowsToInsert) == self.cursor.arraysize:
            self.cursor.executemany(None, self.rowsToInsert)
            self.rowsToInsert = []
            if commit:
                self.connection.commit()
        if self.reportPoint and self.rowsImported % self.reportPoint == 0:
            print "%d rows imported." % self.rowsImported
        self.allowCustomTags = False

    def end_ROWSET(self):
        if self.rowsToInsert:
            self.cursor.executemany(None, self.rowsToInsert)
        if self.commitPoint is None \
                or self.rowsImported % self.commitPoint != 0:
            self.connection.commit()
        if self.reportPoint is None \
                or self.rowsImported % self.reportPoint != 0:
            print "%d rows imported." % self.rowsImported

    def startElement(self, name, attrs):
        if self.allowCustomTags:
            self.columnValue = ""
            self.allowCustomTags = False
        else:
            cx_XML.Parser.startElement(self, name, attrs)

    def start_ROW(self, num = None):
        self.row = [None] * len(self.columnIndexes)
        self.rowsToInsert.append(self.row)
        self.allowCustomTags = True

    def start_ROWSET(self):
        self.rowsToInsert = []


# parse the XML data stream
if options.fileName == "-":
    inputFile = sys.stdin
else:
    inputFile = file(options.fileName, "r")
handler = Handler(options)
parser = xml.sax.make_parser()
parser.setContentHandler(handler)
parser.parse(inputFile)

print >> sys.stderr, "Done."

