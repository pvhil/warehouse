from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from discord_webhook import DiscordWebhook, DiscordEmbed
import yaml
from threading import Thread
import re
import os
from pypresence import Presence
from playsound import playsound
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('log-level=3')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--single-process')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('ignore-certificate-errors')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_argument("disable-infobars")
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36')
chrome_prefs = {}
chrome_options.page_load_strategy = 'eager'
chrome_options.experimental_options["prefs"] = chrome_prefs
chrome_prefs["profile.default_content_settings"] = {"images": 2}
chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}

def cls():
        os.system('cls' if os.name=='nt' else 'clear')

class warehousemonitor():
    def monitor(self,asin,proxy):
        # request monitor
        if proxy != "null":
            print(f"\U0001F7EB Info: Using proxy '{proxy}' for '{asin}'")
            pp = proxy.split(":")
        s = requests.session()
        while 1:
            print(f"\U0001F4A4 Monitoring {asin}...")
            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "accept-language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
                "cache-control": "max-age=0",
                "device-memory": "8",
                "downlink": "10",
                "dpr": "1",
                "ect": "4g",
                "rtt": "50",
                "sec-ch-device-memory": "8",
                "sec-ch-dpr": "1",
                "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"101\", \"Google Chrome\";v=\"101\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "sec-ch-viewport-width": "1920",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "viewport-width": "1920",
            }
            try:
                if proxy == "null":
                    x = s.get(f'http://www.amazon.de/gp/product/ajax/ref=dp_aod_unknown_mbc?asin={asin}&m=&qid=&smid=&sourcecustomerorglistid=&sourcecustomerorglistitemid=&sr=&pc=dp&experienceId=aodAjaxMain', headers=headers, timeout=8)
                else:
                    proxies = {
                        "http": f"http://{pp[2]}:{pp[3]}@{pp[0]}:{pp[1]}",
                        "https": f"http://{pp[2]}:{pp[3]}@{pp[0]}:{pp[1]}"
                    }
                    x = s.get(f'http://www.amazon.de/gp/product/ajax/ref=dp_aod_unknown_mbc?asin={asin}&m=&qid=&smid=&sourcecustomerorglistid=&sourcecustomerorglistitemid=&sr=&pc=dp&experienceId=aodAjaxMain', headers=headers, proxies=proxies, timeout=8)
            except Exception:
                print(f"Temporary Proxy Error. (Timeout or invalid proxy) Continuing... ({asin})")
                s = requests.session()
                continue

            html = x.text
            soup = BeautifulSoup(html, "html.parser")
            element = soup.find_all("div", {"id":"aod-offer"})
            if len(element) == 0:
                if proxy == "null":
                    print("\U0001F6AB Blocked Monitor Request. Waiting extra 30s..")
                    time.sleep(30)
                    s = requests.session()
                else:
                    print("\U0001F6AB Blocked Monitor Request. Retrying...")
                    s = requests.session()
            for tag in element:
                temp = tag.find("div", {"id":"aod-offer-soldBy"})
                seller = temp.find("a", {"class":"a-size-small a-link-normal"})
                if (seller.text).replace(" ","") != "AmazonWarehouse":
                    continue
                print(f"\U0001F3AE Found offer from {seller.text}")
                quality = tag.find("span",{"class":"expandable-expanded-text"}).text
                print("\U0001F3AE The Quality Description is: "+quality)
                priceTag = tag.find("div", {"id":"aod-offer-price"})
                price = re.sub('[^0-9,]', "", priceTag.find("span", {"class": "a-offscreen"}).text)
                print(f"\U0001F3AE The price is {price}")
                if (int(price.split(',', 1)[0])) > (self.maxprice+5):
                    print("\U0001F6AB The Price is too high! Skipping...")
                    continue
                tdTags = tag.find_all("span", {"data-action": "aod-atc-action"})
                for tag in tdTags:
                    f = json.loads(tag["data-aod-atc-action"])
                    print(f"\U0001F3AE The offer ID is: {f['oid']}")
                    try:
                        playsound(os.path.dirname(__file__)+'\\util\\ding.mp3',block=False)
                    except Exception:
                        pass
                    print(f"\U0001F3AE Checkout Link: https://www.amazon.de/gp/product/handle-buy-box/ref=dp_start-bbf_1_glance?ASIN={asin}&quantity.1=1&asin.1={asin}&quantity=1&submit.buy-now=1&tag=baba08b-21&offeringID={f['oid']}")
                    return f['oid'], price , quality
            #monitordelay
            time.sleep(self.delay)

    def run(self,asin,proxy):
        while 1:
            if self.headless:
                chrome_options.add_argument("--headless")
            browser = webdriver.Chrome(service=self.service,options=chrome_options)
            cls()
            browser.get("https://www.amazon.de/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.de%2Fgp%2Fcss%2Fyour-account-access%2Fref%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=deflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&")
            print(f"\U0001F511 Logging in... ({asin})")
            try:
                WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.NAME, "email"))).send_keys(self.email)
                WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, "continue"))).click()
                WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.NAME, "password"))).send_keys(self.password)
                WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.NAME, "rememberMe"))).click()
                time.sleep(1)
                browser.find_element(by=By.ID,value="signInSubmit").click()
            except Exception:
                print("\U0001F6AB Error. Invalid Credentials! Please fill in the config.yaml!")
                time.sleep(5)
                return
            print(f"\U0001F511 Logged into your account. ({asin})")

            # waiting for monitor
            oid, price, quality = self.monitor(asin,proxy)

            url = f"https://www.amazon.de/gp/product/handle-buy-box/ref=dp_start-bbf_1_glance?ASIN={asin}&quantity.1=1&asin.1={asin}&quantity=1&submit.buy-now=1&tag=baba08b-21&offeringID={oid}"
            for x in range(10000):
                try:
                    browser.get(url)
                    checkout = browser.find_element(By.NAME, "placeYourOrder1")
                    checkout.click()
                    print("\U0001F4B0 Potentially bought the product! Check your Mails! Still trying to buy for safety...")
                    try:
                        playsound(os.path.dirname(__file__)+'\\util\\cash.mp3',block=False)
                    except Exception:
                        pass
                    try:
                        webhook = DiscordWebhook(url=self.webhookurl, username="Phils Warehouse",content=f"<@{self.discordname}>", timeout=3)
                        embed = DiscordEmbed(title='Potentially sniped a Warehouse Deal!', color='55ff00',description='Managed to click "buy" at the Checkout Screen!\nIt does not mean it was successful, so look at your mails!\nInfo: Bot still tries to buy for safety.')
                        embed.set_footer(text='Made by pvhil | Ver 1.0.0')
                        embed.set_timestamp()
                        embed.add_embed_field(name='Account', value=self.email)
                        embed.add_embed_field(name='ASIN', value=asin)
                        embed.add_embed_field(name='OfferID', value=oid,inline=False)
                        embed.add_embed_field(name='Price', value=price)
                        embed.add_embed_field(name="Quality",value=quality)
                        embed.set_image(url=f"https://ws-eu.amazon-adsystem.com/widgets/q?_encoding=UTF8&MarketPlace=DE&ASIN={asin}&ServiceVersion=20070822&ID=AsinImage&WS=1&Format=AC_SL500")
                        webhook.add_embed(embed)
                        webhook.execute()
                    except Exception:
                        print("\U0001F6AB Warning! The Discord Webhook is invalid. Could not send a Webhook.")
                    time.sleep(4)
                except Exception:
                    print(f"\U0001F6AB Failed the checkout! Retrying... ({asin})")
                    time.sleep(0.2)

            print(f"\U0001F3AE Restarting the Task with the ASIN {asin} to hopefully buy more :))")
            time.sleep(10)
            browser.quit()
            time.sleep(5)

    def __init__(self) -> None:
        """Start the program and initialize"""
        os.system("title pvhil's Warehouse Bot" if os.name=='nt' else 'clear')
        cls()
        print(r"""
     _       __                __                        
    | |     / /___ _________  / /_  ____  __  __________ 
    | | /| / / __ `/ ___/ _ \/ __ \/ __ \/ / / / ___/ _ \
    | |/ |/ / /_/ / /  /  __/ / / / /_/ / /_/ (__  )  __/
    |__/|__/\__,_/_/   \___/_/ /_/\____/\__,_/____/\___/ 
        """)
        try:
            RPC = Presence(client_id="965260628925251675")
            RPC.connect()
            RPC.update(state="Hunting Deals..",buttons=[{"label": "Website", "url": "https://pvhil.me"}])
        except:
            pass

        threads = []
        print("\U0001F44B Thanks for using the Warehouse bot (Ver. 1.0.0). Loading the config.yaml file.")
        print("Note: Please use this programm with a static IP address\n")
        print("\U0001F310 Please visit my website: https://pvhil.me\n")
        time.sleep(1)

        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        # static config
        self.email = config["email"]
        self.password = config["password"]
        self.headless = config["headless"]
        self.maxprice = config["maxprice"]
        self.delay = config["monitordelay"]
        self.webhookurl =config["webhook"]
        self.discordname = config["discord"]

        asins = config["asins"]
        proxies = config["proxy"]
        self.service = Service(executable_path=ChromeDriverManager().install())

        if self.email == "email":
            print("\U0001F6AB Error. Invalid Credentials! Please fill in the config.yaml!")
            time.sleep(2)
            return
        for index, value in enumerate(asins):
            if index >= len(proxies):
                proxy = "null"
            else:
                proxy = proxies[index]
            t = Thread(target=self.run,
                        args=(value,proxy))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

warehousemonitor()