from PyQt5.QtWidgets import (QApplication, QDialog, QTableWidget, QHeaderView, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QFrame, QPushButton, QSizePolicy)
from PyQt5.QtCore import QRect, QThread, pyqtSignal
from module import Window


class TableShow(QTableWidget):
    end = pyqtSignal()
    one_success = pyqtSignal()
    one_error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._nb_thread = 1
        self._item_width = 440
        self._item_height = 320
        margin = self.parent().layout().getContentsMargins()
        self._width = self.parent().width() - (margin[0] + margin[2])
        self._max_column = max(self._width // self._item_width, 1)
        self._row = 1
        self._column = 1
        h_header = self.horizontalHeader()
        h_header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        h_header.setDefaultSectionSize(self._item_width)
        h_header.hide()
        v_header = self.verticalHeader()
        v_header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        v_header.setDefaultSectionSize(self._item_height)
        v_header.hide()
        self._items = [None]
        self._threads = [None]
        self._success = 0
        self._error = 0

    def successCount(self):
        return self._success

    def errorCount(self):
        return self._error

    def setNumberThreads(self, nb_thread):
        self._nb_thread = nb_thread
        self._threads = [None] * self._nb_thread
        self._column = self._max_column if self._max_column < self._nb_thread else self._nb_thread
        self._row = self._nb_thread // self._column + (self._nb_thread % self._column > 0)
        self.setColumnCount(self._column)
        self.setRowCount(self._row)
        self._items = [None] * (self._column * self._row)

    def setItemSize(self, size):
        self._item_width = size[0]
        self._item_height = size[1]
        self.horizontalHeader().setDefaultSectionSize(self._item_width)
        self.verticalHeader().setDefaultSectionSize(self._item_height)

    def setMaxColumn(self, count):
        self._max_column = count
        self._column = self._max_column if self._max_column < self._nb_thread else self._nb_thread
        self._row = self._nb_thread // self._column + (self._nb_thread % self._column > 0)
        self.setColumnCount(self._column)
        self.setRowCount(self._row)

    def setThread(self, idx, target, args):
        if idx > self._nb_thread:
            raise ValueError("thread index out of range")
        item = self._items[idx]
        if isinstance(item, ItemShowWidget):
            window = Window.from_pyqt(item.widget)
        elif isinstance(item, QWidget):
            window = Window.from_pyqt(item)
        else:
            raise
        if self._threads[idx] is not None:
            if not self._threads[idx].isRunning():
                thread = self.Thread(window, item, target, args)
                self._threads[idx] = thread
                thread.end.connect(self._on_thread_finished)
                thread.start()
            else:
                print("Thread %d already running" % idx)
        else:
            thread = self.Thread(window, item, target, args)
            self._threads[idx] = thread
            thread.end.connect(self._on_thread_finished)
            thread.success.connect(self._on_thread_success)
            thread.error.connect(self._on_thread_error)
            thread.start()

    def _on_thread_success(self):
        self._success += 1
        self.one_success.emit()

    def _on_thread_error(self, error):
        self._error += 1
        self.one_error.emit(error)

    def _on_thread_finished(self):
        if self.runningCount() == 0:
            self.end.emit()

    def run(self, target, args):
        for i in range(self._nb_thread):
            self.setThread(i, target, args)

    def getItem(self, idx):
        return self._items[idx]

    def setItem(self, idx, item):
        item.setGeometry(QRect(0, 0, self._item_width, self._item_height))
        self.setCellWidget(idx // self._column, idx % self._column, item)
        self._items[idx] = item

    def clear(self):
        for i, thread in enumerate(self._threads):
            if thread is not None:
                thread.terminate()
                self._threads[i] = None

    def listThreads(self):
        return self._threads

    def runningCount(self):
        c = 0
        for t in self._threads:
            if t is not None and t.isRunning():
                c += 1
        return c


    class Thread(QThread):
        error = pyqtSignal(str)
        success = pyqtSignal()
        end = pyqtSignal()

        def __init__(self, window, item, target, args):
            super().__init__()
            self._window = window
            self._item = item
            self._target = target
            self._args = args

        def run(self):
            try:
                self._target(self._window, self._item, self.success, self.error, *self._args)
            finally:
                self.end.emit()


class ItemShowWidget(QWidget):
    """
    Widget with 1 "label" top,
    1 "widget" middle,
    2 buttons "buttonLeft", "buttonRight" bottom
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(self)
        self.label.setText("Label")

        self.frame_label = QFrame(self)
        self.frame_label.setFrameShape(QFrame.StyledPanel)
        self.frame_label.setFrameShadow(QFrame.Raised)

        self.label_layout = QHBoxLayout(self.frame_label)
        self.label_layout.setContentsMargins(6, 1, 1, 1)
        self.label_layout.addWidget(self.label)
        self.main_layout.addWidget(self.frame_label)

        self.widget = QWidget(self)
        # self.widget.setStyleSheet("border: 1px solid red")
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(size_policy)
        self.main_layout.addWidget(self.widget)

        self.frame_button = QFrame(self)
        self.frame_button.setFrameShape(QFrame.StyledPanel)
        self.frame_button.setFrameShadow(QFrame.Raised)

        self.button_layout = QHBoxLayout(self.frame_button)
        self.button_layout.setContentsMargins(6, 0, 6, 6)

        self.buttonLeft = QPushButton(self.frame_button)
        self.buttonLeft.setText("Left")
        self.button_layout.addWidget(self.buttonLeft)

        self.buttonRight = QPushButton(self.frame_button)
        self.buttonRight.setText("Right")
        self.button_layout.addWidget(self.buttonRight)

        self.main_layout.addWidget(self.frame_button)

        self._right_click_callback = lambda: None
        self._left_click_callback = lambda: None

        self._on_right_clicked = lambda: self._right_click_callback()
        self._on_left_clicked = lambda: self._left_click_callback()
        self.buttonRight.clicked.connect(self._on_right_clicked)
        self.buttonLeft.clicked.connect(self._on_left_clicked)

    def setButtonRightClicked(self, callback):
        self._right_click_callback = callback

    def setButtonLeftClicked(self, callback):
        self._left_click_callback = callback


class DialogShow(QDialog):
    def __init__(self, number_thread):
        super().__init__(None)
        self.setWindowTitle("Show")
        self.showMaximized()
        self.show()
        self.update()
        QApplication.processEvents()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.table = TableShow(self)
        self.table.setNumberThreads(number_thread)
        self.main_layout.addWidget(self.table)
        self._nb_thread = number_thread

    def start(self, target, args):
        for i in range(self._nb_thread):
            item = ItemShowWidget(self.table)
            self.table.setItem(i, item)
        self.table.run(target, args)
