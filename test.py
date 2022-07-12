from PyQt5.QtWidgets import QApplication
from widgets import DialogShow
import sys
import time
from selenium_modules import chrome_in_window
import chromedriver_autoinstaller


chromedriver_autoinstaller.install()


class Test(object):
    def __init__(self):
        self.running = True

    def run(self, window, item, success, error):
        item.label.setText("test")
        item.buttonRight.setText("Exit")
        item.setButtonRightClicked(self._on_click)
        try:
            driver = chrome_in_window(window, scale=0.3)
            driver.get("https://www.google.com")
            while self.running:
                time.sleep(.2)
            driver.quit()
            success.emit()
        except Exception as e:
            error.emit(str(e))

    def _on_click(self):
        self.running = False


def on_end():
    print(d.table.successCount())
    d.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    d = DialogShow(6)
    d.table.end.connect(on_end)
    d.start(lambda *args: Test().run(*args), tuple())
    app.exec_()