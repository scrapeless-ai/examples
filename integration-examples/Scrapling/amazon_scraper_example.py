from urllib.parse import urlencode
import json
import time
import re
from bs4 import BeautifulSoup
from scrapling.fetchers import DynamicSession

config = {
    "token": "scrapeless api key",
    "sessionName": "Data Scraping",
    "sessionTTL": "900",  
    "proxyCountry": "ANY",
    "sessionRecording": "true",
}

ws_endpoint = f"wss://browser.scrapeless.com/api/v2/browser?{urlencode(config)}"
target_url = "https://www.amazon.com/ESR-Compatible-Military-Grade-Protection-Scratch-Resistant/dp/B0CC1F4V7Q"

def retry(func, retries=2, wait=2):
    for i in range(retries + 1):
        try:
            return func()
        except Exception as e:
            print(f"Attempt {i+1} failed: {e}")
            if i == retries:
                raise
            time.sleep(wait * (i + 1))

def detect_bot(html):
    body_text = html.lower() if html else ""
    keywords = [
        "captcha",
        "are you a human",
        "verify you are human",
        "access to this page has been denied",
        "bot detection",
        "please enable javascript",
    ]
    return any(k in body_text for k in keywords)

with DynamicSession(cdp_url=ws_endpoint, disable_resources=True) as s:
    print("Connected to Scrapeless DynamicSession!")

    response = retry(lambda: s.fetch(target_url, network_idle=True, timeout=120000))
    html = response.body

    if detect_bot(html):
        print("Bot/CAPTCHA detected — consider switching proxy or manual solve.")
        try:
            response.screenshot(path="captcha_detected.png")
        except:
            pass

    soup = BeautifulSoup(html, "lxml")

    title_tag = soup.select_one("#productTitle, #title")
    wait_time = 0
    while not title_tag and wait_time < 60:
        print("Waiting for productTitle to appear...")
        time.sleep(3)
        wait_time += 3
        response = s.fetch(target_url, network_idle=True, timeout=120000)
        html = response.body
        soup = BeautifulSoup(html, "lxml")
        title_tag = soup.select_one("#productTitle, #title")

    title = title_tag.get_text(strip=True) if title_tag else None

    def get_text(selectors, multiple=False):
        if multiple:
            return [el.get_text(strip=True) for sel in selectors for el in soup.select(sel)]
        for sel in selectors:
            el = soup.select_one(sel)
            if el:
                return el.get_text(strip=True)
        return None

    price_raw = get_text([
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        "#priceblock_saleprice",
        "#price_inside_buybox",
        ".a-price .a-offscreen"
    ])
    rating_text = get_text(["span.a-icon-alt", "#acrPopover"])
    review_count_text = get_text(["#acrCustomerReviewText", "[data-hook='total-review-count']"])
    availability = get_text([
        "#availability .a-color-state",
        "#availability .a-color-success",
        "#outOfStock",
        "#availability"
    ])
    features = get_text(["#feature-bullets ul li"], multiple=True) or []
    description = get_text([
        "#productDescription",
        "#bookDescription_feature_div .a-expander-content",
        "#productOverview_feature_div"
    ])

    images = []
    main_img = soup.select_one("#imgTagWrapperId img") or soup.select_one("#landingImage")
    if main_img:
        src = main_img.get("data-old-hires") or main_img.get("src")
        if src:
            images.append(src)
        dyn = main_img.get("data-a-dynamic-image")
        if dyn:
            try:
                obj = json.loads(dyn)
                images.extend(obj.keys())
            except:
                pass
    alt_imgs = soup.select("#altImages img, .imageThumbnail img")
    for img in alt_imgs:
        src = img.get("src")
        if src:
            images.append(re.sub(r"\.(_SX\d+_)?\.?$", "", src))

    asin_input = soup.select_one("input#ASIN")
    asin = asin_input.get("value").strip() if asin_input else None
    if not asin:
        detail_text = " ".join([li.get_text(strip=True) for li in soup.select("#detailBullets_feature_div li")])
        m = re.search(r"ASIN[:\s]*([A-Z0-9-]+)", detail_text, re.I)
        if m:
            asin = m[1].strip()

    merchant = get_text(["#sellerProfileTriggerId", "#merchant-info", "#bylineInfo"])
    categories = get_text([
        "#wayfinding-breadcrumbs_container ul li a",
        "#wayfinding-breadcrumbs_feature_div ul li a"
    ], multiple=True) or []

    currency, price = None, None
    if price_raw:
        m = re.match(r"([^\d.,\s]+)?\s*([\d.,]+)", price_raw)
        if m:
            currency = m.group(1).strip() if m.group(1) else None
            price = float(m.group(2).replace(",", ""))

    data = {
        "title": title,
        "price_raw": price_raw,
        "price": price,
        "currency": currency,
        "rating": float(rating_text.split()[0].replace(",", "")) if rating_text else None,
        "review_count": int(''.join(filter(str.isdigit, review_count_text))) if review_count_text else None,
        "availability": availability,
        "features": features,
        "description": description,
        "images": list(dict.fromkeys(images)),
        "asin": asin,
        "merchant": merchant,
        "categories": categories,
        "url": target_url,
        "scrapedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    print(json.dumps(data, indent=2))
    with open("scrapeless-amazon-product.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
