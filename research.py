# Importing Selenium WebDriver to interact with the browser
import os
import time
from functools import wraps
from pprint import pprint
from typing import Callable

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options

# Service class introduced in Selenium 4 for managing driver installation, opening, and closing
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# Used for setting wait times
from selenium.webdriver.support.ui import WebDriverWait
from termcolor import colored, cprint

# ChromeDriverManager is used to install the driver without manually downloading the binary file
from webdriver_manager.chrome import ChromeDriverManager


def initialize_web_driver(site: str) -> webdriver.Chrome:
    """
    Initializes the Selenium WebDriver for Chrome and opens the target website.

    Args:
        site: str "http://localhost:3000/"

    Returns:
        webdriver.Chrome: An instance of the Chrome WebDriver.
    """
    options = Options()
    # Отключить уведомления
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)
    # Установка драйвера или что-то подобное
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(site)
    driver.set_window_size(1920, 1080)
    # Implicit wait for all elements
    driver.implicitly_wait(7)
    # wait = WebDriverWait(driver, 10)
    # wait.until(EC.visibility_of_element_located((By.TAG_NAME, "html")))
    return driver


def perform_authorization(login, password) -> webdriver.Chrome:
    driver = initialize_web_driver("https://system.asite.com/login")
    # driver.fullscreen_window()  # ! Не раскрывает окно для людей, но для Selenium это работает
    # Раскрываем браузер на весь экран монитора
    driver.set_window_size(1920, 1080)
    wait = WebDriverWait(driver, 10)
    # If there is an iframe then need to switch to it
    iframe = wait.until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id="iFrameAsite"]'))
    )
    # Switch to iframe
    driver.switch_to.frame(iframe)
    # print(f"Найдено iframe: {len(iframes)}")
    btn_login_xpath: str = '//*[@id="_58_login"]'
    btn_password_xpath: str = '//*[@id="_58_password"]'
    btn_submit_xpath: str = '//*[@id="login-cloud"]'
    # btn_login_el = driver.find_element(By.XPATH, btn_login_xpath)
    # btn_login_el.send_keys(login)
    input_login_el = wait.until(
        EC.visibility_of_element_located((By.XPATH, btn_login_xpath))
    )
    input_password_el = wait.until(
        EC.visibility_of_element_located((By.XPATH, btn_password_xpath))
    )
    btn_submit_el = wait.until(
        EC.visibility_of_element_located((By.XPATH, btn_submit_xpath))
    )
    input_login_el.send_keys(login)
    input_password_el.send_keys(password)
    btn_submit_el.click()
    # Switch driver focus back to main page (outside all iframes)
    driver.switch_to.default_content()
    # btn_login_el.clear()
    return driver


def check_session(func):
    """
    DECORATOR for check status session.
    """

    @wraps(func)
    def wrapper(driver, *args, **kwargs):
        """
        Проверяет, авторизован ли клиент. Если нет - выполняет авторизацию заново.

        Returns:
            webdriver.Chrome - актуальный экземпляр драйвера (перезапущенный при необходимости).
        """
        login = "andrii.khoroshchak@leemarley.com"
        password = "1992d1992D!"
        try:
            # if "login" in driver.current_url or driver.title == "Unauthorised":
            if driver.title == "Unauthorised":
                print(
                    colored("Сессия недействительна. Повторная авторизация...", "red")
                )
                driver.quit()  # Закрываем старый драйвер
                driver = perform_authorization(login, password)
            # else:
            #     print(colored("Сессия активна.", "green"))
        except Exception as err:
            print(colored(f"Ошибка при проверке сессии: {err}", "red"))
            # Выйти из старого драйвера, где был сбой
            driver.quit()
            # Авторизоваться на сайте заново
            driver = perform_authorization(login, password)
        return func(driver, *args, **kwargs)

    return wrapper


@check_session
def click_btn_more(driver):
    btn_more_xpath = '//*[@id="header_moreNav"]'
    wait = WebDriverWait(driver, 10)
    btn_more_el = wait.until(
        EC.visibility_of_element_located((By.XPATH, btn_more_xpath))
    )
    btn_more_el.click()
    return driver


@check_session
def click_btn_quality(driver):
    btn_quality_xpath = '//*[@id="navquality"]'
    wait = WebDriverWait(driver, 5)
    btn_quality_el = wait.until(
        EC.visibility_of_element_located((By.XPATH, btn_quality_xpath))
    )
    btn_quality_el.click()
    return driver


