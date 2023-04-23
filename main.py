from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QDate, QByteArray, QBuffer, QIODevice
from PyQt5.QtGui import QPixmap, QImageReader, QImage
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel

from ui.main import Ui_MainWindow

import sys
import numpy as np



class mywindow(QtWidgets.QMainWindow):

    def init_combo_box(self):
        self.ui.comboBox.addItem("Выберите звание")
        self.ui.comboBox_2.addItem("Выберите год поступления")

        self.posts = [
            "Рядовой",
            "Сержант",
            "Майор",
            "Полковник",
            "Генерал"
        ]
        self.ui.comboBox.addItems(self.posts)


        for i in np.arange(QDate.currentDate().year(), QDate.currentDate().year()-100, -1):
            self.ui.comboBox_2.addItem(str(i))

    def set_header(self, model):
        model.setHeaderData(2, QtCore.Qt.Horizontal, "Фамилия")
        model.setHeaderData(3, QtCore.Qt.Horizontal, "Имя")
        model.setHeaderData(4, QtCore.Qt.Horizontal, "Отчество")
        model.setHeaderData(5, QtCore.Qt.Horizontal, "Звание")
        model.setHeaderData(6, QtCore.Qt.Horizontal, "Год поступления")
        model.setHeaderData(7, QtCore.Qt.Horizontal, "Зарплата (рубли)")


    def connect(self):
        self.con = QSqlDatabase.addDatabase("QSQLITE")
        self.con.setDatabaseName("soilders.sqlite")
        self.con.open()

        query = QSqlQuery(self.con)
        query.exec(" create table if not exists soldat (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,photo BLOB, l varchar(255), f varchar(255), m varchar(255), post varchar(255), year INTEGER, salary INTEGER)")

        self.soldat_model = QSqlQueryModel()
        self.soldat_model.setQuery("select * from soldat")


        self.set_header(self.soldat_model)

        self.ui.tableView.setModel(self.soldat_model)


        self.ui.tableView.setColumnHidden(0, True)
        self.ui.tableView.setColumnHidden(1, True)

        self.ui.tableView_2.setColumnHidden(0, True)
        self.ui.tableView_2.setColumnHidden(1, True)

    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ba = QByteArray()

        header = self.ui.tableView.horizontalHeader()
        #header.setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)

        self.connect()
        self.init_combo_box()

        self.ui.pushButton.clicked.connect(self.insert)
        self.ui.pushButton_2.clicked.connect(self.delete)
        self.ui.pushButton_3.clicked.connect(self.update)
        self.ui.pushButton_4.clicked.connect(self.get_photo)
        self.ui.tableView.clicked.connect(self.cell_click)

        self.ui.radioButton.toggled.connect(self.order)
        self.ui.radioButton_2.toggled.connect(self.order)
        self.ui.radioButton_3.toggled.connect(self.order)

        self.ui.pushButton_5.clicked.connect(self.find)
        self.ui.pushButton_6.clicked.connect(self.clear_gui)

    def clear_gui(self):
        self.ui.label.clear()
        self.ba = QByteArray()

        self.ui.lineEdit.clear()
        self.ui.lineEdit_2.clear()
        self.ui.lineEdit_3.clear()
        self.ui.lineEdit_4.clear()

        self.ui.comboBox.setCurrentIndex(0)
        self.ui.comboBox_2.setCurrentIndex(0)

    def empty(self):
        if (self.ui.lineEdit.text() == "") | (self.ui.lineEdit_2.text() == "") | (self.ui.lineEdit_3.text() == "") | (self.ui.lineEdit_4.text() == "") | (self.ui.comboBox.currentIndex() == 0) | (self.ui.comboBox_2.currentIndex() == 0):
            return True
        return False

    def cell_click(self, item):
        self.ba = QByteArray()
        self.ba.append(self.soldat_model.data(self.soldat_model.index(self.ui.tableView.currentIndex().row(), 1)))
        bf = QBuffer(self.ba)
        bf.open(QIODevice.ReadOnly)
        imgreader = QImageReader(bf)
        img = QImage(imgreader.read())
        pix = QPixmap(img).scaled(200,200)
        self.ui.label.setPixmap(pix)

        self.ui.lineEdit.setText(self.soldat_model.data(self.soldat_model.index(self.ui.tableView.currentIndex().row(), 2)))
        self.ui.lineEdit_2.setText(self.soldat_model.data(self.soldat_model.index(self.ui.tableView.currentIndex().row(), 3)))
        self.ui.lineEdit_3.setText(self.soldat_model.data(self.soldat_model.index(self.ui.tableView.currentIndex().row(), 4)))
        self.ui.lineEdit_4.setText(str(self.soldat_model.data(self.soldat_model.index(self.ui.tableView.currentIndex().row(), 7))))

        self.ui.comboBox.setCurrentIndex(1 + self.posts.index(str(self.soldat_model.data(self.soldat_model.index(self.ui.tableView.currentIndex().row(), 5)))))
        self.ui.comboBox_2.setCurrentIndex(QDate.currentDate().year() - int(self.soldat_model.data(self.soldat_model.index(self.ui.tableView.currentIndex().row(), 6))) + 1)


    def get_photo(self):
        file, check = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()", "", "PNG(*.png);; JPG(*.jpg)")
        if check:

            pixmap = QPixmap(file).scaled(200,200)
            self.ui.label.setPixmap(pixmap)

            with open(file,"rb") as f:
                img = f.read()

                self.ba = QByteArray()
                bf = QBuffer(self.ba)
                bf.open(QIODevice.WriteOnly)
                bf.write(img)
                f.close()

    def insert(self):
        if self.empty():
            QMessageBox.about(self, "ошибка", "не все поля заполнены")
            return
        lname = self.ui.lineEdit.text()
        fname = self.ui.lineEdit_2.text()
        mname = self.ui.lineEdit_3.text()

        salary = self.ui.lineEdit_4.text()
        post = self.ui.comboBox.currentText()
        year = self.ui.comboBox_2.currentText()

        query = QSqlQuery()
        sql = f"insert into soldat(photo, l, f, m, post, year, salary) values (:pic, '{lname}', '{fname}', '{mname}', '{post}', {year}, {salary})"

        query.prepare(sql)
        query.bindValue(":pic", self.ba)
        query.exec()

        if (query.lastError().number() != -1):
            QMessageBox.about(self, "Ошибка", f"{query.lastError().text()}")
            return

        self.clear_gui()
        self.soldat_model.setQuery(self.soldat_model.query().lastQuery())

    def delete(self):
        query = QSqlQuery()
        query.exec(f"delete from soldat where id = {int(self.soldat_model.data(self.soldat_model.index(self.ui.tableView.currentIndex().row(), 0)))}")

        if (query.lastError().number() != -1):
            QMessageBox.about(self, "Ошибка", f"{query.lastError().text()}")
            return

        self.soldat_model.setQuery(self.soldat_model.query().lastQuery())


    def update(self):
        if self.empty():
            QMessageBox.about(self, "Ошибка", "Не все поля заполнены")
            return
        lname = self.ui.lineEdit.text()
        fname = self.ui.lineEdit_2.text()
        mname = self.ui.lineEdit_3.text()

        salary = self.ui.lineEdit_4.text()
        post = self.ui.comboBox.currentText()
        year = self.ui.comboBox_2.currentText()

        query = QSqlQuery()

        sql = f"update soldat set photo = :pic, l = '{lname}', f = '{fname}', m = '{mname}', post = '{post}', year = {year}, salary = {salary} where id = {int(self.soldat_model.data(self.soldat_model.index(self.ui.tableView.currentIndex().row(), 0)))}"

        query.prepare(sql)
        query.bindValue(":pic", self.ba)
        query.exec()

        if (query.lastError().number() != -1):
            QMessageBox.about(self, "Ошибка", f"{query.lastError().text()}")
            return

        self.clear_gui()
        self.soldat_model.setQuery(self.soldat_model.query().lastQuery())

    def order(self):
        radioButton = self.sender()
        order_model = QSqlQueryModel()


        if radioButton.isChecked():
            if radioButton.text() == "Фамилия":
                order_model.setQuery("select * from soldat order by l asc")
            elif radioButton.text() == "Звание (алфавитный порядок)":
                order_model.setQuery("select * from soldat order by post asc")
            elif radioButton.text() == "Зарплата":
                order_model.setQuery("select * from soldat order by salary asc")

        self.set_header(order_model)
        self.ui.tableView_3.setModel(order_model)
        self.ui.tableView_3.setColumnHidden(0, True)
        self.ui.tableView_3.setColumnHidden(1, True)

    def find(self):
        find_name = self.ui.lineEdit_5.text()

        query = QSqlQuery()
        query.exec(f"select  count(*) from soldat where l like '{find_name}%'")
        query.first()
        if int(query.value(0)) == 0:
            QMessageBox.about(self, "Ошибка", "Такого человека нет")
            return

        find_model = QSqlQueryModel()
        find_model.setQuery(f"select * from soldat where l like '{find_name}%'")

        self.set_header(find_model)

        self.ui.tableView_2.setModel(find_model)
        self.ui.tableView_2.setColumnHidden(0, True)
        self.ui.tableView_2.setColumnHidden(1, True)


app = QtWidgets.QApplication([])
application = mywindow()
application.show()
sys.exit(app.exec())