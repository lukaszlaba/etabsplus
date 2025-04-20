import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

from mainwindow_ui import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.pushButton_ClearResults.clicked.connect(self.plainTextEdit.clear)
        self.pushButton_GetResults.clicked.connect(pull_member_results_from_etabs)

        self.radioButton_SelectedGroup.clicked.connect(lambda: ui.listWidget_Groups.setEnabled(True))
        self.radioButton_SelecteInEtabs.clicked.connect(lambda: ui.listWidget_Groups.setEnabled(False))

    def selected_LCs(self) -> list[str]:
        return [i.text() for i in self.listWidget_LC.selectedItems()]

    def selected_Groups(self) -> list[str]:
        return [i.text() for i in self.listWidget_Groups.selectedItems()]

    def set_list_of_LCs(self, lc_list: list[str]):
        self.listWidget_LC.clear()
        self.listWidget_LC.addItems(lc_list)

    def set_list_of_Groups(self, groups_list: list[str]):
        self.listWidget_Groups.clear()
        self.listWidget_Groups.addItems(groups_list)

    def set_progress(value: int=0):
        self.progressBar.setValue(value)

def pull_member_results_from_etabs():
    ui.plainTextEdit.setPlainText('Results..')



if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec())
