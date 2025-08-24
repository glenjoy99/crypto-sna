import time
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait



# Get list of Sanctioned Wallet IDs

# Request page of sanctioned wallets
sanctions_url = "https://www.opensanctions.org/search/?datasets=us_ofac_sdn&schema=CryptoWallet&scope=securities"
page = requests.get(sanctions_url)

# Parse html returned
soup = BeautifulSoup(page.content, "html.parser")

# Get all `li` elements
all_list_items = soup.find_all("li")

wallet_ids = []
for li in all_list_items:
    if li.has_attr('class'):
        for className in li["class"]:
            if "Search_resultItem" in className:
                ending_string_index = li.getText().index("Cryptocurrency")
                if ending_string_index > 0:
                    wallet_id = li.getText()[0:ending_string_index]
                    wallet_ids.append(wallet_id)


print(wallet_ids)


# Get all transactions for current wallet id (only first for now)
wallet_id = wallet_ids[0]

print(f"Checking outgoing transactions for wallet {wallet_id}")

# Request page for wallet info of current wallet id (this page uses javascript to pull data, 
# so we need to use selenium to allow page to wait for data fetching)
wallet_id_info_url = f"https://www.blockchain.com/explorer/addresses/btc/{wallet_id}"

driver = webdriver.Chrome()
driver.get(wallet_id_info_url)

# Wait for section component containing data to appear
WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.TAG_NAME, "section")));

# All data is found inside section component, only search in that subtree
section = driver.find_element(By.TAG_NAME, "section")

all_anchors = section.find_elements(By.TAG_NAME, "a")

outgoing_wallet_ids = []
for a in all_anchors:
    # Only match anchor tags with text content that matches the bitcoin wallet id regex and is not our current wallet id
    if a.text != "" and re.search(r"(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}", a.text) and a.text != wallet_id:
        outgoing_wallet_ids.append(a.text)

print("Outgoing ids:", outgoing_wallet_ids)

# Sleep to prevent excessive requests to blockchain.com
time.sleep(5)



driver.quit()
