import requests
import config
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from smtplib import SMTP


class CurrencyChecker:
    USD_PAGE = 'https://minfin.com.ua/currency/usd/'
    headers = {'User-Agent': ''}
    buy_usd = 0
    sell_usd = 0

    def __init__(self):
        """
        initialization, call get_currency_price
        """
        self.get_currency_price()

    def update_headers(self):
        """
        get random user-agent
        """
        user_agent = UserAgent()
        self.headers['User-Agent'] = user_agent.random

    def get_currency_price(self):
        """
        get the price of the dollar
        """
        # call update_headers()
        self.update_headers()

        # getting page content and create BeautifulSoup object
        page_content = requests.get(self.USD_PAGE, headers=self.headers).content
        soup = BeautifulSoup(page_content, 'html.parser')

        # find table with currency price
        currency_table = soup.find('table', class_='table-response mfm-table mfcur-table-lg mfcur-table-lg-currency-cur has-no-tfoot')

        # getting the price of the dollar in the bank
        currency_row = currency_table.find_all('tr')[1]
        self.buy_usd = float(currency_row.find('td', {'data-title': "Покупка"}).find('span', class_="mfm-posr").text[:7])
        self.sell_usd = float(currency_row.find('td', {'data-title': "Продажа"}).find('span', class_="mfm-posr").text[:7])

    def send_email(self):
        """
        sending the price of the usd
        """
        server = SMTP("smtp.gmail.com", 587)
        server.starttls()

        # sign in using personal gmail account
        server.login(config.SENDER_MAIL, config.SENDER_PASSWORD)

        # mail content
        mail_body = f"Subject: Currency\n\nHi Bohdan!\n\nThe dollar price has changed!\n\
Buy dollar: {self.buy_usd}\nSell dollar: {self.sell_usd}\n\nBest regards,\nCurrencyChecker."

        # sending mail
        server.sendmail(config.SENDER_MAIL, config.RECIPIENT_MAIL, mail_body)
        server.quit()

    def check_currency_price(self):
        """
        сheck the price for a change and send an email if the price has changed dramatically
        """
        # set old price in variables
        old_buy_usd = self.buy_usd
        old_sell_usd = self.sell_usd

        # get new price
        self.get_currency_price()

        # checking price
        if self.buy_usd <= old_buy_usd - 0.2 or self.sell_usd <= old_sell_usd - 0.2:
            self.send_email()
        elif self.buy_usd <= 27 or self.sell_usd <= 27:
            self.send_email()


currency = CurrencyChecker()

# checking the dollar price every hour
while True:
    currency.check_currency_price()
    time.sleep(60*60)
