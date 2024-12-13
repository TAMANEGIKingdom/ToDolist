import sys
import os
import ctypes
from PySide6.QtWidgets import QApplication, QMainWindow
from ToDoUI import Ui_MainWindow  # 生成されたファイル名をインポート
from PySide6.QtCore import (Qt)
from PySide6.QtWidgets import (QApplication, QMainWindow)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

    def keyPressEvent(self, event):
        """
        キー入力を処理する
        """
        if event.key() in [Qt.Key_Delete, Qt.Key_Backspace]:
            if hasattr(self, "selected_task_group") and self.selected_task_group is not None:
                # 選択されたタスクグループを削除
                self.remove_task_group(self.selected_task_group)
                # 選択状態を解除
                self.selected_task_group = None
    def closeEvent(self, event):
        """
        ウィンドウが閉じられるときにタスク状態を保存
        """
        self.save_to_file()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # アプリ全体のアイコンを設定
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("my_application")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