@check_session
def click_new_malden_quality_plan(driver):
    wait = WebDriverWait(driver, 5)
    new_malden_xpath = '//*[@id="qualities-list"]/div/div/adoddle-table-listing/div/div[2]/div[2]/div/ul[1]/li[2]/a'
    new_malden_el = wait.until(
        EC.visibility_of_element_located((By.XPATH, new_malden_xpath))
    )
    new_malden_el.click()
    return driver


@check_session
def set_color_to_element(driver, element, color: str = "#5cc695") -> webdriver.Chrome:
    original_style = element.get_attribute("style")
    # Подсветить активный элемент
    driver.execute_script(
        "arguments[0].setAttribute('style', arguments[1]);",
        element,
        f"background: {color}",
    )
    time.sleep(1)
    # Возврат к оригинальному стилю
    driver.execute_script(
        "arguments[0].setAttribute('style', arguments[1]);", element, original_style
    )
    return driver


def insert_data_into_field(field, data: str):
    # Получаем поле ввода input_contractors_q_a_form_ref_numb и заполняем его
    field.clear()
    field.send_keys(data)


@check_session
def edit_form(driver):
    wait = WebDriverWait(driver, 12)
    # Получаем кнопку для редактирования формы
    btn_edit_form_xpath = '//*[@id="edit-ori-btn"]/i'
    btn_edit_form = wait.until(
        EC.element_to_be_clickable((By.XPATH, btn_edit_form_xpath))
    )
    btn_edit_form.click()
    WebDriverWait(driver, 7).until(
        EC.presence_of_element_located((By.TAG_NAME, "html"))
    )
    xpaths = {
        "ref_numb": '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[1]/div/div/div[1]/div/div[2]/div/div/div/input',
        "form_name_title": '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[1]/div/div/div[2]/div/div[2]/div/div/div/input',
        "contract_cert": '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[1]/div/div/div[3]/div/div[2]/div/div/div/input',
        "area_of_inspection": '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[1]/div/div/div[4]/div/div[2]/div/div/div/input',
        "check_comment_field": '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[2]/div/div[8]/div/div[2]//div[contains(@class, "comment-section")]',
    }

    wait = WebDriverWait(driver, 7)
    contractors_q_a_form_ref_numb_xpath = xpaths["ref_numb"]
    contractors_q_a_form_name_title_xpath = xpaths["form_name_title"]
    contract_cert_xpath = xpaths["contract_cert"]
    area_of_inspection_xpath = xpaths["area_of_inspection"]
    check_comment_field_xpath = xpaths["check_comment_field"]
    # ! Заполнить поле ввода contractors_q_a_form_ref_numb_xpath
    # Contractor’s Quality Assurance form reference number
    contractors_q_a_form_ref_numb = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, contractors_q_a_form_ref_numb_xpath)
        )
    )
    if len(contractors_q_a_form_ref_numb.get_attribute("value")) <= 2:
        insert_data_into_field(contractors_q_a_form_ref_numb, "BMS01.G01")

    # ! Заполнить поле ввода contractors_q_a_form_name_title
    # Contractor’s Quality Assurance form name/title
    contractors_q_a_form_name_title = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, contractors_q_a_form_name_title_xpath)
        )
    )
    if len(contractors_q_a_form_name_title.get_attribute("value")) <= 2:
        insert_data_into_field(contractors_q_a_form_name_title, "Quality policy")

    # ! Заполнить поле ввода contract_cert
    # Contractor’s certification body
    contract_cert = wait.until(
        EC.visibility_of_element_located((By.XPATH, contract_cert_xpath))
    )
    if len(contract_cert.get_attribute("value")) <= 2:
        insert_data_into_field(contract_cert, "IFC Certificate number: IFCC 3054")

    # ! Заполнить поле ввода area_of_inspection
    # Area of inspection (please note the gridlines or structural elements to locate this area and floor/level)
    area_of_inspection = driver.find_element(By.XPATH, area_of_inspection_xpath)
    if len(area_of_inspection.get_attribute("value")) <= 2:
        location_site_area_xpath = (
            '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/div[1]/div[3]/input'
        )
        location_site_area_input = driver.find_element(
            By.XPATH, location_site_area_xpath
        )
        driver.execute_script(
            "arguments[0].removeAttribute('disabled')", location_site_area_input
        )
        location_site_area_raw_text = location_site_area_input.get_attribute("value")
        location_site_area_text = " ".join(location_site_area_raw_text.split(">"))
        insert_data_into_field(area_of_inspection, location_site_area_text)

    # ! Проверяем поле ввода check_comment_field
    # 2.1 Confirm that a copy of the contractor’s Project Quality Plan
    check_comment_field = driver.find_elements(By.XPATH, check_comment_field_xpath)
    # print(f"{len(check_comment_field)=}")
    # Если нет комментариев
    if len(check_comment_field) == 0:
        # Найти кнопку создания комментария
        btn_create_comment_xpath = '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[2]/div/div[8]/div/div[1]/div[2]/div[1]/div[2]/button'
        btn_create_comment = wait.until(
            EC.element_to_be_clickable((By.XPATH, btn_create_comment_xpath))
        )
        # Проскролить к кнопке чтобы её было видно и кликнуть по ней
        actions = ActionChains(driver)
        actions.scroll_to_element(btn_create_comment).perform()
        actions.scroll_by_amount(0, 200).perform()
        btn_create_comment.click()
        # Находим поле комментариев
        field_to_insert_comment_xpath = '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[2]/div/div[8]/div/div[2]//div[contains(@class, "comment-section")]/div[2]/textarea'
        field_to_insert_comment = driver.find_element(
            By.XPATH, field_to_insert_comment_xpath
        )
        # Вставляем данные в комментарии
        insert_data_into_field(
            field_to_insert_comment,
            "ITP and PQP uploaded on Asite\n"
            "H8499-LEM-SW-ZZ-QA-CT-19715 PQP\n"
            "H8499-LEM-SW-ZZ-QA-CO-LM123 ITP\n",
        )
    time.sleep(1)
    # Получаем кнопку "Update" и делаем на ней клик
    btn_update_xpath = '//*[@id="btnSaveForm"]'
    btn_update = wait.until(EC.element_to_be_clickable((By.XPATH, btn_update_xpath)))
    btn_update.click()
    # Ждем пока страница обновится после нажатия кнопки
    wait.until(
        EC.text_to_be_present_in_element_attribute(
            (By.XPATH, "//*[@id='formWrapper']/div[2]"), "class", "loaded"
        )
    )
    return driver


