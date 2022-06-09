from PyQt5.QtWidgets import QApplication, QMainWindow
from widgets import DialogShow
import sys
import time
from selenium_modules import chrome_in_window
import chromedriver_autoinstaller


chromedriver_autoinstaller.install()


def test(window, item, success, error, *args):

    def on_click():
        print("clicked")
        nonlocal running
        running = False

    try:
        running = True
        item.label.setText("test")
        item.buttonRight.setText("Exit")
        item.setButtonRightClicked(on_click)
        driver = chrome_in_window(window, scale=0.3)
        driver.get("https://www.google.com")
        while running:
            time.sleep(.1)
        driver.quit()
    except Exception:
        error.emit()
    else:
        success.emit()

def on_end():
    print(d.table.successCount())
    d.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    d = DialogShow(6)
    d.table.end.connect(on_end)
    d.start(test, tuple())
    app.exec_()