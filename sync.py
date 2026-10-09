import requests
import os

def main():
    key = os.environ["TEXTDB_KEY"]
    print("DEBUG key value:", repr(key))
    source_url = "https://tvbox.xiaoy93.ccwu.cc"
    resp = requests.get(source_url, timeout=30)
    resp.raise_for_status()
    content = resp.text

    # 替换raw镜像地址
    content = content.replace(
        "https://raw.githubusercontent.com",
        "https://ghfast.top/https://raw.githubusercontent.com"
    )

    # key放在url参数，body直接传文本
    url = f"https://textdb.online/update/?key={key}"
    res = requests.post(url, data=content, timeout=60)
    print("textdb返回内容:", res.text)

if __name__ == "__main__":
    main()
