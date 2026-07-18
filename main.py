from playwright.sync_api import sync_playwright
import re, pandas

excelPath = "vic.xlsx"
startIndex = 0 #including
endIndex = 48 #excluding
websiteReg = r"\b(?:www\.)?[a-zA-Z0-9-]+\.(?:com|net|org|ir|co|az)\b" 
phoneReg = r"\+\d{1,3}\s?\d{1,3}\s?\d{3,4}\s?\d{3,4}"
executablePath=r"C:\Users\amitis\Desktop\mapScraper\chrome-win64\chrome.exe"

companyNames = pandas.read_excel(excelPath)["name"][startIndex:endIndex]

output=[]

def setWebsite(text:str) -> str:
    """
    gets a string and extrct website \b
    if not founed, returns None
    """
    match = re.search(pattern=websiteReg, string=text)
    return match.group() if match else None

def setPhone(text:str) -> str:
    """
    gets a string and extrct phone number \b
    if not founed, returns None
    """
    match = re.search(pattern=phoneReg, string=text)
    return match.group() if match else None

# def setAddress(text) -> str:
#     """
#     gets a string and extrct address \b
#     if not founed, returns None
#     """
#     match = re.search(
#         r'\s*\n?(.*?)\s*\n?',
#         text,
#         re.DOTALL
#     )
    # if match:
    #     return match.group(1).strip()
    # return None

for companyName in companyNames:
    try:
        with sync_playwright() as p:
            baseUrl = "https://www.google.com/maps/search/"
            companyNameInUrl = companyName.replace(" ", "+")
            scrapUrl = baseUrl + companyNameInUrl
            browser = p.chromium.launch(executable_path=executablePath, headless=False)
            page = browser.new_page(viewport={"width": 1000, "height": 1000})
            page.goto(scrapUrl)

            page.wait_for_timeout(1000)
            h1 = page.locator("h1")
            if (h1.count() == 0):
                continue
            notFound = page.locator("h1", has_text="Results").count()
            if notFound > 0:
                continue

            texts = page.locator("div.m6QErb").all_inner_texts()
            title = h1.inner_text()
            fullText = "\n".join(texts)

            output.append({
                "name": title,
                "website": setWebsite(fullText),
                "phone": setPhone(fullText),
            })
            browser.close()
    except:
        continue

dfOutput = pandas.DataFrame(output)
dfOutput.to_excel(excel_writer=f"output-{startIndex}-{endIndex}.xlsx")