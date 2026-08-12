import sys
import sqlite3
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon, QColor
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidget,
                             QTableWidgetItem, QDialog, QVBoxLayout,
                             QLineEdit, QComboBox, QPushButton, QMessageBox,
                             QToolBar, QStatusBar, QLabel, QGridLayout)


# Ensure database and table exist to prevent crashes
def create_database_if_not_exists():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            course TEXT NOT NULL,
            mobile TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()


class DatabaseConnection:
    def __init__(self, database_file="database.db"):
        self.database_file = database_file

    def connect(self):
        connection = sqlite3.connect(self.database_file)
        return connection





class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

        # Menu bar
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")


        # Add Student Action
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert_student)
        file_menu_item.addAction(add_student_action)

        # About Action
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        # Search Action
        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        # Main Table Setup
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create toolbar and add toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)


        # Create status bar and add status bar elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)





    def load_data(self):
        try:
            connection = DatabaseConnection().connect()
            result = connection.execute("SELECT * FROM students")

            # Reset table before loading data
            self.table.setRowCount(0)

            for row_number, row_data in enumerate(result):
                self.table.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

            connection.close()
        except sqlite3.Error as error:
            QMessageBox.critical(self, "Database Error", f"Failed to load data:\n{error}")

    def insert_student(self):
        dialog = InsertDialog(self)  # Pass self as parent to center the dialog
        dialog.exec()
        # Refresh the table so the new student shows up immediately
        self.load_data()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This app was created during the course "The Python Mega Course".
        Feel free to modify and use this app however you'd like.
        """

        self.setText(content)


class EditDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get student name from selected row
        index = main_window.table.currentRow()
        student_name = main_window.table.item(index, 1).text()

        # Get id from selected row
        self.student_id = main_window.table.item(index, 0).text()

        # Student Name
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Course Combo Box
        course_name = main_window.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Math", "Astronomy", "Biology", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # Mobile Number
        mobile = main_window.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add a submit Button
        submit_button = QPushButton("Update")
        submit_button.clicked.connect(self.update_student)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def update_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? ""WHERE id = ?",
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.mobile.text(), self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()




class DeleteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)

    def delete_student(self):
        # Get selected row index and student id
        index = main_window.table.currentRow()
        student_id = main_window.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = ?", (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

        self.close()

        conformation_widget = QMessageBox()
        conformation_widget.setWindowTitle("Success")
        conformation_widget.setText("The record was deleted successfully")
        conformation_widget.exec()






class InsertDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Student Name
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Course Combo Box
        self.course_name = QComboBox()
        courses = ["Math", "Astronomy", "Biology", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Mobile Number
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Register Button
        submit_button = QPushButton("Register")
        submit_button.clicked.connect(self.add_student)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()

        # Prevent empty submissions
        if not name or not mobile:
            QMessageBox.warning(self, "Input Error", "Name and Mobile fields cannot be empty!")
            return

        try:
            connection = DatabaseConnection().connect()
            cursor = connection.cursor()

            cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
                           (name, course, mobile))

            connection.commit()
            cursor.close()
            connection.close()

            # Close the dialog window after successful save
            self.accept()

        except sqlite3.Error as error:
            # Show a pop-up with the exact SQL error if something goes wrong
            QMessageBox.critical(self, "Database Error", f"Failed to add student:\n{error}")
        except Exception as error:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred:\n{error}")


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(150)

        layout = QVBoxLayout()
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()
        main_window.table.clearSelection()

        # Reset all rows to a standard white background before a new search
        for row in range(main_window.table.rowCount()):
            for col in range(main_window.table.columnCount()):
                item = main_window.table.item(row, col)
                if item:
                    item.setBackground(QColor("white"))

        # Find matching items
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchContains)

        if items:
            for item in items:
                target_row = item.row()
                main_window.table.selectRow(target_row)
                main_window.cell_clicked()

                # Make every cell in the found row Light Blue
                for col in range(main_window.table.columnCount()):
                    # You can change "lightblue" to "blue" or "#0078D7" (Hex code)
                    main_window.table.item(target_row, col).setBackground(QColor("lightblue"))

            self.accept()
        else:
            QMessageBox.information(self, "Not Found", f"No student found with the name: {name}")


# Run the setup script to ensure DB exists
create_database_if_not_exists()

# Initialize and run the App
app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())