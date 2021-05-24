from selenium import webdriver
from selenium.common.exceptions import MoveTargetOutOfBoundsException
from selenium.webdriver.common.action_chains import ActionChains
import time

driver = webdriver.Chrome('C:\\Users\\user\\PycharmProjects\\pythonProject\\chromedriver\\chromedriver.exe')
driver.get('https://new.land.naver.com/complexes?ms=37.3575749,127.1179303,16&a=APT:JGC:ABYG&e=RETAIL')
driver.maximize_window()
print("+" * 100)
print(driver.title)
print(driver.current_url)
print("naver land crolling")
print("-" * 100)

time.sleep(3)

parsedLandList = []
# 아파트명 / 세대수 / 입주일 / 매매가 / 전세가 / 매물수 / 층수
landElementList = driver.find_elements_by_css_selector('a[data-nclk="MAP.sectorCmark"]')
try:
    for landElement in landElementList:
        try:
            ActionChains(driver).move_by_offset(landElement.location.get('x'), landElement.location.get('y')).perform()
            # ActionChains.move_to_element(landElement).perform()
        except MoveTargetOutOfBoundsException:
            continue

        # 매물 이름(아파트 이름)
        complexTitle = landElement.find_element_by_class_name('complex_title').text
        if complexTitle != '':
            articleQtyList = landElement.find_elements_by_class_name('article_link')
            for articleQty in articleQtyList:
                buyingType = articleQty.find_element_by_class_name('type').text
                articleCnt = articleQty.find_element_by_class_name('count').text
                if buyingType in ['매매', '전세']:
                    articleQty.click()
                    time.sleep(0.3)
                    overViewList = driver.find_element_by_id('complexOverviewList')
                    # 세대수
                    numOfHouse = overViewList.find_elements_by_css_selector('.complex_feature dd:nth-child(2)')[
                        0].text

                    for item in overViewList.find_elements_by_class_name('item'):
                        item.click()
                        time.sleep(0.3)
                        detailItemWrap = driver.find_element_by_class_name('detail_contents')
                        floorInfo = detailItemWrap.find_elements_by_css_selector('.info_title_wrap > .info_title')[
                            0].text.replace(complexTitle, '')
                        moveDate = detailItemWrap.find_elements_by_css_selector('.info_table_wrap tr:nth-child(8) td:nth-child(2)')[0].text
                        priceInfoWrap = item.find_elements_by_css_selector('.price_line, .info_article_price ')[0]
                        price = priceInfoWrap.find_element_by_class_name('price').text
                        parsedLandList.append({
                            'title': complexTitle,
                            'numOfHouse': numOfHouse,
                            'moveDate': moveDate,
                            'buyingType': buyingType,
                            'price': price,
                            'qty': articleCnt,
                            'floorInfo': floorInfo
                        })

finally:
    print(parsedLandList)