@check_session
def processs_form_qc4j_side_rise_rain_screen_firebreak(driver):
    project_title_xpath = '//*[@id="header-section"]/div[1]/h3'
    wait = WebDriverWait(driver, 10)
    project_title = wait.until(
        EC.visibility_of_element_located((By.XPATH, project_title_xpath))
    )
    # Проверить является ли страница редактируемой
    try:
        is_not_editable_inspection_xpath = (
            '//*[@id="form-holder"]/div[1]/div[2]/div/div'
        )
        is_not_editable_inspection = WebDriverWait(driver, 1).until(
            EC.visibility_of_element_located(
                (By.XPATH, is_not_editable_inspection_xpath)
            )
        )
    except Exception:
        # Если элемента is_not_editable_inspection_xpath нет на странице, значит она редактируемая
        is_not_editable_inspection = False
    else:
        # Если страница не редактируемая то закрыть её и вернуться на главную страницу
        print(f"{bool(is_not_editable_inspection)=}")
        main_tab = driver.window_handles[0]
        driver.close()
        driver.switch_to.window(main_tab)
        return driver
    # Проверить что открыта форма правильного столбца
    if "qc4j side-rise rain-screen firebreak" in project_title.text.lower():
        # Contractor’s Quality Assurance form reference number
        form_number_xpath = '//*[@id="formWrapper"]/div[2]/section[2]/section[1]/div/div/div[1]/div/div[2]/div/div/div'
        # form_number = wait.until(
        #     EC.visibility_of_element_located((By.XPATH, form_number_xpath))
        # )
        form_number = driver.find_element(By.XPATH, form_number_xpath)

        # Contractor’s Quality Assurance form name/title
        form_name_title_xpath = '//*[@id="formWrapper"]/div[2]/section[2]/section[1]/div/div/div[2]/div/div[2]/div/div/div'
        # form_name = wait.until(
        #     EC.visibility_of_element_located((By.XPATH, form_name_xpath))
        # )
        form_name_title = driver.find_element(By.XPATH, form_name_title_xpath)

        # Contractor’s certification body
        contract_cert_xpath = '//*[@id="formWrapper"]/div[2]/section[2]/section[1]/div/div/div[3]/div/div[2]/div/div/div'
        # contract_cert = wait.until(
        #     EC.visibility_of_element_located((By.XPATH, contract_cert_xpath))
        # )
        contract_cert = driver.find_element(By.XPATH, contract_cert_xpath)

        # Area of inspection (please note the gridlines or structural elements to locate this area and floor/level)
        area_of_inspect_xpath = '//*[@id="formWrapper"]/div[2]/section[2]/section[1]/div/div/div[4]/div/div[2]/div/div/div'
        # area_of_inspect = wait.until(
        #     EC.visibility_of_element_located((By.XPATH, area_of_inspect_xpath))
        # )
        area_of_inspect = driver.find_element(By.XPATH, area_of_inspect_xpath)

        # 2.1 Confirm that a copy of the contractor’s Project Quality Plan
        comment_xpath = '//*[@id="formWrapper"]/div[2]/section[2]/section[2]/div/div[8]//div[contains(@class, "comment-section")]'
        comments = driver.find_elements(By.XPATH, comment_xpath)
        # Проверяем поля ввода на отсутствие текста
        elements_to_check_for_edit = (
            form_number,
            form_name_title,
            contract_cert,
            area_of_inspect,
            comments,
        )
        is_edit = any(
            len(element) == 0 if type(element) is list else len(element.text) <= 2
            for element in elements_to_check_for_edit
        )
        # Если хоть одне полне не заполнено, а содержит лишь точку и возможно пробел то редактировать
        if is_edit:
            # ВНЕСЕНИЕ ИНФЫ В ФОРМУ
            driver = edit_form(driver)
        # Переключиться на главную страницу
        main_tab = driver.window_handles[0]
        driver.close()
        driver.switch_to.window(main_tab)
    return driver


