import requests
import base64
import os

def main():
    key = os.environ["TEXTDB_KEY"]
    source_url = "https://tvbox.xiaoy93.ccwu.cc"

    resp = requests.get(source_url, timeout=30)
    resp.raise_for_status()
    content = resp.text

    content = content.replace(
        "https://raw.githubusercontent.com",
        "https://ghfast.top/https://raw.githubusercontent.com"
    )

    b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    payload = {
        "key": key,
        "data": b64,
        "encode": "base64"
    }
    res = requests.post("https://textdb.online/api", json=payload, timeout=30)
    print("textdb返回内容：", res.text)

if __name__ == "__main__":
    main()
