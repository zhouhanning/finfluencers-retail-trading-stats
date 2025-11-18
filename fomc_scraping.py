import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"

start_date = datetime(2020, 1, 1)
end_date = datetime(2024, 12, 31)

print("Fetching webpage...")
response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

records = []

year_headers = soup.find_all("h3")

for h in year_headers:
    txt = h.get_text()
    year_match = re.search(r"(20\d{2})", txt)
    if not year_match:
        continue

    year = int(year_match.group(1))
    if not (2020 <= year <= 2024):
        continue

    sibling = h.find_next_sibling()

    while sibling and sibling.name != "h3":  
        meetings = sibling.find_all("div", class_=re.compile("fomc-meeting"))
        for m in meetings:
            # month
            month_div = m.find("div", class_=re.compile("fomc-meeting__month"))
            if not month_div:
                continue
            month = month_div.get_text(strip=True)

            # date
            date_div = m.find("div", class_=re.compile("fomc-meeting__date"))
            if not date_div:
                continue
            raw_day = date_div.get_text(strip=True)

            # take the first day of the range if it's a range
            day_clean = raw_day.split("-")[0].replace("*", "").strip()
            date_str = f"{month} {day_clean}, {year}"

            try:
                meeting_date = datetime.strptime(date_str, "%B %d, %Y")
            except:
                continue

            if start_date <= meeting_date <= end_date:
                records.append({
                    "date": meeting_date.strftime("%Y-%m-%d"),
                    "month": month,
                    "raw_day": raw_day,
                    "year": year
                })

        sibling = sibling.find_next_sibling()

# output results
if not records:
    print("❗ Still no meetings found — send me 10 lines of the HTML (I will decode it).")
else:
    df = pd.DataFrame(records).sort_values("date")
    df.to_csv("fomc_meetings.csv", index=False)
    print("Saved to fomc_meetings.csv")
    print(df)