@check_session
def get_location_title(driver, number_line):
    """
    Функция получает название объекта в таблице сайта (дом или этаж или квартира)
    """
    wait = WebDriverWait(driver, 20)
    location_cell_xpath = (
        f'//*[@id="table_body_header_scroller"]/div/div[{number_line}]'
    )
    location_cell = wait.until(
        EC.visibility_of_element_located((By.XPATH, location_cell_xpath))
    )
    location_title = location_cell.find_element(
        By.CLASS_NAME, "location-title"
    ).get_attribute("title")
    return (driver, location_title)


@check_session
def click_arrow_to_open_block(driver, number_line):
    """
    Функция выполняет клик по стрелке в ячейках "Block N", где N - это номер блока.

    args:
        driver - драйвер Selenium
        number_line - номер рядка в таблице сайта
    """
    wait = WebDriverWait(driver, 10)
    arrow_open_block_xpath = (
        f'//*[@id="table_body_header_scroller"]/div/div[{number_line}]/div/i'
    )
    # Ждем пока элемент стрелка станет кликабельной
    arrow_open_block = wait.until(
        EC.element_to_be_clickable((By.XPATH, arrow_open_block_xpath))
    )
    # Кликаем по стрелке
    arrow_open_block.click()
    # Ждем пока в элементе появится класс chevron-up.
    # Это значит что список элементов раскрылся и можно дальше работать без time.sleep(6)
    wait.until(
        EC.text_to_be_present_in_element_attribute(
            (By.XPATH, arrow_open_block_xpath), "class", "chevron-up"
        )
    )

    return driver


@check_session
def click_arrow_to_open_level(driver, number_line):
    """
    Функция выполняет клик по стрелке в ячейках "Block N", где N - это номер блока.

    args:
        driver - драйвер Selenium
        number_line - номер рядка в таблице сайта
    """
    try:
        wait = WebDriverWait(driver, 5)
        arrow_open_level_xpath = (
            f'//*[@id="table_body_header_scroller"]/div/div[{number_line}]/div/i'
        )
        # Ждем пока элемент стрелка станет кликабельной
        arrow_open_level = wait.until(
            EC.element_to_be_clickable((By.XPATH, arrow_open_level_xpath))
        )
        # Кликаем по стрелке
        arrow_open_level.click()
        # Ждем пока в элементе появится класс chevron-up.
        # Это значит что список элементов раскрылся и можно дальше работать без time.sleep(6)
        wait.until(
            EC.text_to_be_present_in_element_attribute(
                (By.XPATH, arrow_open_level_xpath), "class", "chevron-up"
            )
        )
    except Exception:
        return driver
    return driver


@check_session
def click_card_in_progress(driver, element):
    element.find_element(By.CSS_SELECTOR, "span.ng-star-inserted")
    # Скрол до нужного элемента с Python или с Javascript
    # driver.execute_script("arguments[0].scrollIntoView(true);", btn_open_new_tab)
    ActionChains(driver).scroll_to_element(element).perform()
    time.sleep(1)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "span.ng-star-inserted"))
    )
    try:
        # Открыть форму в новой вкладке
        element.click()
    except ElementClickInterceptedException:
        print("Work ElementClickInterceptedException")
        # Используем JavaScript для клика, если элемент перекрыт
        driver.execute_script("arguments[0].click();", element)
    return driver


