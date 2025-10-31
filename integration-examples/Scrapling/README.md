

## Brief Overview
[Scrapling](https://github.com/D4Vinci/Scrapling?utm_source=github&utm_medium=integration&utm_campaign=scrapling) is an undetectable, powerful, flexible, and high-performance Python web scraping library designed to make web scraping simple and effortless. It is the first **adaptive scraping library** capable of learning from website changes and evolving along with them. While other libraries break when site structures update, Scrapling automatically repositions elements and keeps your scrapers running smoothly.

### Key Features
- **Adaptive Scraping Technology** – The first library that learns from website changes and automatically evolves. When a site’s structure updates, Scrapling intelligently repositions elements to ensure continuous operation.  
- **Browser Fingerprint Spoofing** – Supports TLS fingerprint matching and real browser header emulation.  
- **Stealth Scraping Capabilities** – The StealthyFetcher can bypass advanced anti-bot systems like Cloudflare Turnstile.  
- **Persistent Session Support** – Offers multiple session types, including FetcherSession, DynamicSession, and StealthySession, for reliable and efficient scraping.  

Learn more in the [[official documentation](https://scrapling.readthedocs.io/en/latest/tutorials/external/?utm_source=github&utm_medium=integration&utm_campaign=scrapling)].


## Why Combine Scrapeless and Scrapling?

Scrapling excels at high-performance web data extraction, supporting adaptive scraping and AI integration. It comes with multiple built-in Fetcher classes — **Fetcher**, **DynamicFetcher**, and **StealthyFetcher** — to handle various scenarios. However, when facing advanced anti-bot mechanisms or large-scale concurrent scraping, several challenges may still arise:

- Local browsers can be easily blocked by Cloudflare, AWS WAF, or reCAPTCHA.  
- High browser resource consumption limits performance during large-scale concurrent scraping.  
- Although StealthyFetcher has built-in stealth capabilities, extreme anti-bot scenarios may still require stronger infrastructure support.  
- Debugging failures can be complicated, making it difficult to pinpoint the root cause.  

[Scrapeless Cloud Browser](https://www.scrapeless.com/en/product/scraping-browser?utm_source=github&utm_medium=integration&utm_campaign=scrapling) effectively addresses these challenges:

- **One-Click Anti-Bot Bypass** – Automatically handles reCAPTCHA, Cloudflare Turnstile/Challenge, AWS WAF, and other verifications. Combined with Scrapling’s adaptive extraction, success rates are significantly improved.  
- **Unlimited Concurrent Scaling** – Each task can launch 50–1000+ browser instances within seconds, removing local performance bottlenecks and maximizing Scrapling’s high-performance potential.  
- **Cost Reduction by 40–80%** – Compared to similar cloud services, Scrapeless costs only 20–60% overall and supports pay-as-you-go billing, making it affordable even for small projects.  
- **Visual Debugging Tools** – Monitor Scrapling execution in real time with Session Replay and Live URL, quickly identify scraping failures, and reduce debugging costs.  
- **Flexible Integration** – Scrapling’s DynamicFetcher and PlaywrightFetcher (built on Playwright) can connect to Scrapeless Cloud Browser via configuration without rewriting existing logic.  
- **Edge Service Nodes** – Global nodes offer startup speed and stability 2–3× faster than other cloud browsers, with over 90 million trusted residential IPs across 195+ countries, accelerating Scrapling execution.  
- **Isolated Environments & Persistent Sessions** – Each Scrapeless profile runs in an isolated environment, supporting persistent logins and session separation to improve stability for large-scale scraping.  
- **Flexible Fingerprint Configuration** – Scrapeless can randomly generate or fully customize browser fingerprints. When paired with Scrapling’s StealthyFetcher, detection risk is further reduced and success rates increase.

## Getting Started
[Log in to Scrapeless](https://app.scrapeless.com/passport/login?utm_source=github&utm_medium=integration&utm_campaign=scrapling) and get your API Key.

![Log in to Scrapeless and get your API Key](https://assets.scrapeless.com/prod/posts/scrapling/f96ce3bfdb6b2b9a11cf8dc6bcae67f6.png)


## Prerequisites

- **Python 3.10+**  
- **A registered Scrapeless account with a valid API Key**  
- **Install Scrapling** (or use the Docker image):

```bash
pip install scrapling

# If you need fetchers (dynamic/stealth):
pip install "scrapling[fetchers]"

# Install browser dependencies
scrapling install
````

* **Or use the official Docker image**:

```bash
docker pull pyd4vinci/scrapling
# or
docker pull ghcr.io/d4vinci/scrapling:latest
```

## Quickstart — Connect to Scrapeless Cloud Browser Using DynamicSession

Here is the simplest example: connect to the Scrapeless Cloud Browser WebSocket endpoint using `DynamicSession` provided by Scrapling, then fetch a page and print the response.

```
from urllib.parse import urlencode

from scrapling.fetchers import DynamicSession

# Configure your browser session
config = {
    "token": "YOUR_API_KEY",
    "sessionName": "scrapling-session",
    "sessionTTL": "300",  # 5 minutes
    "proxyCountry": "ANY",
    "sessionRecording": "false",
}

# Build WebSocket URL
ws_endpoint = f"wss://browser.scrapeless.com/api/v2/browser?{urlencode(config)}"
print('Connecting to Scrapeless...')

with DynamicSession(cdp_url=ws_endpoint, disable_resources=True) as s:
    print("Connected!")
    page = s.fetch("https://httpbin.org/headers", network_idle=True)
    print(f"Page loaded, content length: {len(page.body)}")
    print(page.json())

```
> Note: The Scrapeless Cloud Browser supports [configurable proxy options](https://docs.scrapeless.com/en/scraping-browser/features/advanced-privacy-anti-detection/custom-fingerprint/?utm_source=official&utm_medium=blog&utm_campaign=scrapling), such as proxy country, custom fingerprint settings, [CAPTCHA solving](https://docs.scrapeless.com/en/scraping-browser/features/advanced-privacy-anti-detection/supported-captchas/?utm_source=official&utm_medium=blog&utm_campaign=scrapling), and more.  
> Refer to the [Scrapeless browser documentation](https://docs.scrapeless.com/en/scraping-browser/quickstart/introduction/?utm_source=github&utm_medium=integration&utm_campaign=scrapling) for more detailed information.

## Common Use Cases (with Full Examples)

Here we demonstrate a typical practical scenario combining Scrapling and Scrapeless.  

💡 Before getting started, make sure that you have:  
- Installed dependencies using `pip install "scrapling[fetchers]"`
- Downloaded the browser with `scrapling install`;  
- Obtained a valid API Key from the Scrapeless dashboard;  
- Python 3.10+ installed.  

---

### Scraping Amazon with Scrapling + Scrapeless

Below is a complete Python example for scraping Amazon product details.  

The script automatically connects to the Scrapeless Cloud Browser, loads the target page, detects anti-bot protections, and extracts core information such as:  
- Product title  
- Price  
- Stock status  
- Rating  
- Number of reviews  
- Feature descriptions  
- Product images  
- ASIN  
- Seller information  
- Categories

```
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

```

**Sample Output:**
```
{
  "title": "ESR for iPhone 15 Pro Max Case, Compatible with MagSafe, Military-Grade Protection, Yellowing Resistant, Scratch-Resistant Back, Magnetic Phone Case for iPhone 15 Pro Max, Classic Series, Clear",
  "price_raw": "$12.99",
  "price": 12.99,
  "currency": "$",
  "rating": 4.6,
  "review_count": 133714,
  "availability": "In Stock",
  "features": [
    "Compatibility: only for iPhone 15 Pro Max; full functionality maintained via precise speaker and port cutouts and easy-press buttons",
    "Stronger Magnetic Lock: powerful built-in magnets with 1,500 g of holding force enable faster, easier place-and-go wireless charging and a secure lock on any MagSafe accessory",
    "Military-Grade Drop Protection: rigorously tested to ensure total protection on all sides, with specially designed Air Guard corners that absorb shock so your phone doesn\u2019t have to",
    "Raised-Edge Protection: raised screen edges and Camera Guard lens frame provide enhanced scratch protection where it really counts",
    "Stay Original: scratch-resistant, crystal-clear acrylic back lets you show off your iPhone 15 Pro Max\u2019s true style in stunning clarity that lasts",
    "Complete Customer Support: detailed setup videos and FAQs, comprehensive 12-month protection plan, lifetime support, and personalized help."
  ],
  "description": "BrandESRCompatible Phone ModelsiPhone 15 Pro MaxColorA-ClearCompatible DevicesiPhone 15 Pro MaxMaterialAcrylic",
  "images": [
    "https://m.media-amazon.com/images/I/71-ishbNM+L._AC_SL1500_.jpg",
    "https://m.media-amazon.com/images/I/71-ishbNM+L._AC_SX342_.jpg",
    "https://m.media-amazon.com/images/I/71-ishbNM+L._AC_SX679_.jpg",
    "https://m.media-amazon.com/images/I/71-ishbNM+L._AC_SX522_.jpg",
    "https://m.media-amazon.com/images/I/71-ishbNM+L._AC_SX385_.jpg",
    "https://m.media-amazon.com/images/I/71-ishbNM+L._AC_SX466_.jpg",
    "https://m.media-amazon.com/images/I/71-ishbNM+L._AC_SX425_.jpg",
    "https://m.media-amazon.com/images/I/71-ishbNM+L._AC_SX569_.jpg",
    "https://m.media-amazon.com/images/I/41Ajq9jnx9L._AC_SR38,50_.jpg",
    "https://m.media-amazon.com/images/I/51RkuGXBMVL._AC_SR38,50_.jpg",
    "https://m.media-amazon.com/images/I/516RCbMo5tL._AC_SR38,50_.jpg",
    "https://m.media-amazon.com/images/I/51DdOFdiQQL._AC_SR38,50_.jpg",
    "https://m.media-amazon.com/images/I/514qvXYcYOL._AC_SR38,50_.jpg",
    "https://m.media-amazon.com/images/I/518CS81EFXL._AC_SR38,50_.jpg",
    "https://m.media-amazon.com/images/I/413EWAtny9L.SX38_SY50_CR,0,0,38,50_BG85,85,85_BR-120_PKdp-play-icon-overlay__.jpg",
    "https://images-na.ssl-images-amazon.com/images/G/01/x-locale/common/transparent-pixel._V192234675_.gif"
  ],
  "asin": "B0CC1F4V7Q",
  "merchant": "Minghutech-US",
  "categories": [
    "Cell Phones & Accessories",
    "Cases, Holsters & Sleeves",
    "Basic Cases"
  ],
  "url": "https://www.amazon.com/ESR-Compatible-Military-Grade-Protection-Scratch-Resistant/dp/B0CC1F4V7Q",
  "scrapedAt": "2025-10-30T10:20:16Z"
}

```

This example demonstrates how DynamicSession and Scrapeless can work together to create a stable, reusable long-session environment.

Within the same session, you can request multiple pages without restarting the browser, maintain login states, cookies, and local storage, and achieve profile isolation and session persistence.



