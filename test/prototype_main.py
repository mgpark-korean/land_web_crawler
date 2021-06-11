import time

import xlsxwriter
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from driver.DriverUtils import DriverUtils

webdriver = DriverUtils()
webdriver.connect('https://new.land.naver.com/complexes?ms=37.3575749,127.1179303,16&a=APT:JGC:ABYG&e=RETAIL', 5)

wait = WebDriverWait(webdriver.driver(), 5)

wait.until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[data-nclk="MAP.sectorCmark"]'))
)

parsedLandList = []
# 아파트명 / 세대수 / 입주일 / 매매가 / 전세가 / 매물수 / 층수
landElementList = webdriver.driver().find_elements_by_css_selector('a[data-nclk="MAP.sectorCmark"]')
for landElement in landElementList:
    # ActionChains(driver).move_by_offset(landElement.location.get('x'), landElement.location.get('y')).perform()
    try:
        webdriver.move_to_click_element(landElement)
        # landID = landElement.get_attribute('id')
        # wait.until(EC.presence_of_element_located((By.ID, landID)))
        # ActionChains(driver).move_to_element(landElement).click(landElement).perform()
        wait.until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, '.complex_infos')))

        landElement.find_element_by_class_name('complex_title')

        if landElement.find_element_by_class_name('complex_title'):
            # 매물 이름(아파트명)
            complexTitle = landElement.find_element_by_class_name('complex_title').text
            articleQtyList = landElement.find_elements_by_class_name('article_link')
            for articleQty in articleQtyList:
                # 매매, 전세 구분
                buyingType = articleQty.find_element_by_class_name('type').text
                # 매물수
                articleCnt = articleQty.find_element_by_class_name('count').text
                if buyingType in ['매매', '전세']:
                    webdriver.move_to_click_element(articleQty)
                    # ActionChains(driver).click(articleQty).perform()

                    # wait.until(
                    #     EC.presence_of_element_located((By.ID, 'complexOverviewList'))
                    # )
                    overViewList = webdriver.driver().find_element_by_id('complexOverviewList')
                    scrollDivElement = overViewList.find_element_by_class_name('item_list')
                    lastScrollHeight = 0

                    # 스크롤 다운
                    while True:
                        webdriver.driver().execute_script(
                            'let scrollDiv = document.querySelector("#complexOverviewList .item_list"); scrollDiv.scrollTo(0, scrollDiv.scrollHeight)')
                        time.sleep(0.3)
                        newScrollHeight = webdriver.driver().execute_script(
                            'return document.querySelector("#complexOverviewList .item_list").scrollHeight')
                        if lastScrollHeight == newScrollHeight:
                            break
                        lastScrollHeight = newScrollHeight

                    # 세대수
                    numOfHouse = overViewList.find_elements_by_css_selector('.complex_feature dd:nth-child(2)')[0].text

                    for item in overViewList.find_elements_by_class_name('item'):
                        webdriver.move_to_click_element(item)
                        detailItemWrap = webdriver.driver().find_element_by_class_name('detail_contents')

                        # wait.until(
                        #     EC.visibility_of_element_located((By.CSS_SELECTOR, 'detail_contnts .info_title_wrap > .info_title'))
                        # )

                        # 층수
                        floorInfo = detailItemWrap.find_elements_by_css_selector('.info_title_wrap > .info_title')[
                            0].text.replace(complexTitle, '')

                        # 입주일
                        moveDate = detailItemWrap.find_elements_by_css_selector(
                            '.info_table_wrap tr:nth-child(8) td:nth-child(2)')[0].text

                        # 매매가 / 전세가
                        price = detailItemWrap.find_elements_by_css_selector('.info_article_price > .price')[0].text
                        # 수집 정보 배열에 추가
                        parsedLandList.append({
                            'title': complexTitle,
                            'numOfHouse': numOfHouse,
                            'moveDate': moveDate,
                            'buyingType': buyingType,
                            'price': price,
                            'qty': articleCnt,
                            'floorInfo': floorInfo
                        })

    except StaleElementReferenceException:
        continue

workbook = xlsxwriter.Workbook('naver_land_crawling.xlsx')
worksheet = workbook.add_worksheet()

row = 0
worksheet.write(row, 1, '매물명')
worksheet.write(row, 2, '세대수')
worksheet.write(row, 3, '입주가능일')
worksheet.write(row, 4, '매매/전세')
worksheet.write(row, 5, '가격')
worksheet.write(row, 6, '개수')
worksheet.write(row, 7, '층수')

row += 1

for landItem in parsedLandList:
    worksheet.write(row, 1, landItem.get('title'))
    worksheet.write(row, 2, landItem.get('numOfHouse'))
    worksheet.write(row, 3, landItem.get('moveDate'))
    worksheet.write(row, 4, landItem.get('buyingType'))
    worksheet.write(row, 5, landItem.get('price'))
    worksheet.write(row, 6, landItem.get('qty'))
    worksheet.write(row, 7, landItem.get('floorInfo'))
    row += 1

workbook.close()
print(parsedLandList)
