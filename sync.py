import requests
import os

def main():
    key = os.environ["TEXTDB_KEY"]
    print("DEBUG key value:", repr(key))

    source_url = "https://tvbox.xiaoy93.ccwu.cc"
    resp = requests.get(source_url, timeout=30)
    resp.encoding = "utf-8"
    content = content = resp.text.replace("https://raw.githubusercontent.com", "https://ghfast.top/https://raw.githubusercontent.com")

    # 写入本地临时文件
    with open("/tmp/config.json","w",encoding="utf-8") as f:
        f.write(content)

    data = {"key": key}
    files = {"value": open("/tmp/config.json","rb")}

    res = requests.post("https://textdb.online/update/", data=data, files=files, timeout=60)
    print("textdb返回内容:", res.text)

if __name__ == "__main__":
    main()
