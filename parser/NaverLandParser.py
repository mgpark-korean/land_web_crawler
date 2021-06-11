import time
from telnetlib import EC

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from driver.DriverUtils import DriverUtils


class NaverLandParser:
    __TIME_OUT = 5
    __connect_url = ''

    @property
    def connect_url(self):
        return self.__connect_url

    @connect_url.setter
    def connect_url(self, value):
        self.__connect_url = value

    # 네이버 지도에서 파싱해야하는 maker의 ID를 리스트로 반환
    # 추후 이를 이용해 멀티 프로세스 수행 예정
    def get_marker_id_list(self, url):
        driver_utils = DriverUtils()
        driver_utils.connect(url, self.__TIME_OUT)
        wait = WebDriverWait(driver_utils.driver, 5)

        wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[data-nclk="MAP.sectorCmark"]'))
        )

        # 아파트명 / 세대수 / 입주일 / 매매가 / 전세가 / 매물수 / 층수
        landElementList = driver_utils.driver.find_elements_by_css_selector('a[data-nclk="MAP.sectorCmark"]')

        land_id_list = []
        for land in landElementList:
            land_id_list.append(land.get_attribute('id'))

        driver_utils.driver.quit()
        return land_id_list

    # 파싱한 Marker에서 부동산 필요 정보를 수집함
    def parse_land_info(self, url, land_id_list):
        driver_utils = DriverUtils()
        driver_utils.connect(url, self.__TIME_OUT)
        driver = driver_utils.driver

        wait = WebDriverWait(driver_utils.driver, 5)

        parsedLandList = []
        for land_id in land_id_list:
            land_marker = driver.find_element_by_id(land_id)
            driver_utils.move_to_click_element(land_marker)
            wait.until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, '.complex_infos')))

            title_element = land_marker.find_element_by_class_name('complex_title')
            if title_element:
                title = title_element.text
                qty_elements = land_marker.find_elements_by_class_name('article_link')

                for qty_element in qty_elements:
                    # 매매, 전세 구분
                    buying_type = qty_element.find_element_by_class_name('type').text
                    # 매물수
                    article_cnt = qty_element.find_element_by_class_name('count').text
                    if buying_type in ['매매', '전세']:
                        driver.move_to_click_element(qty_element)

                        over_view_list = driver.find_element_by_id('complexOverviewList')
                        scrollDivElement = over_view_list.find_element_by_class_name('item_list')
                        last_scroll_height = 0

                        # 스크롤 다운
                        while True:
                            driver.execute_script(
                                'let scrollDiv = document.querySelector("#complexOverviewList .item_list"); '
                                'scrollDiv.scrollTo(0, scrollDiv.scrollHeight)')
                            time.sleep(0.3)
                            new_scroll_height = driver.execute_script(
                                'return document.querySelector("#complexOverviewList .item_list").scrollHeight')
                            if last_scroll_height == new_scroll_height:
                                break
                            last_scroll_height = new_scroll_height

                        # 세대수
                        num_of_house = over_view_list.find_elements_by_css_selector('.complex_feature dd:nth-child(2)')[0].text

                        for item in over_view_list.find_elements_by_class_name('item'):
                            driver.move_to_click_element(item)
                            detailItemWrap = driver.find_element_by_class_name('detail_contents')

                            # 층수
                            floor_info = detailItemWrap.find_elements_by_css_selector('.info_title_wrap > .info_title')[
                                0].text.replace(title, '')

                            # 입주일
                            move_date = detailItemWrap.find_elements_by_css_selector(
                                '.info_table_wrap tr:nth-child(8) td:nth-child(2)')[0].text

                            # 매매가 / 전세가
                            price = detailItemWrap.find_elements_by_css_selector('.info_article_price > .price')[
                                0].text
                            # 수집 정보 배열에 추가
                            parsedLandList.append({
                                'title': title,
                                'numOfHouse': num_of_house,
                                'moveDate': move_date,
                                'buyingType': buying_type,
                                'price': price,
                                'qty': article_cnt,
                                'floorInfo': floor_info
                            })