def get_letter_block_to_start() -> str:
    get_letter: bool = False
    block_letters: str = "ABCDEFG"
    while get_letter is False:
        letter_block_to_start: str = input(
            "Enter the letter of the 'block' from which you want to start automation.\n"
            "Press one letter from A, B, C, D, E, F, G on the keyboard.\n\n"
            "You can press the letter in any register - lowercase or uppercase.\n\n"
            "If you want the program to process everything from the very beginning, \n"
            "then you don't need to enter anything, just press the 'Enter' key.\n\n"
            "Please enter the block letter: "
        )
        if len(letter_block_to_start) > 0:
            print(f"\nYou enter letter_block_to_start: {letter_block_to_start}")
        # Если ввод пользователя одна буква из ABCDEFG или пользователь ничего не ввел то остановить цикл
        if (
            len(letter_block_to_start) == 1
            and letter_block_to_start.upper() in block_letters
        ):
            get_letter = True
            print(
                f"The program will start working from the block with the letter {letter_block_to_start}"
            )
        elif len(letter_block_to_start) == 0:
            get_letter = True
            print("The program will work from the beginning of the list.")
    return letter_block_to_start.lower()


def get_number_level_to_start() -> str:
    """
    Функция получает номер level с которого начинать работу.
    Форматирует number_level_to_start - добавляет 0 к значению переменной,
    если number_level_to_start состоит из одной цифры.
    Возвращает строкой цифры вида "01"
    """
    get_number_level: bool = False
    while get_number_level is False:
        number_level_to_start: str = input(
            "\nEnter the number of the 'level' from which you want to start automation.\n"
            "Press one number on the keyboard.\n\n"
            "If you want the program to process everything from the very beginning, \n"
            "then you don't need to enter anything, just press the 'Enter' key.\n\n"
            "Please enter the level number: "
        )
        if 1 <= len(number_level_to_start) <= 2 and number_level_to_start != "0":
            get_number_level = True
            print(f"\nYou enter number_level_to_start: {number_level_to_start}")
            print(
                f"The program will start working from the level with the number {number_level_to_start}"
            )
        elif len(number_level_to_start) == 0:
            get_number_level = True
            print("The program will work from the beginning of the list.")
        else:
            print(
                f"\nThe number that you enter {number_level_to_start} is not correct.\n"
            )
    return (
        "0" + number_level_to_start
        if len(number_level_to_start) == 1
        else number_level_to_start
    )


def get_number_plot_to_start():
    """
    Функция получает номер plot с которого начинать работу.
    Форматирует number_plot_to_start - добавляет 0 к значению переменной,
    если number_plot_to_start состоит из одной цифры.

    Возвращает тип данных строку в виде цифр "01", "09", "10" и т.д.
    """
    get_number_level = False
    while get_number_level is False:
        number_plot_to_start = input(
            "\nEnter the number of the 'plot' from which you want to start automation.\n"
            "Press one number on the keyboard.\n\n"
            "If you want the program to process everything from the very beginning, \n"
            "then you don't need to enter anything, just press the 'Enter' key.\n\n"
            "Please enter the plot number: "
        )
        if 1 <= len(number_plot_to_start) <= 3 and number_plot_to_start != "0":
            get_number_level = True
            print(f"\nYou enter number_plot_to_start: {number_plot_to_start}")
            print(
                f"The program will start working from the level with the number {number_plot_to_start}"
            )
        elif len(number_plot_to_start) == 0:
            get_number_level = True
            print("The program will work from the beginning of the list.")
        else:
            print(
                f"\nThe number that you enter {number_plot_to_start} is not correct.\n"
            )
    return (
        "0" + number_plot_to_start
        if len(number_plot_to_start) == 1
        else number_plot_to_start
    )


@check_session
def scroll_to_location_title(driver, number_line: int):
    wait = WebDriverWait(driver, 10)
    location_cell_xpath = (
        f'//*[@id="table_body_header_scroller"]/div/div[{number_line}]'
    )
    location_cell = wait.until(
        EC.visibility_of_element_located((By.XPATH, location_cell_xpath))
    )
    location_title = location_cell.find_element(By.CLASS_NAME, "location-title")
    # Скрол до нужного элемента с Python или с Javascript
    # driver.execute_script("arguments[0].scrollIntoView(true);", btn_open_new_tab)
    ActionChains(driver).scroll_to_element(location_title).perform()
    driver = set_color_to_element(driver, location_title, "#7ff6bf")
    return driver


