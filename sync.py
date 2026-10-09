import requests
import os

def main():
    key = os.environ["TEXTDB_KEY"]
    print("DEBUG key value:", repr(key))

    # 拉取源配置
    source_url = "https://tvbox.xiaoy93.ccwu.cc"
    resp = requests.get(source_url, timeout=30)
    resp.encoding = "utf-8"
    content = resp.text

    # 替换github raw镜像
    content = content.replace(
        "https://raw.githubusercontent.com",
        "https://ghfast.top/https://raw.githubusercontent.com"
    )

    # 重点！模拟网页：把json文本作为文件上传（multipart/form-data）
    files = {
        "value": ("config.json", content, "text/plain")
    }
    data = {
        "key": key
    }

    res = requests.post("https://textdb.online/update/", files=files, data=data, timeout=60)
    print("textdb返回内容:", res.text)

if __name__ == "__main__":
    main()
