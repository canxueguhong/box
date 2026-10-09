import requests
import os

def main():
    key = os.environ["TEXTDB_KEY"]
    print("DEBUG key value:", repr(key))
    source_url = "https://tvbox.xiaoy93.ccwu.cc"
    resp = requests.get(source_url, timeout=30)
    resp.raise_for_status()
    resp.encoding = 'utf-8'
    content = resp.text

    # 替换raw镜像地址
    content = content.replace(
        "https://raw.githubusercontent.com",
        "https://ghfast.top/https://raw.githubusercontent.com"
    )

    # ✅ 用表单data字典，key和value，这是textdb网页端提交的标准格式
    payload = {
        "key": key,
        "value": content
    }
    res = requests.post("https://textdb.online/update/", data=payload, timeout=60)
    print("textdb返回内容:", res.text)

if __name__ == "__main__":
    main()