@check_session
def switch_to_new_tab(driver):
    new_tab = driver.window_handles[1]
    # Переключаем контекст Selenium на новую вкладку
    driver.switch_to.window(new_tab)
    # Ждать загрузки страницы
    WebDriverWait(driver, 10).until(
        EC.visibility_of_all_elements_located((By.TAG_NAME, "html"))
    )
    return driver


@check_session
def click_select_form_action(driver, btn_select_form_action):
    # Скрол до нужного элемента с Python или с Javascript
    # driver.execute_script("arguments[0].scrollIntoView(true);", btn_open_new_tab)
    ActionChains(driver).scroll_to_element(btn_select_form_action).perform()
    # # time.sleep(0.5)
    # wait.until(EC.element_to_be_clickable((By.XPATH, btn_select_form_action_xpath)))
    try:
        # Открыть форму в новой вкладке
        btn_select_form_action.click()
    except ElementClickInterceptedException:
        print("Work ElementClickInterceptedException")
        # Используем JavaScript для клика, если элемент перекрыт
        driver.execute_script("arguments[0].click();", btn_select_form_action)
    return driver


def get_location_site_area(driver):
    location_site_area_xpath = (
        '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/div[1]/div[3]/input'
    )
    location_site_area_input = driver.find_element(By.XPATH, location_site_area_xpath)
    driver.execute_script(
        "arguments[0].removeAttribute('disabled')", location_site_area_input
    )
    location_site_area_raw_text = location_site_area_input.get_attribute("value")
    location_site_area_text = " ".join(location_site_area_raw_text.split(">"))
    return (driver, location_site_area_text)


@check_session
def click_btn_create_form(driver):
    wait = WebDriverWait(driver, 10)
    select_form_action = '//*[@id="subscriptionPlanId-2"]/ngb-modal-window'
    # Ждем пока появится модальное окно
    wait.until(
        EC.text_to_be_present_in_element_attribute(
            (By.XPATH, select_form_action), "class", "form-modal"
        )
    )
    btn_create_form_xpath = (
        '//*[@id="subscriptionPlanId-2"]/ngb-modal-window/div/div/div[2]/div[1]/img'
    )
    btn_create_form = wait.until(
        EC.visibility_of_element_located((By.XPATH, btn_create_form_xpath))
    )
    btn_create_form.click()
    return driver


@check_session
def get_field_to_insert_comment(driver):
    # Найти кнопку создания комментария
    btn_create_comment_xpath = '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[2]/div/div[8]/div/div[1]/div[2]/div[1]/div[2]/button'
    btn_create_comment = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, btn_create_comment_xpath))
    )
    # Проскролить к кнопке чтобы её было видно и кликнуть по ней
    actions = ActionChains(driver)
    actions.scroll_to_element(btn_create_comment).perform()
    actions.scroll_by_amount(0, 200).perform()
    btn_create_comment.click()
    # Находим поле комментариев
    field_to_insert_comment_xpath = '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[2]/div/div[8]/div/div[2]//div[contains(@class, "comment-section")]/div[2]/textarea'
    field_to_insert_comment = driver.find_element(
        By.XPATH, field_to_insert_comment_xpath
    )
    return (driver, field_to_insert_comment)


@check_session
def set_data_to_created_inspection(driver):
    wait = WebDriverWait(driver, 10)
    # Получить элемент календарь и кликнуть на нем чтобы он развернулся
    calendar_xpath = '//*[@id="custFormTD"]/div[2]/div/section[2]/div[2]/div[2]/datepicker/label/input[1]'
    calendar = wait.until(EC.visibility_of_element_located((By.XPATH, calendar_xpath)))
    actions = ActionChains(driver)
    actions.scroll_to_element(calendar).perform()
    actions.scroll_by_amount(0, 200).perform()
    calendar.click()

    month_select_xpath = "/html/body/div[5]/div[1]/div[3]/a[1]/span"
    month_select = wait.until(
        EC.element_to_be_clickable((By.XPATH, month_select_xpath))
    )
    month_select.click()

    september_xpath = "/html/body/div[5]/div[2]/a[9]"
    september = wait.until(EC.element_to_be_clickable((By.XPATH, september_xpath)))
    september.click()

    date_of_september_xpath = "/html/body/div[5]/div[5]/a[3]"
    date_of_september = wait.until(
        EC.element_to_be_clickable((By.XPATH, date_of_september_xpath))
    )
    date_of_september.click()
    return driver


