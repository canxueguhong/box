import requests
import os

def main():
    key = os.environ["TEXTDB_KEY"]
    print("DEBUG key value:", repr(key))

    source_url = "https://tvbox.xiaoy93.ccwu.cc"
    resp = requests.get(source_url, timeout=30)
    resp.encoding = "utf-8"
    content = resp.text

    # 替换镜像
    content = content.replace(
        "https://raw.githubusercontent.com",
        "https://ghfast.top/https://raw.githubusercontent.com"
    )

    # ⚠️重点：data参数放前面，files放后面，模拟浏览器表单顺序
    data = {
        "key": key
    }
    files = {
        "value": ("config.json", content, "text/plain")
    }

    res = requests.post("https://textdb.online/update/", data=data, files=files, timeout=60)
    print("textdb返回内容:", res.text)

if __name__ == "__main__":
    main()
