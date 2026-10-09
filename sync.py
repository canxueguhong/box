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

    # POST提交文本，不再拼在URL上，规避414
    payload = {
        "id": key,
        "data": content
    }
    res = requests.post("https://textdb.online/update/", data=payload, timeout=60)
    print("textdb返回内容:", res.text)

if __name__ == "__main__":
    main()