@check_session
def fill_created_form(driver):
    wait = WebDriverWait(driver, 10)
    # Ждем пока прогрузится страница
    iframe_with_form = wait.until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='createFormIframe']"))
    )
    driver.switch_to.frame(iframe_with_form)

    xpaths = {
        "ref_numb": '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[1]/div/div/div[1]/div/div[2]/div/div/div/input',
        "form_name_title": '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[1]/div/div/div[2]/div/div[2]/div/div/div/input',
        "contract_cert": '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[1]/div/div/div[3]/div/div[2]/div/div/div/input',
        "area_of_inspection": '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[1]/div/div/div[4]/div/div[2]/div/div/div/input',
        "confirm_materials_stored_with_instructions": '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[1]/div/div/div[6]/div/div[2]/div/div/div/input',
    }

    # ! Заполнить поле ввода contractors_q_a_form_ref_numb_xpath
    # Contractor’s Quality Assurance form reference number
    contractors_q_a_form_ref_numb = wait.until(
        EC.visibility_of_element_located((By.XPATH, xpaths["ref_numb"]))
    )
    print(f"{dir(contractors_q_a_form_ref_numb)=}")
    insert_data_into_field(contractors_q_a_form_ref_numb, "BMS01.G01")

    # ! Заполнить поле ввода contractors_q_a_form_name_title
    # Contractor’s Quality Assurance form name/title
    contractors_q_a_form_name_title = wait.until(
        EC.visibility_of_element_located((By.XPATH, xpaths["form_name_title"]))
    )
    insert_data_into_field(contractors_q_a_form_name_title, "Quality policy")

    # ! Заполнить поле ввода contract_cert
    # Contractor’s certification body
    contract_cert = wait.until(
        EC.visibility_of_element_located((By.XPATH, xpaths["contract_cert"]))
    )
    insert_data_into_field(contract_cert, "IFC Certificate number: IFCC 3054")

    # ! Заполнить поле ввода area_of_inspection
    # Area of inspection (please note the gridlines or structural elements to locate this area and floor/level)
    area_of_inspection = driver.find_element(By.XPATH, xpaths["area_of_inspection"])
    driver, location_site_area_text = get_location_site_area(driver)
    insert_data_into_field(area_of_inspection, location_site_area_text)

    # ! WORK HERE !
    # ! Заполнить поле ввода confirm_materials_stored_with_instructions
    # Please confirm that the materials have been stored and protected in accordance with
    # manufacturer’s instructions and the Contractor’s Quality Management System
    confirm_materials_stored_with_instructions = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, xpaths["confirm_materials_stored_with_instructions"])
        )
    )
    insert_data_into_field(confirm_materials_stored_with_instructions, ".")

    # ! Заполнить поле ввода field_to_insert_comment
    # Confirm that a copy of the contractor’s Project Quality Plan (вставляем комментарии в это поле)
    driver, field_to_insert_comment = get_field_to_insert_comment(driver)
    insert_data_into_field(
        field_to_insert_comment,
        "ITP and PQP uploaded on Asite\n"
        "H8499-LEM-SW-ZZ-QA-CT-19715 PQP\n"
        "H8499-LEM-SW-ZZ-QA-CO-LM123 ITP\n",
    )

    # Установить дату в календаре 2 Сентября (на пол-года вперед).
    driver = set_data_to_created_inspection(driver)

    time.sleep(20)

    # Получаем кнопку "Update" и делаем на ней клик
    btn_update_xpath = '//*[@id="btnSaveForm"]'
    btn_update = wait.until(EC.element_to_be_clickable((By.XPATH, btn_update_xpath)))
    btn_update.click()
    # Ждем пока страница обновится после нажатия кнопки
    wait.until(
        EC.text_to_be_present_in_element_attribute(
            (By.XPATH, "//*[@id='formWrapper']/div[2]"), "class", "loaded"
        )
    )
    return driver


