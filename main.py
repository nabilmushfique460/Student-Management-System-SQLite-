import sys
import sqlite3

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidget,
                             QTableWidgetItem, QDialog, QVBoxLayout,
                             QLineEdit, QComboBox, QPushButton, QMessageBox)


# --- Ensure database and table exist to prevent crashes ---
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(600, 400)

        # Menu bar
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")

        # Add Student Action
        add_student_action = QAction("Add Student", self)
        add_student_action.triggered.connect(self.insert_student)
        file_menu_item.addAction(add_student_action)

        # About Action
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)

        # Main Table Setup
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.setCentralWidget(self.table)

    def load_data(self):
        try:
            connection = sqlite3.connect("database.db")
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
            connection = sqlite3.connect("database.db")
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


# Run the setup script to ensure DB exists
create_database_if_not_exists()

# Initialize and run the App
app = QApplication(sys.argv)
student_management_system = MainWindow()
student_management_system.show()
student_management_system.load_data()
sys.exit(app.exec())