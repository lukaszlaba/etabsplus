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
        self.pushButton_GetResults.clicked.connect(show_results)

        self.pushButton_zoomIn.clicked.connect(self.plainTextEdit.zoomIn)
        self.pushButton_zoomOut.clicked.connect(self.plainTextEdit.zoomOut)

        self.radioButton_SelectedGroup.clicked.connect(lambda: ui.listWidget_Groups.setEnabled(True))
        self.radioButton_SelectedGroup.clicked.connect(lambda: ui.listWidget_Section.setEnabled(False))

        self.radioButton_SelectedSection.clicked.connect(lambda: ui.listWidget_Section.setEnabled(True))
        self.radioButton_SelectedSection.clicked.connect(lambda: ui.listWidget_Groups.setEnabled(False))

        self.radioButton_SelecteInEtabs.clicked.connect(lambda: ui.listWidget_Groups.setEnabled(False))
        self.radioButton_SelecteInEtabs.clicked.connect(lambda: ui.listWidget_Section.setEnabled(False))

        self.set_title()
        self.set_app_info(app_info.about)

        self.set_progress_1()
        self.set_progress_2()

    def selected_LCs(self) -> list[str]:
        return [i.text() for i in self.listWidget_LC.selectedItems()]

    def selected_Groups(self) -> list[str]:
        return [i.text() for i in self.listWidget_Groups.selectedItems()]

    def selected_Sections(self) -> list[str]:
        return [i.text() for i in ui.listWidget_Section.selectedItems()]

    def set_list_of_LCs(self, lc_list: list[str]):
        self.listWidget_LC.clear()
        self.listWidget_LC.addItems(lc_list)

    def set_list_of_Sections(self, section_list: list[str]):
        self.listWidget_Section.clear()
        self.listWidget_Section.addItems(section_list)

    def set_list_of_Groups(self, groups_list: list[str]):
        self.listWidget_Groups.clear()
        self.listWidget_Groups.addItems(groups_list)

    def set_progress_1(self, value: int=0):
        self.progressBar_1.setValue(value)

    def set_progress_2(self, value: int=0):
        self.progressBar_2.setValue(value)

    def set_title(self, text: str=''):
        if text:
            self.setWindowTitle(f'{app_info.appname} {app_info.version} - {text}')
        else:
            self.setWindowTitle(f'{app_info.appname} {app_info.version}')

    def set_app_info(self, text: str=''):
        self.plainTextEdit_AppInfo.setPlainText(text)


def set_options():
    options = etabs_processing.Analysis_Options
    options.P_max = ui.checkBox_P_max.isChecked()
    options.P_min = ui.checkBox_P_min.isChecked()
    options.P_abs = ui.checkBox_P_abs.isChecked()
    options.V2_abs = ui.checkBox_V2_abs.isChecked()
    options.V3_abs = ui.checkBox_V3_abs.isChecked()
    options.T_abs = ui.checkBox_T_abs.isChecked()
    options.M2_abs = ui.checkBox_M2_abs.isChecked()
    options.M3_min = ui.checkBox_M3_min.isChecked()
    options.M3_max = ui.checkBox_M3_max.isChecked()
    options.M3_abs = ui.checkBox_M3_abs.isChecked()
    options.Mtot_abs = ui.checkBox_Mtot_abs.isChecked()
    options.Vtot_abs = ui.checkBox_Vtot_abs.isChecked()
    options.PV2_abs = ui.checkBox_PV2_abs.isChecked()
    options.PV3_abs = ui.checkBox_PV3_abs.isChecked()
    options.PV_abs = ui.checkBox_PV_abs.isChecked()
    options.sigma_PM2_abs = ui.checkBox_PM2_abs.isChecked()
    options.sigma_PM3_abs = ui.checkBox_PM3_abs.isChecked()
    options.sigma_PM_abs = ui.checkBox_PM_abs.isChecked()
    options.ends_only = ui.checkBox_ends_only.isChecked()
    options.reduce_LC_name= ui.checkBox_PM_abs_2.isChecked() #<!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def show_results():
    ui.plainTextEdit.setPlainText('Processing....')
    #--
    set_options()
    #--
    group_list = ui.selected_Groups()
    section_list = ui.selected_Sections()
    lc_list = ui.selected_LCs()
    #--
    report = ''
    #--
    if ui.radioButton_SelectedGroup.isChecked():
        i = 0
        for group in group_list:
            frame_list = etabs_processing.get_frame_list_for_group(group)
            report += f'{group}\n'
            report += etabs_processing.get_report(frame_list, lc_list,  progress = ui)
            report += '\n'
            i += 1
            ui.set_progress_2(int(i/len(group_list)*100))
        ui.set_progress_2()
    if ui.radioButton_SelectedSection.isChecked():
        i = 0
        for section in section_list:
            frame_list = etabs_processing.get_frame_list_for_prop(section)
            report += f'{section}\n'
            report += etabs_processing.get_report(frame_list, lc_list,  progress = ui)
            report += '\n'
            i += 1
            ui.set_progress_2(int(i/len(section_list)*100))
        ui.set_progress_2()
    if ui.radioButton_SelecteInEtabs.isChecked():
            frame_list = etabs_processing.get_frame_list_current_selected()
            report += f'Selected {len(frame_list)} frames\n'
            report += etabs_processing.get_report(frame_list, lc_list,  progress = ui)
            report += '\n'
    ui.plainTextEdit.setPlainText(report)

def connect_etabs():
    etabs_processing.connect()
    ui.set_list_of_LCs(etabs_processing.get_lcs_list())
    ui.set_list_of_Sections(etabs_processing.get_frame_props_list())
    ui.set_list_of_Groups(etabs_processing.get_groups_list())
    ui.set_title(etabs_processing.get_model_filename())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec())

#Icon
#https://icon-icons.com/icon/math-plus-minus/158290
#command used to frozening with pyinstaller
#pyinstaller --noconsole --icon=app.ico C:\Users\LABAL\source_etabsplus\etabsplus\scr\etabsplus.py


#https://github.com/enthought/comtypes/issues/340
#--hidden-import=comtypes.gen.{PowerPoint / Word / ...}   CSiAPIv1