def edit_or_create_inspection(driver, number_line):
    """
    Функция определяет что делать - редактировать инспекцию или создавать с ноля.
    Возвращает
    """
    wait = WebDriverWait(driver, 10)
    element_xpath = (
        f'//*[@id="table_body_content_scroller"]/div/div[{number_line}]/div/div[36]'
    )
    btn_select_form_action_xpath = f'//*[@id="table_body_content_scroller"]/div/div[{number_line}]/div/div[36]/div/img'
    # '//*[@id="table_body_content_scroller"]/div/div[5]/div/div[36]'
    element = wait.until(EC.visibility_of_element_located((By.XPATH, element_xpath)))
    # Если элемент содержит надпись "in progress" то открыть её для редактирования
    if element.text and element.text.lower() == "in progress":
        return (driver, element, "edit")
    # Если элемент содержит изображение создания формы btn_select_form_action
    elif element.find_element(By.XPATH, btn_select_form_action_xpath):
        btn_select_form_action = wait.until(
            EC.visibility_of_element_located((By.XPATH, btn_select_form_action_xpath))
        )
        print(f"{btn_select_form_action=}")
        return (driver, btn_select_form_action, "create")
    raise Exception("Error in edit_or_create_inspection")


@check_session
def moving_through_quality_checklist(
    driver,
    number_line: int = 2,
    letter_block_to_start: str | bool = False,
    number_level_to_start: str | bool = False,
    number_plot_to_start: str | bool = False,
):
    """
    Функция перемещается по рядам таблицы сайта от 2-й и до конца.

    args:
        driver - драйвер Selenium
        number_line - номер рядка в таблице сайта
    """
    # Слово для остановки работы скрипта
    stop_word: bool = True
    while stop_word:
        # Получить название текущей ячейки - Block, Level (этаж), Plot (квартира)
        driver, location_title = get_location_title(driver, number_line)
        driver = scroll_to_location_title(driver, number_line)
        if type(location_title) is str:
            location_title = location_title.lower()
            print(f"{location_title=}, {number_line=}")
            # ! PROCESS SECTION Block
            if "block" in location_title:
                if not letter_block_to_start:
                    driver = click_arrow_to_open_block(driver, number_line)
                elif location_title == f"block {letter_block_to_start}":
                    letter_block_to_start = False
                    driver = click_arrow_to_open_block(driver, number_line)
            # ! PROCESS SECTION Level
            elif "level" in location_title:
                if not number_level_to_start:
                    driver = click_arrow_to_open_level(driver, number_line)
                elif location_title == f"level {number_level_to_start}":
                    number_level_to_start = False
                    driver = click_arrow_to_open_level(driver, number_line)
            # ! PROCESS SECTION Plot
            elif "plot" in location_title:
                if (
                    not number_plot_to_start
                    or location_title == f"plot {number_plot_to_start}"
                ):
                    # # Если 6-й этаж то скрипт остановиться
                    # # ! REMOVE THIS
                    # if location_title == "plot 06":
                    #     break
                    number_plot_to_start = False

                    driver, element, edit_or_create = edit_or_create_inspection(
                        driver, number_line
                    )
                    if edit_or_create == "edit":
                        driver = click_card_in_progress(driver, element)
                        # Если открыта новая (вторая) вкладка
                        if len(driver.window_handles) > 1:
                            # Переключиться на новую вкладку
                            driver = switch_to_new_tab(driver)
                            # Обрабоать страницу
                            driver = processs_form_qc4j_side_rise_rain_screen_firebreak(
                                driver
                            )
                    elif edit_or_create == "create":
                        # Клик на изображении создания формы, чтобы открыть окно опций
                        driver = click_select_form_action(driver, element)
                        # Клик на кнопке создать форму
                        driver = click_btn_create_form(driver)

                        # ! WORK HERE
                        # Заполнить форму данными (изображениями, документами)
                        driver = fill_created_form(driver)

                        time.sleep(5)
        number_line += 1
    return driver


def main() -> None:
    # Get login and password for autorization
    load_dotenv()
    site_login = os.getenv("SITE_LOGIN")
    site_password = os.getenv("SITE_PASSWORD")
    # Get letter block where script start working
    letter_block_to_start: str = get_letter_block_to_start()
    # Get number lever where script start working
    number_level_to_start: str = get_number_level_to_start()
    # Get number plot where script start working
    number_plot_to_start: str = get_number_plot_to_start()
    # Autorization
    driver_authorized = perform_authorization(site_login, site_password)
    driver_first_page = click_btn_more(driver_authorized)
    time.sleep(0.5)

    driver_quality_page = click_btn_quality(driver_first_page)

    driver = click_new_malden_quality_plan(driver_quality_page)

    driver = moving_through_quality_checklist(
        driver,
        letter_block_to_start=letter_block_to_start,
        number_level_to_start=number_level_to_start,
        number_plot_to_start=number_plot_to_start,
    )
    driver.quit()


if __name__ == "__main__":
    main()
