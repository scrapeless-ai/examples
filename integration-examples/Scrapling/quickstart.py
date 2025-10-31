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
