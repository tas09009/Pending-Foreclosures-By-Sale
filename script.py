import requests
import datetime
from lxml import html
import webbrowser

BASE_URL = (
    "https://sso.eservices.jud.ct.gov/Foreclosures/Public/PendPostbyTownDetails.aspx"
)
VIEW_FULL_NOTICE_BASE_URL = "https://sso.eservices.jud.ct.gov/Foreclosures/Public"
HEADERS = {
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "DNT": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
    "sec-ch-ua": '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
}

# Xpaths
NEXT_SALE_DATE_XPATH = '//*[@id="ctl00_cphBody_GridView1_ctl02_Label1"]/text()[1]'
PAGE_LINKS = '//*[contains(text(), "{date}")]/../..//a[contains(text(), "View Full Notice")]/@href'
CANCELLED_SALE_NOTICE = '//*[contains(text(), "This Sale is Cancelled")]'


def create_parameters(town):
    """
    'Milford' seems to be the only exception here with two
    non-breaking spaces in its URL
    """
    if town != "Milford":
        parameters = {"town": {town}}
    else:
        town_alternate = town + "\u00A0" + "\u00A0"
        parameters = {"town": {town_alternate}}
    return parameters


def get_page_xml_tree(town):
    parameters = create_parameters(town)
    town_page = requests.get(url=BASE_URL, headers=HEADERS, params=parameters)
    tree = html.fromstring(town_page.content)  # Notes: these 2 lines
    return tree


def is_date_within_week(date: str):
    format_str = "%m/%d/%Y"
    sale_date = datetime.datetime.strptime(date, format_str)
    one_week_from_now = datetime.datetime.now() + datetime.timedelta(days=7)
    if sale_date <= one_week_from_now:
        return True
    return False


def is_sale_cancelled(url):
    """
    Cancelled auctions will only show up after opening the page.
    """
    response = requests.get(url, headers=HEADERS)
    tree = html.fromstring(response.content)
    return True if tree.xpath(CANCELLED_SALE_NOTICE) else False


if __name__ == "__main__":
    town_list = open("town_list.txt").read().split("\n")
    urls = []
    for town in town_list:
        tree = get_page_xml_tree(town)
        date = tree.xpath(NEXT_SALE_DATE_XPATH)[0]

        if is_date_within_week(date):
            links = tree.xpath(PAGE_LINKS.format(date=date))
            for page_path in links:
                url = VIEW_FULL_NOTICE_BASE_URL + "/" + page_path
                if not is_sale_cancelled(url):
                    urls.append(url)

    # Open each one up!
    for url in urls:
        webbrowser.open(url)
