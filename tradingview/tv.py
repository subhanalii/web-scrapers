import requests
import json
import time
import csv

screeners = {
    "crypto": {
        "url": "https://scanner.tradingview.com/coin/scan",
        "market": "coin",
        "columns": ["base_currency", "base_currency_desc", "close", "24h_close_change|5", "market_cap_calc"]
    },
    "cex": {
        "url": "https://scanner.tradingview.com/cex/scan",
        "market": "cex",
        "columns": ["name", "close", "24h_close_change|5", "volume", "market_cap_calc"]
    },
    "dex": {
        "url": "https://scanner.tradingview.com/dex/scan",
        "market": "dex",
        "columns": ["name", "close", "24h_close_change|5", "volume", "market_cap_calc"]
    },
    "stock": {
        "url": "https://scanner.tradingview.com/america/scan",
        "market": "stock",
        "columns": ["name", "close", "change", "volume", "market_cap_basic"]
    },
    "etf": {
        "url": "https://scanner.tradingview.com/etf/scan",
        "market": "etf",
        "columns": ["name", "close", "change", "volume", "market_cap_basic"]
    }
}
cookies = {
    'device_t': 'RW9nUEJBOjA.IVRIK9EL2MybU498h7Hp9r_bCdrrLp89GM3A7oppPp0',
    'cookiePrivacyPreferenceBannerProduction': 'notApplicable',
    '_ga': 'GA1.1.968929997.1736063828',
    'cookiesSettings': '{"analytics":true,"advertising":true}',
    'sessionid': '4i6qh63gebxm9ewqtdb6z4mhto75glz8',
    'sessionid_sign': 'v3:dtTFT72Z2HSw4ZJSFrJ3eGzKOMGoiA6PBfM9V6Kp1Xg=',
    'tv_ecuid': '1ee637ff-1b6d-4efd-8916-892335363ecf',
    '_sp_ses.cf1a': '*',
    '__gads': 'ID=2631cf66edcbb1cd:T=1726585531:RT=1746954322:S=ALNI_MaZLmVZTDWPSzl_rwSI7sOT6ZkT-w',
    '__gpi': 'UID=00000ef1ae066af8:T=1726585531:RT=1746954322:S=ALNI_Ma0vlUIvn5IGu02Gd4QUDfXSRvjeQ',
    '__eoi': 'ID=ed5f02a7cf2c2c27:T=1742228036:RT=1746954322:S=AA-AfjYWLIwv4TnydwZ-7CJgvuy1',
    '_ga_YVVRYGL0E0': 'GS2.1.s1746953254$o174$g1$t1746955133$j60$l0$h0',
    '_sp_id.cf1a': 'e67d7e23-0080-4248-bc1e-bb04c266dd76.1726584761.148.1746955175.1744888608.8424145b-a6a3-4e3e-8a35-662d9bced431.5a0c4deb-087e-4054-b451-2e4a45b59291.2eced0b6-c42e-421f-9af2-a9cc8d84044b.1746953254011.29',
}

headers = {
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'text/plain;charset=UTF-8',
    'origin': 'https://www.tradingview.com',
    'priority': 'u=1, i',
    'referer': 'https://www.tradingview.com/',
    'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    # 'cookie': 'device_t=RW9nUEJBOjA.IVRIK9EL2MybU498h7Hp9r_bCdrrLp89GM3A7oppPp0; cookiePrivacyPreferenceBannerProduction=notApplicable; _ga=GA1.1.968929997.1736063828; cookiesSettings={"analytics":true,"advertising":true}; sessionid=4i6qh63gebxm9ewqtdb6z4mhto75glz8; sessionid_sign=v3:dtTFT72Z2HSw4ZJSFrJ3eGzKOMGoiA6PBfM9V6Kp1Xg=; tv_ecuid=1ee637ff-1b6d-4efd-8916-892335363ecf; _sp_ses.cf1a=*; __gads=ID=2631cf66edcbb1cd:T=1726585531:RT=1746954322:S=ALNI_MaZLmVZTDWPSzl_rwSI7sOT6ZkT-w; __gpi=UID=00000ef1ae066af8:T=1726585531:RT=1746954322:S=ALNI_Ma0vlUIvn5IGu02Gd4QUDfXSRvjeQ; __eoi=ID=ed5f02a7cf2c2c27:T=1742228036:RT=1746954322:S=AA-AfjYWLIwv4TnydwZ-7CJgvuy1; _ga_YVVRYGL0E0=GS2.1.s1746953254$o174$g1$t1746955133$j60$l0$h0; _sp_id.cf1a=e67d7e23-0080-4248-bc1e-bb04c266dd76.1726584761.148.1746955175.1744888608.8424145b-a6a3-4e3e-8a35-662d9bced431.5a0c4deb-087e-4054-b451-2e4a45b59291.2eced0b6-c42e-421f-9af2-a9cc8d84044b.1746953254011.29',
}


params = {'label-product': 'screener-coin'}

def fetch_screener_to_csv(name, config, page_size=100):
    print(f"\n📥 Fetching {name.upper()} Screener...")
    all_data = []
    start = 0

    while True:
        payload = {
            "columns": config["columns"],
            "ignore_unknown_fields": False,
            "options": {"lang": "en"},
            "range": [start, start + page_size],
            "sort": {
                "sortBy": config["columns"][0],  # Sort by first column
                "sortOrder": "asc"
            },
            "symbols": {},
            "markets": [config["market"]]
        }

        response = requests.post(
            config["url"],
            headers=headers,
            cookies=cookies,
            params=params,
            data=json.dumps(payload)
        )

        try:
            result = response.json()
            batch = result.get("data", [])
            if not batch:
                break

            all_data.extend(batch)
            #print(f" - Fetched {len(batch)} rows (total: {len(all_data)})")
            for row in batch:    
                print(f"{row['s']}")
            start += page_size
            time.sleep(0.3)
        except Exception as e:
            print(f" Error: {e}")
            break

    if not all_data:
        print(f" No data fetched for {name}. Skipping CSV.")
        return

    # Save to CSV
    file_name = f"{name}_screener.csv"
    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["symbol"] + config["columns"])
        for row in all_data:
            writer.writerow([row['s']] + row['d'])

   # print(f"Saved {len(all_data)} rows to {file_name}")

# Run for all screeners
for screener_name, screener_config in screeners.items():
    fetch_screener_to_csv(screener_name, screener_config)
