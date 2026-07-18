from playwright.sync_api import sync_playwright
import re, pandas
from urllib.parse import urlparse, urlunparse

relatedWords = {"شیر": 20 , "ماست": 10, "لبنیات": 10, "سرشیر": 25
                , "دوغ": 20, "کشک": 5, "خامه": 15}

hatedWords = {"فروشگاه اینترنتی": 10, "فروشگاه آنلاین": 10, "فروشگاه": 5,
               "خرید": 10, "سبد خرید": 30, "تأمین‌کننده": 10, "غرفه‌دار": 10, "درخواست قیمت": 10}

executablePath=r"C:\Users\amitis\Desktop\mapScraper\chrome-win64\chrome.exe"
excelName = "output-0-48.xlsx"
excelPath = f"websiteRanking\{excelName}"
dataset = pandas.read_excel(excelPath)

websites = dataset["website"]

relatedScores = []
hatedScores = []

def addHttps(link: str) -> str | None:
    """
    Adds https:// to a link if there is not
    """
    if not link:
        return None
    parsed = urlparse(link)
    if not parsed.scheme:
        parsed = parsed._replace(scheme="https")

    return urlunparse(parsed)


for website in websites:
    try:
        if not isinstance(website, str) or website.strip() == "":
            relatedScores.append(-1)
            hatedScores.append(-1)
            continue
        
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=executablePath, headless=False)
            page = browser.new_page(viewport={"width": 1000, "height": 1000})
            page.goto(addHttps(website))
            page.wait_for_timeout(1000)
            text = page.locator("body").inner_text()

            # Normalize
            text = text.replace("\u200c", " ")      # Remove half-space (ZWNJ)
            text = re.sub(r"\s+", " ", text)        # Multiple spaces -> one
            text = text.lower()

            relatedScore = 0
            hatedScore = 0

            for word, weight in relatedWords.items():
                count = text.count(word.lower())
                relatedScore += count * weight

            for word, weight in hatedWords.items():
                count = text.count(word.lower())
                hatedScore += count * weight

            relatedScores.append(relatedScore)
            hatedScores.append(hatedScore)

            # print(website)
            # print(relatedScore)
            # print(hatedScore)
            # print("------------------")

            browser.close()
    except:
        relatedScores.append(-1)
        hatedScores.append(-1)
        continue


dataset["relatedScore"] = relatedScores
dataset["hatedScore"] = hatedScores

dataset.to_excel(f"websiteRanking\{excelName}", index=False)
