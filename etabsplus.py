import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

from mainwindow_ui import Ui_MainWindow

import etabs_processing
import app_info

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.pushButton_GetEtabsData.clicked.connect(connect_etabs)
        self.pushButton_ClearResults.clicked.connect(self.plainTextEdit.clear)
        self.pushButton_GetResults.clicked.connect(show_results)

        self.radioButton_SelectedGroup.clicked.connect(lambda: ui.listWidget_Groups.setEnabled(True))
        self.radioButton_SelecteInEtabs.clicked.connect(lambda: ui.listWidget_Groups.setEnabled(False))

        self.set_title()
        self.set_app_info(app_info.about)

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

    def set_progress(self, value: int=0):
        self.progressBar.setValue(value)

    def set_title(self, text: str=''):
        if text:
            self.setWindowTitle(f'{app_info.appname} {app_info.version} - {text}')
        else:
            self.setWindowTitle(f'{app_info.appname} {app_info.version}')

    def set_app_info(self, text: str=''):
        self.plainTextEdit_AppInfo.setPlainText(text)


def set_options():
    options = etabs_processing.Analysis_Options

    options.P_max = ui.checkBox_Pmax.isChecked()
    options.P_maxabs = ui.checkBox_Pmax.isChecked()
    options.P_min = ui.checkBox_Pmax.isChecked()
    options.V2_maxabs = ui.checkBox_Pmax.isChecked()
    options.V3_maxabs = ui.checkBox_Pmax.isChecked()
    options.T_maxabs = ui.checkBox_Pmax.isChecked()
    options.M2_maxabs = ui.checkBox_Pmax.isChecked()
    options.M3_maxabs = ui.checkBox_Pmax.isChecked()
    options.M3_max = ui.checkBox_Pmax.isChecked()
    options.M3_min = ui.checkBox_Pmax.isChecked()
    options.Mtot_maxabs = ui.checkBox_Pmax.isChecked()
    options.Vtot_maxabs = ui.checkBox_Pmax.isChecked()
    options.NM3signatot_maxabs = ui.checkBox_Pmax.isChecked()
    options.NM2signatot_maxabs = ui.checkBox_Pmax.isChecked()
    options.NMsignatot_maxabs = ui.checkBox_Pmax.isChecked()
    options.ends_only = ui.checkBox_EndsOnly.isChecked()

def show_results():
    set_options()
    group_list = ui.selected_Groups()
    lc_list = ui.selected_LCs()

    report = ''

    for group in group_list:
        frame_list = etabs_processing.get_frame_list_for_group(group)
        report += f'{group}\n'
        report += etabs_processing.get_report(frame_list, lc_list,  progress = ui)


    ui.plainTextEdit.setPlainText(report)


def connect_etabs():
    etabs_processing.connect()
    ui.set_list_of_LCs(etabs_processing.get_lcs_list())
    ui.set_list_of_Groups(etabs_processing.get_groups_list())
    ui.set_title(etabs_processing.get_model_filename())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()

    ui.listWidget_LC.clear() #!!!!!!!!!
    ui.listWidget_Groups.clear() #!!!!!!!!!!
    ui.set_progress() #!!!!!!!!!!!

    sys.exit(app.exec())
