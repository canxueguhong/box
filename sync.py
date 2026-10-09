import requests
import base64
import os

def main():
    key = os.environ["TEXTDB_KEY"]
    source_url = "https://tvbox.xiaoy93.ccwu.cc"

    resp = requests.get(source_url, timeout=30)
    resp.raise_for_status()
    content = resp.text

    # 替换raw资源镜像
    content = content.replace(
        "https://raw.githubusercontent.com",
        "https://ghfast.top/https://raw.githubusercontent.com"
    )

    # url编码，textdb用url传value，不是base64
    from urllib.parse import quote
    value_encoded = quote(content)

    # textdb update接口
    api_url = f"https://textdb.online/update/?key={key}&value={value_encoded}"
    res = requests.get(api_url, timeout=30)
    print("textdb返回内容:", res.text)

if __name__ == "__main__":
    main()
