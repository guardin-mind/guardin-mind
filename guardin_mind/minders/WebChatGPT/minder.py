from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions as selexcept
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ActionChains
import tomllib
from webdriver_manager.chrome import ChromeDriverManager
import functools
import os
import time
from pathlib import Path
import sys
import undetected_chromedriver as uc
import pyperclip
from .logger import *

UNTITLED_PLACEHOLDER = '[recently generated chat]'

def driver_refresh(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        self.driver.implicitly_wait(self.wait_sec)
        time.sleep(1)
        try:
            return func(self, *args, **kwargs)
        except selexcept.WebDriverException as e:
            if str(e).strip() == 'Message: disconnected: not connected to DevTools':
                self.logger.warning('WebDriver timed out. Refreshing page')
                self.driver.refresh()
                self.driver.implicitly_wait(self.wait_sec)
                if self.selected_chat != None:
                    if self.selected_chat == UNTITLED_PLACEHOLDER:
                        self.select_latest_chat()
                    else:
                        self.select_chat(self.selected_chat)
                return func(self, *args, **kwargs)  
            else:
                raise e  
    return wrapper

prev_answer_count = 0

class ChatMain:
    @driver_refresh
    def completion(self, prompt, mode="standard"):
        global prev_answer_count

        def fast_scroll_down(driver, scroll_steps=30, scroll_amount=100):
            # Наводим курсор на центр окна (условно, через JS)
            driver.execute_script("""
                // Создаём невидимый элемент в центре и фокусируемся на него
                let centerElem = document.createElement('div');
                centerElem.style.position = 'fixed';
                centerElem.style.top = '50%';
                centerElem.style.left = '50%';
                centerElem.style.width = '1px';
                centerElem.style.height = '1px';
                centerElem.style.zIndex = '999999';
                centerElem.style.background = 'transparent';
                document.body.appendChild(centerElem);
                centerElem.focus();
            """)

            # Функция для генерации события колесика мыши
            scroll_script = """
                function triggerWheel(yDelta) {
                    let event = new WheelEvent('wheel', {
                        deltaY: yDelta,
                        bubbles: true,
                        cancelable: true,
                        view: window
                    });
                    document.dispatchEvent(event);
                }
                for (let i = 0; i < arguments[0]; i++) {
                    triggerWheel(arguments[1]);
                }
            """

            # Выполняем скролл
            driver.execute_script(scroll_script, scroll_steps, scroll_amount)

            # Удаляем временный элемент
            driver.execute_script("""
                let centerElem = document.querySelector('div[style*="z-index: 999999"]');
                if(centerElem) centerElem.remove();
            """)

        actions = ActionChains(self.driver)
        try:
            # Находим элемент для вставки текста
            prompt_write = self.driver.find_element(By.CSS_SELECTOR, 'div[contenteditable="true"]')
            prompt_write.click()
            pyperclip.copy(prompt) # Промпт копируем в буфер обмена
            time.sleep(0.1)

            actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            button_send = self.driver.find_element(By.CSS_SELECTOR, 'button#composer-submit-button')
            button_send.click()

        except Exception as e:
            self.driver.save_screenshot("image.png")
            print("Error 0323: ", e)
            return "Error 0323: ", e


        time.sleep(0.2)

        get_answer = True
        while get_answer:
            try:
                #print("UNDUXUS indicator")

                # Пролистываем вниз
                fast_scroll_down(self.driver)

                indicator = self.driver.find_element(By.CSS_SELECTOR, 'button[data-testid="composer-speech-button"]') # Индикаторы по которым можно понять закончил ли балакать GPT
                time.sleep(50/1000)
                #print("Under indicator")
                if mode == "standard":
                    ai_answer = self.driver.find_elements(By.CSS_SELECTOR, "div.markdown") # Проверяем есть ли ответы
                elif mode == "code": # Если режим получения только кода
                    ai_answer = self.driver.find_elements(By.XPATH, '//button[@aria-label="Копировать"]') # Проверяем есть ли ответы
                else:
                    raise ValueError("Нверне значение для `mode`.")

                # Пролистываем вниз
                fast_scroll_down(self.driver)

                if mode == "standard":
                    response = ai_answer[-1].text # Получаем ответ от ИИ
                elif mode == "code":
                    ai_answer[-2].click() # Кликаем на кнопку копировать, чтобы скопировать код
                    time.sleep(0.2)
                    response = pyperclip.paste()
                
                #print("UNDUXUS click")

                # Наводим курсор на кнопку и кликаем
                time.sleep(0.1)
                if mode == "standard":
                    ai_answer_count = len(self.driver.find_elements(By.CSS_SELECTOR, "div.markdown")) # Сколько всего ответов
                elif mode == "code":
                    ai_answer_count = len(self.driver.find_elements(By.XPATH, '//button[@aria-label="Копировать"]')) # Сколько всего ответов

                if ai_answer_count > prev_answer_count: # Если GPT начал балакать
                    prev_answer_count = ai_answer_count
                    get_answer = False
                    return response
                else:
                    time.sleep(0.1)
                    
            except Exception as e:
                print("Exception!!!!")
                try:
                    have_button_i_want_th_an = self.driver.find_elements(By.CSS_SELECTOR, 'button.btn.relative.btn-primary.mt-4.self-start') # Иногда OPENAI предлагает нам выбрать один из ответов с кнопко "Я предпочитаю этот ответ"
                    have_button_i_want_th_an[0].click() # Выбираем первый вариант
                    print("Кнопка 'Я предпочитаю этот ответ' была запрошена и нажата.")
                except:
                    print("Кнопка 'Я предпочитаю этот ответ' не была запрошена")
                time.sleep(0.2)

    def await_element(self):
        """
        Wait for element to appear
        """
        elements = self.driver.find_elements(By.CLASS_NAME, self.config.get('class', 'GPT_response_history'))
        self.last_response = elements[-1]
        

    def await_response(self):
        """
        Wait for response to appear
        """
        self.last_response.text

    def property_script(self, property):
        return f"""
                const element = arguments[0];
                const property = window.getComputedStyle(element, "{property}").getPropertyValue("content");
                return property !== "" && property !== "none";
        """
    
    def check_generator(self, elements):
        sub_elements = elements[-1].find_elements(By.CSS_SELECTOR, "*")
        is_generating = False 
        
        # Check from the last element, where the generator is more likely to be present
        for sub_element in sub_elements[::-1]:
            try:
                has_before = self.driver.execute_script(self.property_script('::before'), sub_element)
                has_after = self.driver.execute_script(self.property_script('::after'), sub_element)
            except Exception as e:
                #selexcept.StaleElementReferenceException or selexcept.WebDriverException:
                self.logger.warning(f'Encountered an {type(e).__name__}. This might occur if an element is checked during an update. Continuing checks as normal.')
                is_generating = True 
                break 

            if has_after and not(has_before):
                is_generating = True 
                break 

        return is_generating
    
    @driver_refresh
    def find_entry(self, type, index):
        if self.selected_chat == None:
            self.logger.error('No chat selected. Please select a chat first.')
            return
        
        if type == 'prompt':
            class_name = self.config.get('class', 'USR_prompt_history')
            slicer = slice(None, None, 2)
        elif type == 'response':
            class_name = self.config.get('class', 'GPT_response_history')
            # slicer = slice(1, None, 2)
        else:
            self.logger.error(f'Invalid type {type}.')
            return

        result_elements = self.driver.find_elements(By.CLASS_NAME, class_name)

        if type == 'prompt':
            result_elements = result_elements[slicer]

        try:
            result = result_elements[index].text
            self.logger.debug(f'{type.capitalize()} found for index {index} in chat "{self.selected_chat}"')
            return result
        except Exception:
            self.logger.error(f'Index overflow or text not found in element')

class Mind(ChatMain):
    '''
    Основной класс библиотеки.
    Из класса Mind загружаются minder'ы
    '''

    def __init__(
        self,
        debug: bool = False
    ):
        if debug:
            self.logger = log_setup(self.config.get('dir', 'log_file'), console_level=None)