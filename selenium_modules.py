from module import Window
from selenium import webdriver
import psutil


def chrome_in_window(window, executable_path="chromedriver", options=webdriver.ChromeOptions(), title_size=77, scale=1):
    options.add_argument("--force-device-scale-factor=" + str(scale))
    driver = webdriver.Chrome(executable_path=executable_path, options=options)
    for child in psutil.Process(driver.service.process.pid).children():
        if child.name() == "chrome.exe":
            pid = child.pid
            break
    else:
        raise
    wins = Window.from_pid(pid)
    for win in wins:
        window.attack_child(win)
        size = window.size
        driver.set_window_rect(-5, -1 * title_size, size[0] // scale + 10, size[1] // scale + title_size + 5)
    return driver
