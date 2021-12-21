import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc


class InvoiceForm(qtw.QWidget):

    submitted = qtc.pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setLayout(qtw.QFormLayout())
        
        # input window
        self.inputs = {}
        self.inputs['Employee Name'] = qtw.QLineEdit()
        self.inputs['Employee Address'] = qtw.QPlainTextEdit()

        self.inputs['Employee Number'] = qtw.QLineEdit()
        self.inputs['Pay Method'] = qtw.QComboBox()
        self.inputs['Pay Method'].addItems(["Weekly", "Bi-weekly", "Monthly"])
        self.inputs['Pay Date'] = qtw.QDateEdit(
            date=qtc.QDate.currentDate(), calendarPopup=True)
        self.inputs['Tax Code'] = qtw.QLineEdit()
        self.inputs['Ni Number'] = qtw.QLineEdit()

        self.inputs['Account No'] = qtw.QLineEdit()
        self.inputs['Account No'].setValidator(qtg.QIntValidator())
        self.inputs['Sort Code'] = qtw.QLineEdit()
        for label, widget in self.inputs.items():
            self.layout().addRow(label, widget)

        # input window bottom table for calculating pay before deductions
        self.line_items = qtw.QTableWidget(
            rowCount=4, columnCount=3)
        self.line_items.setHorizontalHeaderLabels(
            ['Job', 'Rate', 'Hours'])
        self.line_items.horizontalHeader().setSectionResizeMode(
            qtw.QHeaderView.Stretch)
        self.layout().addRow(self.line_items)
        for row in range(self.line_items.rowCount()):
            for col in range(self.line_items.columnCount()):
                if col > 0:
                    w = qtw.QSpinBox(minimum=0)
                    self.line_items.setCellWidget(row, col, w)

        # input window bottom table for deductions
        self.line_items2 = qtw.QTableWidget(
            rowCount=4, columnCount=2)
        self.line_items2.setHorizontalHeaderLabels(
            ['Deductions', 'Amount'])
        self.line_items2.horizontalHeader().setSectionResizeMode(
            qtw.QHeaderView.Stretch)
        self.layout().addRow(self.line_items2)
        for row1 in range(self.line_items2.rowCount()):
            for col1 in range(self.line_items2.columnCount()):
                if col1 > 0:
                    w1 = qtw.QSpinBox(minimum=0, maximum=1000)
                    self.line_items2.setCellWidget(row1, col1, w1)

        # submit button settings
        submit = qtw.QPushButton('Create Payslip', clicked=self.on_submit)
        submit.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        submit.setStyleSheet("*{background-color: darkGrey ;" 
                             "border-style: outset; " 
                             "border-width: 3px;" 
                             "border-radius: 15px;" 
                             "border-color: darkRed;" 
                             "font: bold 16px;" 
                             "min-width: 10em;" 
                             "padding: 8px;}" 
                             "*:hover{background-color: darkRed;}")
        self.layout().addRow(submit)

    # input data getting converted to output data on submit
    def on_submit(self):
        data = {
            'e_name': self.inputs['Employee Name'].text(),
            'e_addr': self.inputs['Employee Address'].toPlainText(),
            'e_number': self.inputs['Employee Number'].text(),
            'i_terms': self.inputs['Pay Method'].currentText(),
            'i_due': self.inputs['Pay Date'].date().toString(),
            'tax_code': self.inputs['Tax Code'].text(),
            'ni_number': self.inputs['Ni Number'].text(),
            'account_no': self.inputs['Account No'].text(),
            'sort_code': self.inputs['Sort Code'].text(),   
        }
        data['line_items'] = []
        for row in range(self.line_items.rowCount()):
            if not self.line_items.item(row, 0):
                continue
            job = self.line_items.item(row, 0).text()
            rate = self.line_items.cellWidget(row, 1).value()
            hours = self.line_items.cellWidget(row, 2).value()
            total = rate * hours
            row_data = [job, rate, hours, total]
            if any(row_data):
                data['line_items'].append(row_data)
        data['total_due'] = sum(x[3] for x in data['line_items'])

        data['line_items2'] = []
        for row1 in range(self.line_items2.rowCount()):
            if not self.line_items2.item(row1, 0):
                continue
            deductions = self.line_items2.item(row1, 0).text()
            amount = self.line_items2.cellWidget(row1, 1).value()
            total = amount
            row_data = [deductions, amount]
            if any(row_data):
                data['line_items2'].append(row_data)
        data['total_due2'] = sum(x[1] for x in data['line_items2'])
        data['netto_pay'] = data['total_due'] - data['total_due2']
        self.submitted.emit(data)

 
