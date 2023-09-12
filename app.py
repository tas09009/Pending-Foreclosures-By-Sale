import requests
import datetime
from lxml import html

from flask import Flask, render_template, request

BASE_URL = (
    "https://sso.eservices.jud.ct.gov/Foreclosures/Public/PendPostbyTownDetails.aspx"
)
LIST_OF_TOWNS_URL = (
    "https://sso.eservices.jud.ct.gov/Foreclosures/Public/PendPostbyTownList.aspx"
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
TOWN_XPATH_LIST = '//a[contains(@href, "PendPostbyTownDetails.aspx")]/text()'
NEXT_SALE_DATE_XPATH = '//*[@id="ctl00_cphBody_GridView1_ctl02_Label1"]/text()[1]'
PAGE_LINKS = '//*[contains(text(), "{date}")]/../..//a[contains(text(), "View Full Notice")]/@href'
CANCELLED_SALE_NOTICE = '//*[contains(text(), "This Sale is Cancelled")]'


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def homepage():
    if request.method == "GET":
        towns = get_all_towns()
        return render_template("homepage.html", towns=towns)

    if request.method == "POST":
        town_list = request.form.getlist("town[]")
        town_urls = {}
        for town in town_list:
            if "Milford" in town:
                town = "Milford"
            urls = []
            tree = get_page_xml_tree(town)
            date = tree.xpath(NEXT_SALE_DATE_XPATH)[0]

            if is_date_within_week(date):
                links = tree.xpath(PAGE_LINKS.format(date=date))
                for page_path in links:
                    url = VIEW_FULL_NOTICE_BASE_URL + "/" + page_path
                    if not is_sale_cancelled(url):
                        urls.append(url)
            town_urls[town] = urls

        return render_template(
            "homepage.html", towns=get_all_towns(), town_urls=town_urls
        )


def get_all_towns():
    response = requests.get(LIST_OF_TOWNS_URL, headers=HEADERS)
    tree = html.fromstring(response.content)
    towns = tree.xpath(TOWN_XPATH_LIST)

    affected_town = next((town for town in towns if "Milford" in town), None)
    if affected_town:
        cleaned_town = affected_town.replace("Â\xa0", "").strip()
        towns[towns.index(affected_town)] = cleaned_town

    return towns


def create_parameters(town):
    """
    'Milford' seems to be the only exception here with two
    non-breaking spaces in its URL
    """
    if "Milford" in town:
        town_alternate = "Milford" + "\u00A0" + "\u00A0"
        parameters = {"town": {town_alternate}}
    else:
        parameters = {"town": {town}}
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
