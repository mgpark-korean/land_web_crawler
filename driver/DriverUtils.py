import time
import chromedriver_autoinstaller
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver import ActionChains


class DriverUtils:
    options = webdriver.ChromeOptions()
    _driver = None

    def __init__(self):
        chromedriver_autoinstaller.install()
        self.options.add_argument('headless')  # headless 설정
        self.options.add_argument('window-size=1920x1080')  # 기본 창크키 설정
        ua = UserAgent(verify_ssl=False)
        self.options.add_argument(f'user-agent={ua.chrome}')
        self._driver = webdriver.Chrome(chrome_options=self.options)

    def connect(self, url, timeout):
        self._driver.implicitly_wait(timeout)
        self._driver.get(url)

    def move_to_click_element(self, element):
        try:
            if not element.is_displayed():
                time.sleep(2)

            ActionChains(self._driver).move_to_element(element).click(element).perform()
        except Exception:
            return

    @property
    def driver(self):
        return self._driver