class InvoiceView(qtw.QTextEdit):
    
    # generated payslip settings
    doc_width = 800
    doc_height = 800

    def __init__(self):
        super().__init__(readOnly=True)
        self.setFixedSize(qtc.QSize(self.doc_width, self.doc_height))

    def build_invoice(self, data):
        # output data location on screen settings
        document = qtg.QTextDocument()
        self.setDocument(document)
        document.setPageSize(qtc.QSizeF(self.doc_width, self.doc_height))
        cursor = qtg.QTextCursor(document)
        root = document.rootFrame()
        cursor.setPosition(root.lastPosition())
       
        cursor.setPosition(root.lastPosition())
        cust_addr_frame_fmt = qtg.QTextFrameFormat()
        cust_addr_frame_fmt.setWidth(self.doc_width * .3)
        cust_addr_frame_fmt.setPosition(qtg.QTextFrameFormat.FloatLeft)
        cust_addr_frame = cursor.insertFrame(cust_addr_frame_fmt)

        cursor.setPosition(root.lastPosition())
        terms_frame_fmt = qtg.QTextFrameFormat()
        terms_frame_fmt.setWidth(self.doc_width * .6)
        terms_frame_fmt.setPosition(qtg.QTextFrameFormat.FloatLeft)
        terms_frame = cursor.insertFrame(terms_frame_fmt)

        cursor.setPosition(3)
        terms_frame_fmt2 = qtg.QTextFrameFormat()
        terms_frame_fmt2.setWidth(self.doc_width * .3)
        terms_frame_fmt2.setPosition(qtg.QTextFrameFormat.FloatRight)
        terms_frame2 = cursor.insertFrame(terms_frame_fmt2)

        cursor.setPosition(root.lastPosition())
        line_items_frame_fmt = qtg.QTextFrameFormat()
        line_items_frame_fmt.setMargin(25)
        line_items_frame = cursor.insertFrame(line_items_frame_fmt)

        cursor.setPosition(9)
        line_items_frame_fmt2 = qtg.QTextFrameFormat()
        line_items_frame_fmt2.setWidth(self.doc_width * .53)
        line_items_frame_fmt2.setPosition(qtg.QTextFrameFormat.FloatRight)
        line_items_frame2 = cursor.insertFrame(line_items_frame_fmt2)

        # font settings
        std_format = qtg.QTextCharFormat()

        label_format = qtg.QTextCharFormat()
        label_format.setFont(qtg.QFont('Sans', 10, qtg.QFont.Bold))

        cursor.setPosition(cust_addr_frame.lastPosition())

        # text spacing settings
        address_format = qtg.QTextBlockFormat()
        address_format.setLineHeight(
            150, qtg.QTextBlockFormat.ProportionalHeight)
        address_format.setAlignment(qtc.Qt.AlignLeft)
        address_format.setLeftMargin(25)

        # employee name, address
        cursor.insertBlock(address_format)
        cursor.insertText('Employee:', label_format)
        cursor.insertBlock(address_format)
        cursor.insertText(data['e_name'], std_format)
        cursor.insertBlock(address_format)
        cursor.insertText(data['e_addr'])

        
        cursor.setPosition(terms_frame.lastPosition())
        cursor.insertList(qtg.QTextListFormat.ListSquare)   

        # employee data information
        term_items = (
            f'<b>Employee No.:</b> {data["e_number"]}',
            f'<b>Pay date:</b> {data["i_due"]}',
            f'<b>Pay method:</b> {data["i_terms"]}',
            f'<b>Tax code:</b> {data["tax_code"]}',
            f'<b>Ni number:</b> {data["ni_number"]}'
        )

        for i, item in enumerate(term_items):
            if i > 0:
                cursor.insertBlock()
            cursor.insertHtml(item)

        cursor.setPosition(terms_frame2.lastPosition())
        cursor.insertList(qtg.QTextListFormat.ListCircle)
        
        # account data information
        term_items2 = (
            f'<b>Account No.:</b> {data["account_no"]}',
            f'<b>Sort Code:</b> {data["sort_code"]}',    
        )

        for i, item in enumerate(term_items2):
            if i > 0:
                cursor.insertBlock()
            cursor.insertHtml(item)

        # pay and allowances table
        table_format = qtg.QTextTableFormat()
        table_format.setHeaderRowCount(1)
        table_format.setWidth(
            qtg.QTextLength(qtg.QTextLength.PercentageLength, 40))

        headings = ('Pay & Allowances', 'Rate', 'Hours', 'Total')
        num_rows = len(data['line_items']) + 1
        num_cols = len(headings)

        cursor.setPosition(line_items_frame.lastPosition())
        table = cursor.insertTable(num_rows, num_cols, table_format)

        for heading in headings:
            cursor.insertText(heading, label_format)
            cursor.movePosition(qtg.QTextCursor.NextCell)

        for row in data['line_items']:
            for col, value in enumerate(row):
                text = f'£{value}' if col in (1, 3) else f'{value}'
                cursor.insertText(text, std_format)
                cursor.movePosition(qtg.QTextCursor.NextCell)

        # pay and allowances table end values
        table.appendRows(1)
        cursor = table.cellAt(num_rows, 0).lastCursorPosition()
        cursor.insertText('Gross Pay', label_format)
        cursor = table.cellAt(num_rows, 3).lastCursorPosition()
        cursor.insertText(f"£{data['total_due']}", label_format)
        table.appendRows(1)
        cursor = table.cellAt(num_rows+1, 0).lastCursorPosition()
        cursor.insertText('Net Pay', label_format)
        cursor = table.cellAt(num_rows+1, 3).lastCursorPosition()
        cursor.insertText(f"£{data['netto_pay']}", label_format)

        # deductions table
        table_format = qtg.QTextTableFormat()
        table_format.setHeaderRowCount(1)
        table_format.setWidth(
            qtg.QTextLength(qtg.QTextLength.PercentageLength, 60))

        headings = ('Deductions', 'Amount')
        num_rows = len(data['line_items2']) + 1
        num_cols = len(headings)

        cursor.setPosition(line_items_frame2.lastPosition())
        table = cursor.insertTable(num_rows, num_cols, table_format)

        for heading in headings:
            cursor.insertText(heading, label_format)
            cursor.movePosition(qtg.QTextCursor.NextCell)

        for row in data['line_items2']:
            for col, value in enumerate(row):
                text = f'£{value}' if col in (1, 1) else f'{value}'
                cursor.insertText(text, std_format)
                cursor.movePosition(qtg.QTextCursor.NextCell)

        # deductions table total value
        table.appendRows(1)
        cursor = table.cellAt(num_rows, 0).lastCursorPosition()
        cursor.insertText('Total', label_format)
        cursor = table.cellAt(num_rows, 1).lastCursorPosition()
        cursor.insertText(f"£{data['total_due2']}", label_format)

        # image on top of generated payslip screen
        cursor.setPosition(0)
        cursor.insertImage('logo_payslip.png')

