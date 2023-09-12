from tkinter import *
import zipfile
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import json
import os
import pandas as pd
import traceback
from tkinter import font


def click_button(driver, button) -> None:
    "нажатие на кнопку"
    wait = WebDriverWait(driver, 10)
    next_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, button)))
    ActionChains(driver).move_to_element(next_button).click().perform()


def get_chromedriver_with_proxy(proxy_ip: str, proxy_port: str, proxy_user: str, proxy_pass: str, user_agent: str):
    "получить хром драйвер с прокси для работы с селениумом"

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"76.0.0"
    }
    """

    background_js = """
    let config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
            }
        };
    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }
    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (proxy_ip, proxy_port, proxy_user, proxy_pass)

    chrome_options = webdriver.ChromeOptions()

    plugin_file = 'proxy_auth_plugin.zip'

    with zipfile.ZipFile(plugin_file, 'w') as zp:
        zp.writestr('manifest.json', manifest_json)
        zp.writestr('background.js', background_js)

    chrome_options.add_extension(plugin_file)
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument(f'--user-agent={user_agent}')

    s = Service(
        executable_path='chromedriver.exe'
    )
    driver = webdriver.Chrome(
        service=s,
        options=chrome_options
    )

    return driver


def graph_interface():
    "весь графыический интерфейс"

    def twitter_auth(driver, login: str, password: str, reserve_mail: str):
        "Заходит в твиттер"
        try:
            wait = WebDriverWait(driver, 20)
            driver.get("https://twitter.com/i/flow/login")
            sleep(2)
            driver.find_element(By.NAME,
                                "text").send_keys(login)
            text_widget.insert(END, "ввожу логин\n")
            sleep(1)
            click_button(driver,
                         "div[class='css-18t94o4 css-1dbjc4n r-sdzlij r-1phboty r-rs99b7 r-ywje51 r-usiww2 r-2yi16 r-1qi8awa r-1ny4l3l r-ymttw5 r-o7ynqc r-6416eg r-lrvibr r-13qz1uu'")
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "Input[type='password']"))).send_keys(
                password)
            text_widget.insert(END, "ввожу пароль\n")
            click_button(driver,
                         "div[class = 'css-18t94o4 css-1dbjc4n r-sdzlij r-1phboty r-rs99b7 r-19yznuf r-64el8z r-1ny4l3l r-1dye5f7 r-o7ynqc r-6416eg r-lrvibr']")
            sleep(2)
            if driver.current_url == "https://twitter.com/home":
                text_widget.insert(END, "зашел без резрвной почты\n")
            else:
                text_widget.insert(END, "ввожу резервную\n")
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "Input[type='email']"))).send_keys(
                    reserve_mail)
                click_button(driver,
                             "div[class = 'css-18t94o4 css-1dbjc4n r-sdzlij r-1phboty r-rs99b7 r-19yznuf r-64el8z r-1ny4l3l r-1dye5f7 r-o7ynqc r-6416eg r-lrvibr']")
            return json.dumps(driver.get_cookie("auth_token"))
        except Exception:
            text_widget.insert(END, "что то не так\n")
        finally:
            driver.close()
            driver.quit()

    def cookies_useragent():
        if var.get() == 6:
            l_useragent = Label(window, text="записать юзерагент?", font=("Arial Bold", 10), fg="white", bg="black")
            l_useragent.grid(column=0, row=4)
            button_useragent_0 = Radiobutton(window, text="да", fg="white", bg="black", variable=var,
                                             command=write_useragent,
                                             value=3, font=custom_font)
            button_useragent_0.grid(column=0, row=5)
            button_useragent_1 = Radiobutton(window, text="нет", fg="white", bg="black", variable=var,
                                             command=write_useragent,
                                             value=4, font=custom_font)
            button_useragent_1.grid(column=1, row=5)
        if var.get() == 5:
            l_lk_retweet = Label(window, text="что делаем?", font=("Arial Bold", 10), fg="white", bg="black")
            l_lk_retweet.grid(column=1, row=8)
            button_like_retweet = Radiobutton(window, text="лайк+ретвит", variable=var, fg="white", bg="black",
                                              command=like_or_retweet, value=0, font=custom_font)
            button_like_retweet.grid(column=0, row=9)
            button_follow = Radiobutton(window, text="подписка", variable=var, fg="white", bg="black",
                                        command=like_or_retweet,
                                        value=1, font=custom_font)
            button_follow.grid(column=1, row=9)
            button_like_retweet_follow = Radiobutton(window, text="лайк+ретвит+подписка", variable=var, fg="white",
                                                     bg="black",
                                                     command=like_or_retweet, value=2, font=custom_font)
            button_like_retweet_follow.grid(column=2, row=9)

        button_move_0.config(state="disabled")
        button_move_1.config(state="disabled")

    def write_useragent():
        "Запись юзерагента"
        if var.get() == 3:
            try:
                file_exists = all([os.path.isfile("data.csv"), os.path.isfile("user_agent.csv")])
                if not file_exists:
                    raise FileNotFoundError("Один или оба файла не найдены.")

                df = pd.read_csv("data.csv")
                df_useragent = pd.read_csv("user_agent.csv")

                len_csv_table = len(df)
                df['user_agent'] = df_useragent['useragent'].sample(n=len_csv_table, replace=True).reset_index(
                    drop=True)
                df.to_csv("data.csv", index=False)

            except FileNotFoundError as e:
                text_widget.insert(END, f"Успешно выполнено действие{e}\n")

            except Exception:
                traceback.print_exc()
                text_widget.insert(END, "Что-то пошло не так при обработке файла\n")
        if var.get() == 4 or var.get() == 3:
            l_get_cookie = Label(window, text="записать кукисы?", font=("Arial Bold", 10), fg="white", bg="black")
            l_get_cookie.grid(column=0, row=6)

            button_get_cookie_0 = Radiobutton(window, text="да", fg="white", bg="black", variable=var,
                                              command=write_cookies, value=7,
                                              font=custom_font)
            button_get_cookie_0.grid(column=0, row=7)
            button_get_cookie_1 = Radiobutton(window, text="нет", fg="white", bg="black", variable=var,
                                              command=write_cookies, value=8,
                                              font=custom_font)
            button_get_cookie_1.grid(column=1, row=7)

    def write_cookies():
        "Запись кукисов"
        if var.get() == 7:
            try:
                df = pd.read_csv("data.csv")
                for i, row in df.iterrows():
                    df.loc[i, 'tw_cookie'] = twitter_auth(
                        get_chromedriver_with_proxy(row["proxy_ip"], row["proxy_port"], row["proxy_login"],
                                                    row["proxy_password"], row["user_agent"]),
                        row["tw_login"], row["tw_password"], row["tw_reserve_mail"])
                    text_widget.insert(END, "успешно добавил кукисы\n")
                df.to_csv("data.csv", index=False)
            except Exception:
                text_widget.insert(END, "что то не так с записью в файл кукисов\n")
        if var.get() == 8 or var.get() == 7:
            l_lk_retweet = Label(window, text="что делаем?", font=("Arial Bold", 10), fg="white", bg="black")
            l_lk_retweet.grid(column=1, row=8)

            button_like_retweet = Radiobutton(window, text="лайк+ретвит", variable=var, fg="white", bg="black",
                                              command=like_or_retweet, value=0, font=custom_font)
            button_like_retweet.grid(column=0, row=9)

            button_follow = Radiobutton(window, text="подписка", variable=var, fg="white", bg="black",
                                        command=like_or_retweet,
                                        value=1, font=custom_font)
            button_follow.grid(column=1, row=9)

            button_like_retweet_follow = Radiobutton(window, text="лайк+ретвит+подписка", variable=var, fg="white",
                                                     bg="black",
                                                     command=like_or_retweet, value=2, font=custom_font)
            button_like_retweet_follow.grid(column=2, row=9)

    def like_or_retweet():
        "делает ретвит или ставит лайк на пост"
        data = pd.read_csv("data.csv")
        driver = None
        for _, row in data.iterrows():
            try:
                proxy_ip = row["proxy_ip"]
                proxy_port = row["proxy_port"]
                proxy_login = row["proxy_login"]
                proxy_password = row["proxy_password"]
                user_agent = row["user_agent"]
                tw_url = row["tw_url"]
                tw_cookie = row["tw_cookie"]
                tw_user = row["tw_user"]

                driver = get_chromedriver_with_proxy(proxy_ip, proxy_port, proxy_login, proxy_password, user_agent)
                wait = WebDriverWait(driver, 5)

                if var.get() == 0 or var.get() == 2:
                    if tw_url and tw_cookie:
                        driver.get(tw_url)
                        driver.add_cookie(json.loads(tw_cookie))
                        driver.refresh()

                        try:
                            way_xpath = "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div/div/div[1]/div/div/article/div/div/div[3]/div[6]/div/div[3]/div"
                            next_button = wait.until(EC.visibility_of_element_located((By.XPATH, way_xpath)))

                            if next_button.get_attribute("data-testid") == "like":
                                ActionChains(driver).move_to_element(next_button).click().perform()
                                text_widget.insert(END, "поставил лайк\n")
                            else:
                                text_widget.insert(END, "уже лайкнул\n")

                            sleep(0.2)

                            next_button1 = wait.until(EC.visibility_of_element_located((By.XPATH,
                                                                                        "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div/div/div[1]/div/div/article/div/div/div[3]/div[6]/div/div[2]/div")))

                            if next_button1.get_attribute("data-testid") == "retweet":
                                ActionChains(driver).move_to_element(next_button1).click().perform()
                                click_button(driver, "div[data-testid='retweetConfirm']")
                                text_widget.insert(END, "сделал ретвит\n")
                            else:
                                text_widget.insert(END, "уже сделал ретвит\n")
                        except Exception:
                            text_widget.insert(END, "Что-то пошло не так\n")
                    else:
                        text_widget.insert(END, "URL или cookie отсутствуют\n")

                if var.get() == 1 or var.get() == 2:
                    if tw_user or tw_cookie:
                        driver.get(f"https://twitter.com/{tw_user}")
                        try:
                            driver.add_cookie(json.loads(tw_cookie))
                            driver.refresh()
                            click_button(driver, f"div[aria-label='Follow @{tw_user}']")
                            text_widget.insert(END, "успешно подписался\n")
                        except Exception:
                            text_widget.insert(END, "уже подписан\n")
                    else:
                        text_widget.insert(END, "Пользователь Twitter или cookie отсутствуют\n")
            except Exception:
                text_widget.insert(END, "проверь таблицу\n")

            finally:
                if driver is not None:
                    driver.close()
                    driver.quit()
                    text_widget.insert(END, "\n")

    window = Tk()
    window.title("Twitter tool")
    window.geometry('1200x600')
    window["bg"] = 'black'

    var = IntVar()

    custom_font = font.Font(size=16)

    ltd = Label(window, text="Xakuss did it", font=("Arial Bold", 10), fg="white", bg="black")
    ltd.grid(column=0, row=0)

    twitter_img = PhotoImage(file="twitter.png")
    label_img = Label(window, image=twitter_img, background="black")
    label_img.grid(column=0, row=1)

    l_move = Label(window, text="Кукисы и юзерагент заполнены?", font=("Arial Bold", 10), fg="white", bg="black")
    l_move.grid(column=0, row=2)

    button_move_0 = Radiobutton(window, text="да", fg="white", bg="black", variable=var, command=cookies_useragent,
                                value=5, font=custom_font)
    button_move_0.grid(column=0, row=3)
    button_move_1 = Radiobutton(window, text="нет", fg="white", bg="black", variable=var, command=cookies_useragent,
                                value=6, font=custom_font)
    button_move_1.grid(column=1, row=3)
    scrollbar = Scrollbar(window)
    scrollbar.grid(row=0, column=2, sticky="ns")

    text_widget = Text(window, height=10, width=50, bg="black", fg="white")
    text_widget.config(width=60, height=10)
    text_widget.grid(row=0, column=2)

    text_widget.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=text_widget.yview)

    window.mainloop()


if __name__ == '__main__':
    graph_interface()
