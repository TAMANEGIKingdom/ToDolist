import os
from OKTab import *
from PySide6.QtCore import ( QMetaObject, QRect, Qt,QDateTime,QTimer)
from PySide6.QtGui import (QIcon)
from PySide6.QtWidgets import ( QCheckBox, QDateTimeEdit, QFrame,
    QGroupBox, QLabel, QMenuBar, QProgressBar, QPushButton,
    QScrollArea, QStatusBar, QTabWidget, QTextEdit, QWidget,QInputDialog,QVBoxLayout,QComboBox, QSizePolicy)
import json
from OKTab import update_completed_tab

# Ui_MainWindowクラスの定義
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        # ウィンドウのサイズ
        window_size = 700
        # 余白
        space = 10
        # 複数のタスクグループを管理するためのリスト
        self.Task = []
        # 複数のタスクフレームを管理するためのリスト
        self.frame = []

        # メインウィンドウの設定
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        # MainWindow.resize(481, 645)

        # ウィンドウのタイトルを変更
        MainWindow.setWindowTitle("ToDo")  # 新しいタイトルを設定

        # ウィンドウのサイズを固定
        MainWindow.setFixedSize(481, window_size)

        # アイコンの設定
        icon = QIcon("app_icon.ico")
        MainWindow.setWindowIcon(icon)
        MainWindow.setTabShape(QTabWidget.TabShape.Rounded)
        self.main_icon = icon  # メインウィンドウのアイコンを保持

        # セントラルウィジェットの設定
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        # ラベルを追加
        self.headerLabel = QLabel(self.centralwidget)
        self.headerLabel.setObjectName(u"headerLabel")
        self.headerLabel.setGeometry(QRect(10, 5, 461, 25))  # ラベルの位置とサイズを設定
        text = "ToDoリスト管理ツール"
        self.headerLabel.setText(text)  # ラベルのテキストを設定
        self.headerLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)  # テキストを中央揃えに設定
        self.headerLabel.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                border: 1px solid lightgray;  /* ライトグレーの枠を追加 */
                border-radius: 5px;          /* 角を丸める */
            }
        """)


        # テキストをスライドさせるための初期設定
        self.full_text = self.headerLabel.text() + "　"*20  # 末尾に余白を追加
        self.full_text = self.headerLabel.text()
        self.text_index = 0

        # QTimerを使用して定期的にテキストを更新
        self.text_timer = QTimer()
        self.text_timer.timeout.connect(self.scroll_text)  # タイマーが切れるごとに`scroll_text`を実行
        self.text_timer.start(200)  # 200ミリ秒ごとに更新


        # タブウィジェットの設定
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(0, 30, 481, 635))
        # タブ変更イベントの設定
        self.tabWidget.currentChanged.connect(self.update_tab_content)


        # 全てタブの設定
        self.AllTab = QWidget()
        self.AllTab.setObjectName(u"AllTab")

        self.Sortcombo = QComboBox(self.AllTab)
        self.Sortcombo.setObjectName(u"Sortcombo")
        self.Sortcombo.setGeometry(QRect(0, 0, 471, 30))
        # コンボボックスに選択肢を追加
        self.Sortcombo.addItems(["Option 1", "Option 2", "Option 3", "Option 4"])
        # 選択変更時の処理を設定（任意）
        self.Sortcombo.currentIndexChanged.connect(self.sort_frames)
        # 選択保存用
        self.previous_index = -1

        # 全てタブのスクロールエリア
        self.AllscrollArea = QScrollArea(self.AllTab)
        self.AllscrollArea.setObjectName(u"AllscrollArea")
        self.AllscrollArea.setGeometry(QRect(0, 35, 471, 600))
        self.AllscrollArea.setWidgetResizable(True)

        # スクロールエリアの内容
        self.AllscrollAreaWidgetContents = QWidget()
        self.AllscrollAreaWidgetContents.setObjectName(u"AllscrollAreaWidgetContents")
        self.AllscrollAreaWidgetContents.setGeometry(QRect(0, 0, 469, 400))
        # フレーム用レイアウトを設定
        self.layout = QVBoxLayout(self.AllscrollAreaWidgetContents)
        # 上詰め配置のためのレイアウト設定
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        try:
            self.load_from_file()
        except FileNotFoundError:
            # ファイルがなければデフォルトフレームを作成
            frame_dict = self.create_task_frame()
            self.frame.append(frame_dict)

        # スクロールエリアのウィジェット設定
        self.AllscrollArea.setWidget(self.AllscrollAreaWidgetContents)

        # タブに追加
        self.tabWidget.addTab(self.AllTab, "タスク一覧")  # タブ名設定

        # 未完了タブの設定
        self.NGTab = QWidget()
        self.NGTab.setObjectName(u"NGTab")

        # 未完了タブに追加
        self.tabWidget.addTab(self.NGTab, "未完了")  # タブ名設定

        # 完了タブの設定
        self.OKTab = QWidget()
        self.OKTab.setObjectName(u"OKTab")
        # 完了タブのレイアウト設定
        self.OKTabLayout = QVBoxLayout(self.OKTab)

        # 完了タブに追加
        self.tabWidget.addTab(self.OKTab, "完了")  # タブ名設定

        # 横長の「+」ボタンを追加
        self.bottomPlusButton = QPushButton(self.centralwidget)
        self.bottomPlusButton.setObjectName(u"bottomPlusButton")
        self.bottomPlusButton.setGeometry(QRect(0, window_size-20*2, 481, 20))  # 幅をウィンドウ全体に合わせる
        self.bottomPlusButton.setText("+")  # ボタンのテキスト設定
        self.bottomPlusButton.clicked.connect(self.add_task_frame)

        # セントラルウィジェットを設定
        MainWindow.setCentralWidget(self.centralwidget)

        # メニューバーとステータスバー
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # タブの初期インデックス設定
        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)

        MainWindow.setFocusPolicy(Qt.StrongFocus)

    def update_progress(self, frame_dict):
        """
        指定されたフレーム内のチェックボックスを監視し、対応するプログレスバーを更新する
        """
        progressBar = frame_dict["progressBar"]  # フレーム内のプログレスバー
        total_checkboxes = frame_dict["task_count"]  # チェックボックスの総数
        checked_boxes = 0     # チェックされたチェックボックスの数

        # フレーム内のタスクを対象に進捗を計算
        for task in self.Task:
            if task is not None and task["group"].parent() == frame_dict["frame"]:  # フレームに属するタスクのみ
                check_box = task["check_box"]
                if check_box.isChecked():
                    checked_boxes += 1

        # プログレスを計算
        progress = int((checked_boxes / total_checkboxes) * 100) if total_checkboxes > 0 else 0
        progressBar.setValue(progress)

    def change_label_text(self,label):
        """変更ボタンが押されたときにラベルのテキストを変更"""
        dialog = QInputDialog()
        dialog.setWindowTitle("ラベル変更")
        dialog.setLabelText("新しい文字列を入力してください:")
        dialog.setWindowIcon(self.main_icon)  # メインウィンドウのアイコンを設定
        ok = dialog.exec()  # ダイアログを表示
        if ok:
            new_text = dialog.textValue()  # 入力された値を取得
            if new_text:
                label.setText(new_text)

    def adjust_textedit_height(self, task_group,frame):
        """
        テキストの内容に応じてテキストボックス、グループ、フレームの高さを調整
        task_group: タスクグループの辞書
        """
        text_edit = task_group["text_edit"]
        group_box = task_group["group"]

        # テキストの高さを取得(0は高さ21)
        document = text_edit.document()
        document_height = document.size().height()
        if document_height < 21:
            document_height = 21

        # 現在のスクロール位置を取得
        vertical_scroll_bar = self.AllscrollArea.verticalScrollBar()
        is_at_bottom = vertical_scroll_bar.value() == vertical_scroll_bar.maximum()

        # テキストボックスの高さを更新
        text_edit.setFixedHeight(int(document_height))

        # グループボックスの高さをテキストボックスに合わせて更新
        new_group_height = int(document_height) + 50
        group_box.setFixedHeight(new_group_height)

        # フレーム全体の高さを再計算
        y_offset = 40  # 初期オフセット
        for task in self.Task:
            if task is not None:
                group = task["group"]
                y_offset += group.height() + 10  # 各タスクグループの高さに余白を加える

        # フレームの高さを更新
        frame.setMinimumHeight(y_offset)
        frame.adjustSize()

        # スクロールエリアの内容の高さを更新
        self.AllscrollAreaWidgetContents.setMinimumHeight(y_offset)
        self.AllscrollAreaWidgetContents.adjustSize()

        self.reorganize_task_groups()

        # カーソルを常に表示 (改行後のスクロール位置を適正化)
        text_edit.ensureCursorVisible()

        # 一番下にスクロールされている場合のみ新しい高さに合わせる
        if is_at_bottom:
            vertical_scroll_bar.setValue(vertical_scroll_bar.maximum())

    def create_task_group(self, parent_frame,layoutTask,frame_dict):
        """
        タスクグループを作成し、必要なオブジェクトを辞書にまとめて返す
        """
        # タスクのカウントを取得しインクリメント
        frame_dict["task_count"] += 1
        task_number = frame_dict["task_count"]
        
        # タスクのグループボックス
        task_group = QGroupBox(parent_frame)
        task_group.setObjectName(u"Task")
        task_group.setGeometry(QRect(5, 40, 420, 71))
        task_group.setTitle(f"タスク {task_number}")  # タスク番号を設定
        # タスクグループをレイアウトに追加
        layoutTask.addWidget(task_group)
        # 外枠のみにスタイルを適用
        task_group.setStyleSheet("""
            QGroupBox {
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            margin-top: 10px; /* タイトル部分の余白を確保 */
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }

            QTextEdit {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 2px;
            }
        """)

        # タスクグループのサイズポリシーを設定
        task_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        task_group.setMinimumHeight(71)  # 必要な最小高さを設定

        # マウスクリックイベントを設定
        task_group.mousePressEvent = lambda event: self.select_task_group(task_group,parent_frame)

        # テキスト入力欄
        text_edit = QTextEdit(task_group)
        text_edit.setObjectName(u"textEdit")
        text_edit.setGeometry(QRect(35, 40, 380, 21))
        # テキストの高さ調整を接続
        text_edit.textChanged.connect(lambda: self.adjust_textedit_height(task_dict,frame_dict["frame"]))

        # テキストエディタの高さが自動調整されるように設定（重要）
        text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        text_edit.setMinimumHeight(21)

        # チェックボックス
        check_box = QCheckBox(task_group)
        check_box.setObjectName(u"checkBox")
        check_box.setGeometry(QRect(10, 40, 21, 20))
        check_box.setChecked(False)
        check_box.setText("CheckBox")
        # タスクグループのチェックボックスの変更イベント設定
        check_box.stateChanged.connect(lambda: self.update_progress(frame_dict))


        # 日時入力欄
        date_time_edit = QDateTimeEdit(task_group)
        date_time_edit.setObjectName(u"dateTimeEdit")
        date_time_edit.setGeometry(QRect(255, 15, 154, 23))
        date_time_edit.setDisplayFormat("yy/MM/dd H:mm")  # 表示フォーマット設定
        date_time_edit.setDateTime(QDateTime.currentDateTime())  # 今日の日付と時刻をデフォルト値に設定

        # まとめて辞書で返す
        task_dict = {
            "group": task_group,
            "text_edit": text_edit,
            "check_box": check_box,
            "date_time_edit": date_time_edit,
            "frame":parent_frame
        }

        # 明示的に描画
        task_group.show()
        text_edit.show()
        check_box.show()
        date_time_edit.show()

        return task_dict

    def add_task_group(self, frame):
        """
        "+"ボタンを押したときに新しいタスクグループを追加
        """
        # 対応する frame_dict を検索
        frame_dict = next((f for f in self.frame if f["frame"] == frame), None)
        if frame_dict is None:
            print(f"Error: Frame {frame} not found")
            return

        # layoutTask を取得
        layoutTask = frame_dict["layoutTask"]

        # 空いているインデックスを探す
        for i in range(len(self.Task)):
            if self.Task[i] is None:
                new_task_group = self.create_task_group(frame,layoutTask,frame_dict)
                self.Task[i] = new_task_group
                break
        else:
            # 空いているインデックスがなければ末尾に追加
            new_task_group = self.create_task_group(frame,layoutTask,frame_dict)
            self.Task.append(new_task_group)

        # 新しいタスクグループの位置を計算
        existing_task_count = len(self.Task)
        new_task_group["group"].setGeometry(QRect(5, 40 + (existing_task_count - 1) * 80, 420, 71))

        # フレーム全体の高さを調整
        frame.setMinimumHeight(40 + existing_task_count * 80)
        frame.adjustSize()
        self.AllscrollAreaWidgetContents.adjustSize()

        self.reorganize_task_groups()
        self.renumber_task_groups()
        # 追加分含めて進捗を更新
        self.update_progress(frame_dict)

    def reorganize_task_groups(self):
        """
        フレームとタスクグループの位置を再計算
        """
        y_offset_frame = 0  # フレームの初期オフセット
        total_height = 0  # スクロールエリア全体の高さを追跡

        for frame_dict in self.frame:
            if frame_dict is not None:  # 空でない場合のみ処理
                frame = frame_dict["frame"]
                layout_task = frame_dict.get("layoutTask", None)

                # タスクグループの位置を再計算
                if layout_task:
                    y_offset_task = 40  # タスクグループの初期オフセット
                    group_count = 0  # フレーム内のタスクグループ数

                    for task in self.Task:
                        if task and task["group"].parent() == frame:  # フレームに属するタスクのみ処理
                            group = task["group"]
                            group.setGeometry(QRect(5, y_offset_task, 420, 71))  # 新しい位置を設定
                            y_offset_task += group.height() + 10  # タスクグループの高さと余白を加算
                            group_count += 1  # タスクグループ数をカウント

                    # フレーム全体の高さをタスクグループに合わせて調整
                    frame.setMinimumHeight(max(y_offset_task, 121))  # 最低高さを維持
                    frame.adjustSize()

                # フレームの位置を設定
                frame.setGeometry(QRect(0, y_offset_frame, 451, frame.height()))
                y_offset_frame += frame.height() + 10  # フレームの高さと余白を加算

                # スクロールエリア全体の高さを更新
                total_height = max(total_height, y_offset_frame)

        # スクロールエリア全体の高さを更新
        self.AllscrollAreaWidgetContents.setMinimumHeight(total_height)
        self.AllscrollAreaWidgetContents.adjustSize()

    def remove_task_group(self,selected):
        """
        タスクグループを削除
        """

        frame = selected["frame"]
        task_group = selected["group"]

        # 対応する frame_dict を取得
        frame_dict = next((f for f in self.frame if f["frame"] == frame), None)
        if frame_dict is None:
            print("Error: Frame not found")
            return
    
        # `task_group`が辞書か直接`QGroupBox`かを判定
        if isinstance(task_group, dict):
            group = task_group["group"]  # 辞書の場合は`group`キーを使用
        else:
            group = task_group  # 直接`QGroupBox`の場合

        # レイアウトからタスクグループを削除
        layoutTask = frame_dict["layoutTask"]
        layoutTask.removeWidget(task_group)
        task_group.setParent(None)
        task_group.deleteLater()

        # リスト内の該当タスクグループを削除
        self.Task = [task for task in self.Task if task["group"] != group]
        frame_dict["task_count"] -= 1

        # タスク番号を振り直す
        self.renumber_task_groups()

        # タスクグループの位置を再計算
        self.reorganize_task_groups()

        # 削除後に選択状態を解除
        self.selected_task_group = None

    def renumber_task_groups(self):
        """
        各フレーム内でタスク番号を1から振り直す
        """
        for frame_dict in self.frame:
            if frame_dict is not None:  # 空でない場合のみ処理
                frame = frame_dict["frame"]
                layoutTask = frame_dict.get("layoutTask", None)

                if layoutTask:
                    task_number = 1  # 各フレーム内でタスク番号をリセット

                    for task in self.Task:
                        # 現在のフレームに属するタスクのみ処理
                        if task and task["group"].parent() == frame:
                            task["group"].setTitle(f"タスク {task_number}")
                            task_number += 1  # 次のタスク番号へ

    def select_task_group(self, task_group, frame):
        """
        タスクグループを選択状態にする
        """
        # 現在選択されているタスクグループが再度クリックされた場合、デフォルトに戻す
        if (
            hasattr(self, "selected_task_group")
            and self.selected_task_group is not None
            and self.selected_task_group["group"] == task_group
        ):
            task_group.setStyleSheet("""
                QGroupBox {
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                    margin-top: 10px; /* タイトル部分の余白を確保 */
                }

                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 5px;
                    color: #E0E0E0; /* デフォルトのタイトル色 */
                }

                QTextEdit {
                    border: 1px solid #E0E0E0;
                    border-radius: 4px;
                    padding: 2px;
                }
            """)
            # 選択を解除
            self.selected_task_group = None
            return

        # すべてのタスクグループをデフォルトの状態に戻す
        for task in self.Task:
            if task:
                task["group"].setStyleSheet("""
                    QGroupBox {
                        border: 1px solid #E0E0E0;
                        border-radius: 8px;
                        margin-top: 10px; /* タイトル部分の余白を確保 */
                    }

                    QGroupBox::title {
                        subcontrol-origin: margin;
                        subcontrol-position: top left;
                        padding: 0 5px;
                    }

                    QTextEdit {
                        border: 1px solid #E0E0E0;
                        border-radius: 4px;
                        padding: 2px;
                    }
                """)

        # 選択されたタスクグループを強調表示
        task_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #0078D7;
                border-radius: 8px;
                margin-top: 10px; /* タイトル部分の余白を確保 */
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color:#0078D7;
            }

            QTextEdit {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 2px;
            }
        """)

        # 現在選択されているタスクグループを保存
        self.selected_task_group = {"frame": frame, "group": task_group}

    def create_task_frame(self):
        """
        タスクフレームを作成し、必要なオブジェクトを辞書にまとめて返す
        """
        # タスクのフレーム
        frame = QFrame(self.AllscrollAreaWidgetContents)
        frame.setObjectName(u"frame")
        frame.setGeometry(QRect(0, 0, 451, 121))
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setFrameShadow(QFrame.Shadow.Raised)
        # タスクのフレームを追加
        self.layout.addWidget(frame)
        
        # タスクグループのサイズポリシーを設定
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        frame.setMinimumHeight(121)  # 必要な最小高さを設定

        # ラベル
        label = QLabel(frame)
        label.setObjectName(u"label")
        label.setGeometry(QRect(10, 10, 101, 21))
        label.setText("システム部業務")  # ラベル設定

        # ボタン
        pushButton = QPushButton(frame)
        pushButton.setObjectName(u"pushButton")
        pushButton.setGeometry(QRect(110, 10, 41, 21))
        pushButton.setText("変更")  # ボタンのテキスト設定
        pushButton.clicked.connect(lambda:self.change_label_text(label))  # ボタンのクリックシグナルを接続

        # プログレスバー
        progressBar = QProgressBar(frame)
        progressBar.setObjectName(u"progressBar")
        progressBar.setGeometry(QRect(167, 10, 200, 23))  # 幅を調整して余白を作成
        progressBar.setValue(0)
        progressBar.setTextVisible(True)
        progressBar.setInvertedAppearance(False)
        progressBar.setFormat("%p%")  # パーセンテージ形式設定

        # 「+」ボタン
        plusButton = QPushButton(frame)
        plusButton.setObjectName(u"plusButton")
        plusButton.setGeometry(QRect(370, 10, 30, 23))  # プログレスバーの右側に配置
        plusButton.setText("+")  # ボタンのテキスト設定
        plusButton.clicked.connect(lambda: self.add_task_group(frame))

        # 「×」ボタン
        closeButton = QPushButton(frame)
        closeButton.setObjectName(u"closeButton")
        closeButton.setGeometry(QRect(405, 10, 30, 23))  # 「+」ボタンの右に配置
        closeButton.setText("×")  # ボタンのテキスト設定
        closeButton.clicked.connect(lambda: self.remove_task_frame(frame_dict))

        Sortcombo = QComboBox(frame)
        Sortcombo.setObjectName(u"Sortcombo")
        Sortcombo.setGeometry(QRect(10, 45, 420, 30))
        # コンボボックスに選択肢を追加
        Sortcombo.addItems(["Option 1", "Option 2", "Option 3", "Option 4"])
        # 選択変更時の処理を設定（任意）
        Sortcombo.currentIndexChanged.connect(self.sort_frames)
        # 選択保存用
        self.previous_index_Task = -1

        # グループ用レイアウトを設定
        layoutTask = QVBoxLayout(frame)
        # 上詰め配置のためのレイアウト設定
        layoutTask.setAlignment(Qt.AlignmentFlag.AlignTop)
        # レイアウトにスペーサーを追加
        layoutTask.addSpacing(65)

        # まとめて辞書で返す
        frame_dict = {
            "frame": frame,
            "label": label,
            "pushButton": pushButton,
            "progressBar": progressBar,
            "plusButton": plusButton,
            "closeButton": closeButton,
            "layoutTask": layoutTask,
            "task_count": 0  # フレーム内のタスク数を初期化
        }
        
        # 最初のタスクグループを作成して追加
        task_dict = self.create_task_group(frame,layoutTask,frame_dict)
        self.Task.append(task_dict)
        # 起動時に adjust_textedit_height を実行
        #self.adjust_textedit_height(task_dict,frame)
        # 起動時に進捗を更新
        self.update_progress(frame_dict)

        # 明示的に描画
        frame.show()
        label.show()
        pushButton.show()
        progressBar.show()
        plusButton.show()
        closeButton.show()

        return frame_dict

    def add_task_frame(self):
        """
        "+"ボタンを押したときに新しいタスクグループを追加
        """
        # 空いているインデックスを探す
        for i in range(len(self.frame)):
            if self.frame[i] is None:
                new_task_frame = self.create_task_frame()
                self.frame[i] = new_task_frame
                break
        else:
            # 空いているインデックスがなければ末尾に追加
            new_task_frame = self.create_task_frame()
            self.frame.append(new_task_frame)

        # 新しいタスクグループの位置を計算
        existing_task_count = len(self.frame)
        new_task_frame["frame"].setGeometry(QRect(5, 40 + (existing_task_count - 1) * 130, 451, 121))

        # フレーム全体の高さを調整
        self.AllscrollAreaWidgetContents.adjustSize()

        self.reorganize_task_groups()
        self.alternate_frame_colors()

    def remove_task_frame(self, frame_dict):
        """
        指定されたフレームを削除
        """
        if len(self.frame) <= 1:
            return
    
        frame = frame_dict["frame"]

        # そのフレームに属するタスクを全て削除
        self.Task = [task for task in self.Task if task["frame"] != frame]

        # スクロールエリアからフレームを削除
        self.layout.removeWidget(frame)
        frame.setParent(None)
        frame.deleteLater()

        # フレームリストから削除
        self.frame.remove(frame_dict)

        # 残りのフレームやタスクを整理
        self.reorganize_task_groups()
        self.alternate_frame_colors()

    def update_tab_content(self, index):
        """
        タブが変更された際に完了タブの内容を更新。
        """
        # タブインデックスのチェック
        if self.tabWidget.tabText(index) == "完了":
            update_completed_tab(self)

    def save_to_file(self, filename="todo_data.json"):
        """
        現在のタスク状態をJSONファイルに保存する
        """
        data = []
        for frame_dict in self.frame:
            frame_data = {
                "label": frame_dict["label"].text(),
                "progress": frame_dict["progressBar"].value(),
                "tasks": []
            }
            for task in self.Task:
                if task["frame"] == frame_dict["frame"]:
                    frame_data["tasks"].append({
                        "title": task["group"].title(),
                        "text": task["text_edit"].toPlainText(),
                        "checked": task["check_box"].isChecked(),
                        "date_time": task["date_time_edit"].dateTime().toString("yyyy-MM-dd HH:mm:ss")
                    })
            data.append(frame_data)
        
        # JSONに保存
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def load_from_file(self, filename="todo_data.json"):
        """
        JSONファイルからタスク状態を復元する
        """
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        # 現在のタスクとフレームをクリア
        for frame_dict in self.frame:
            frame = frame_dict["frame"]
            self.layout.removeWidget(frame)
            frame.setParent(None)
            frame.deleteLater()
        self.frame.clear()
        self.Task.clear()

        # データを再構築
        for frame_data in data:
            # フレームを作成
            frame_dict = self.create_task_frame()  # 新しいフレームを作成
            frame_dict["label"].setText(frame_data["label"])
            self.frame.append(frame_dict)

            # 自動生成された最初のタスクグループを削除
            if frame_dict["task_count"] > 0:  # タスクが1つ以上ある場合のみ処理
                # 最初に作られたタスクグループを取得
                first_task_group = next(
                    (task for task in self.Task if task["frame"] == frame_dict["frame"]), 
                    None
                )
                if first_task_group:
                    self.remove_task_group(first_task_group)

            # タスクグループを再構築
            for task_data in frame_data["tasks"]:
                task_group = self.create_task_group(frame_dict["frame"], frame_dict["layoutTask"], frame_dict)
                task_group["group"].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                task_group["group"].setMinimumHeight(71)  # 必要な最小高さを設定
                task_group["text_edit"].setPlainText(task_data["text"])
                task_group["text_edit"].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                task_group["text_edit"].setMinimumHeight(21)
                task_group["check_box"].setChecked(task_data["checked"])
                task_group["date_time_edit"].setDateTime(QDateTime.fromString(task_data["date_time"], "yyyy-MM-dd HH:mm:ss"))
                self.Task.append(task_group)

                # 高さ調整を遅延実行
                QTimer.singleShot(0, lambda tg=task_group, f=frame_dict["frame"]: self.adjust_textedit_height(tg, f))

            self.update_progress(frame_dict)

        # タスクグループの位置を整理
        self.reorganize_task_groups()
        self.renumber_task_groups()
        self.alternate_frame_colors()

    def alternate_frame_colors(self):
        """
        フレームの背景色を交互に変更する。
        ライトグレー、濃いグレーを繰り返す。
        """
        colors = ["#1e1e1e", "#3e3e3e"]  # ライトグレーと濃いグレー
        for index, frame_dict in enumerate(self.frame):
            frame = frame_dict["frame"]
            color = colors[index % len(colors)]  # インデックスに基づいて色を選択
            frame.setStyleSheet(f"background-color: {color};")

    def scroll_text(self):
        """
        ラベルのテキストをスライドさせる処理
        """
        # テキストを一文字ずつスライド
        if len(self.full_text)>50:
            display_text = self.full_text[self.text_index:] + self.full_text[:self.text_index]
            self.headerLabel.setText(display_text)

            # インデックスを進める（文字数を超えたらリセット）
            self.text_index = (self.text_index + 1) % len(self.full_text)

    def rearrange_layout(self, layout, frame_list):
        """
        レイアウト内のウィジェットを新しい順序で並べ替える
        :param layout: QVBoxLayoutやQHBoxLayoutなどのレイアウト
        :param frame_list: 新しい順序のフレームリスト（辞書リスト）
        """
        # 既存のウィジェットを全て取り除く
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        # フレームリストの順序で追加し直す
        for frame_dict in frame_list:
            # 辞書の中からフレームオブジェクトを取得
            widget = frame_dict.get("frame")  # "frame"キーが存在することを前提
            if widget:
                layout.addWidget(widget)

    def sort_frames(self,index):
        """
        フレームの順序をソートして、レイアウトに適用する
        1:
        2:
        3:
        """

        # インデックスが変わっていなければ何もしない
        if index == self.previous_index:
            return

        if index == 0:  # "順序を反転"が選択された場合
            self.frame.reverse()
            self.rearrange_layout(self.layout, self.frame)

        elif index == 1:  # "タスク順序を反転"が選択された場合
            for frame_dict in self.frame:
                if frame_dict and "layoutTask" in frame_dict:
                    # フレーム内のタスクを取得
                    tasks_in_frame = [task for task in self.Task if task["frame"] == frame_dict["frame"]]

                    # タスク順序を反転
                    reversed_tasks = list(reversed(tasks_in_frame))

                    # `self.Task` を更新
                    for original_task, reversed_task in zip(tasks_in_frame, reversed_tasks):
                        idx = self.Task.index(original_task)
                        self.Task[idx] = reversed_task

                    # タスクの並び替えを適用
                    self.rearrange_tasks_within_frame(frame_dict, reversed_tasks)

        # 現在のインデックスを記録
        self.previous_index = index

    def rearrange_tasks_within_frame(self, frame_dict, tasks_in_frame):
        """
        指定されたフレーム内のタスクを並び替える
        :param frame_dict: フレームの情報を含む辞書
        :param tasks_in_frame: フレーム内のタスクを並び替えたリスト
        """
        if not frame_dict or "layoutTask" not in frame_dict:
            return

        # レイアウトを取得
        layout_task = frame_dict["layoutTask"]

        # レイアウト内のウィジェットをすべて削除
        while layout_task.count():
            item = layout_task.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        
        # レイアウトの一番上にスペーサーを追加
        layout_task.addSpacing(30)

        # 並び替えられたタスクを再配置
        for task in tasks_in_frame:
            group = task["group"]  # タスクのグループボックス
            layout_task.addWidget(group)

        # レイアウトとフレームのサイズを更新
        frame_dict["frame"].adjustSize()
        self.reorganize_task_groups()