class MainWindow(qtw.QMainWindow):

    def __init__(self):
        super().__init__()
        # main window settings
        main = qtw.QWidget()
        main.setLayout(qtw.QHBoxLayout())
        self.setCentralWidget(main)

        # font settings
        form = InvoiceForm()
        main.layout().addWidget(form)
        heading_font = qtg.QFont('Arial', 12)
        form.setFont(heading_font)

        self.preview = InvoiceView()
        main.layout().addWidget(self.preview)

        form.submitted.connect(self.preview.build_invoice)

        app = qtw.QApplication.instance()
        palette = app.palette()

        # window colour change settings
        dotted_brush = qtg.QBrush(
            qtg.QColor('black'), qtc.Qt.SolidPattern)
        gradient = qtg.QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.2, qtg.QColor('lightGrey'))
        gradient.setColorAt(0.9, qtg.QColor('darkBlue'))
        gradient.setColorAt(1, qtg.QColor('black'))
        gradient_brush = qtg.QBrush(gradient)

        window_palette = app.palette()
        window_palette.setBrush(
            qtg.QPalette.Window,
            gradient_brush
        )
        window_palette.setBrush(
            qtg.QPalette.Active,
            qtg.QPalette.WindowText,
            dotted_brush
        )
        self.setPalette(window_palette)
        self.show()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())