import sys
import sqlite3
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")

        add_student_action = QAction("Add Student", self)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.setCentralWidget(self.table)

    def load_data(self):
        connection = sqlite3.connect("database.db")
        result = connection.execute("SELECT * FROM students")

        # Reset table to 0 rows before loading data
        # (prevents duplicating data if you call this function multiple times)
        self.table.setRowCount(0)

        # Loop through the database results and insert them into the GUI table
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                # QTableWidgetItem requires the data to be a string
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        connection.close()


app = QApplication(sys.argv)
student_management_system = MainWindow()
student_management_system.show()
student_management_system.load_data()
sys.exit(app.exec())