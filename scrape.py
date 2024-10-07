from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re


filteredDates = []
Arbeitszeiten = []
def login(driver):
    links = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(("xpath", "//input[@class='text-input__input']")))

    if links:
        input_email = driver.find_element("xpath", "//input[@type='email']")
        input_email.send_keys("your email")
        input_pass = driver.find_element("xpath", "//input[@type='password']")
        input_pass.send_keys("your password")
        time.sleep(1)
        signBtn = driver.find_element("xpath", "//input[@type='submit']")
        signBtn.click()

def einstempeln(driver):
    try:
        einstempeln = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(("xpath", "//button[contains(.,'Einstempeln')]")))
        einstempeln.click()

    except:
        print("Bereits Eingestempelt")


def filterZellText(cellData):
    lines = cellData.split('\n')
    lines = [data for data in lines if data.strip() not in ["Hinzufügen", "0h 00m", "/", "Kategorie", "Jetzt", "Zeit", "–", ""]]
    if lines:
        for line in lines:
            if line == '1':
                return
        try:
            filteredDates.append(lines[0] + lines[1])
        except:
            filteredDates.append(lines[0])

    else:
        return


def filterTwo(filteredDates):
    result = []
    prevElement = None
    for date in filteredDates:

        if date == 'Arbeit' and prevElement == 'Arbeit':
            continue
        singleDigit(date)
        result.append(singleDigit(date))
        prevElement = date
    return result

def clockInData(driver):
    month = str(datetime.date.today().month)
    year = str(datetime.date.today().year)

    url = f"https://app.factorialhr.com/attendance/clock-in/{year}/{month}"
    driver.get(url)

    aufklappen = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(("xpath", "//button[contains(.,'Alle aufklappen')]")))
    aufklappen.click()
    getZeiten(driver)

def singleDigit(date):
    dateSplit = date.split(' ')
    if(len(dateSplit[0])== 1):
        dateSplit[0] = '0' + dateSplit[0]
        newDate = ' '.join(dateSplit)
        return newDate

    else:
        return date

def getZeiten(driver):
    try:
        timetable = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        arr = []

        rows = timetable.find_elements(By.TAG_NAME, "tr")
        for row_index, row in enumerate(rows):
            cells = row.find_elements(By.TAG_NAME, "td")

            for cell in cells:
                try:
                    times = cell.find_elements(By.XPATH, ".//input")
                    for time in times:
                        value = time.get_attribute("value")
                        arr.append(value)
                except:
                    print("No input element found")
                filterZellText(cell.text)

        try:

            for i in range(0, len(arr), 6):
                if arr[i] == arr[i + 1]:
                    Arbeitszeiten.append(arr[i])
                    break
                uhrzeiten = f'{arr[i]} - {arr[i+1]}'
                Arbeitszeiten.append(uhrzeiten)

        except:
            print("out of bounds")


    except:
        print("No Table found or invalid")

def combineDateTime(Arbeitszeiten, Dates):
    with open('C:/Users/geilke/Stundenzettel/zeiten.txt', 'w') as file:
        zeit = 0
        for date in range(0,len(Dates), 1):
            try:
                if Dates[date+1] == 'Arbeit':
                    print(Dates[date] + " " + Arbeitszeiten[zeit])
                    file.write(Dates[date] + " " + Arbeitszeiten[zeit] + '\n')
                    zeit += 1
            except:
                continue

def main():
    options = Options()
    options.add_experimental_option("detach", True)
    options.add_argument("--headless=old")
    options.add_argument("--disable-search-engine-choice-screen")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://app.factorialhr.com/dashboard")
    #driver.maximize_window()
    login(driver)
    einstempeln(driver)
    clockInData(driver)
    combineDateTime(Arbeitszeiten, filterTwo(filteredDates))
    driver.close()


if __name__ == '__main__':

    main()