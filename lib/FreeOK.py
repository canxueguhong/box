# -*- coding: utf-8 -*-
import json
import re
import sys
import os
from urllib.parse import quote

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from base.spider import Spider as BaseSpider
except ImportError:
    class BaseSpider:
        def __init__(self, query_params=None, t4_api=None):
            self.query_params = query_params or {}
            self.t4_api = t4_api or ''
            self.extend = ''
            self.ENV = 'T3'
            self._cache = {}

        def fetch(self, url, params=None, headers=None, cookies=None, timeout=8, **kwargs):
            import requests
            return requests.get(url, params=params, headers=headers,
                                cookies=cookies, timeout=timeout, verify=False)


class Spider(BaseSpider):
    SITE_URL = "https://freeok-tv.com"
    DEBUG = False

    CATEGORY_MAP = {
        "电影": "1", "电视剧": "2", "综艺": "3", "动漫": "4", "短剧": "20",
    }

    HEADERS = {
        "User-Agent": ("Mozilla/5.0 (Linux; Android 12; Pixel 5) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Mobile Safari/537.36"),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": SITE_URL + "/",
    }

    def init(self, extend=""):
        self.extend = extend
        return {"status": 0}

    def getName(self):
        return "🅿️FreeOK"

    def isVideoFormat(self, url):
        if not url or not isinstance(url, str):
            return False
        return any(x in url.lower() for x in ('.m3u8', '.mp4', '.ts', '.mkv', '.flv'))

    def manualVideoCheck(self):
        return False

    def _log(self, msg):
        if self.DEBUG:
            print(f"[FreeOK] {msg}")

    def _get(self, url):
        try:
            rsp = self.fetch(url, headers=self.HEADERS)
            rsp.encoding = "utf-8"
            return rsp.text or ""
        except Exception as e:
            print(f"[FreeOK] GET failed {url}: {e}")
            return ""

    # ============ 首页 ============

    def homeContent(self, filter=False):
        classes = [{"type_id": t, "type_name": n} for n, t in self.CATEGORY_MAP.items()]
        filters = {}
        if filter:
            for n, t in self.CATEGORY_MAP.items():
                filters[t] = self._build_filters()
        return {"class": classes, "filters": filters}

    def _build_filters(self):
        areas = [("全部", ""), ("大陆", "大陆"), ("香港", "香港"), ("台湾", "台湾"),
                 ("美国", "美国"), ("法国", "法国"), ("英国", "英国"),
                 ("日本", "日本"), ("韩国", "韩国"), ("泰国", "泰国")]
        years = [("全部", ""), ("2026", "2026"), ("2025", "2025"), ("2024", "2024"),
                 ("2023", "2023"), ("2022", "2022"), ("2021", "2021"),
                 ("2020", "2020"), ("2019", "2019")]
        return [
            {"key": "area", "name": "地区", "value": [{"n": n, "v": v} for n, v in areas]},
            {"key": "year", "name": "年份", "value": [{"n": n, "v": v} for n, v in years]},
        ]

    def homeVideoContent(self):
        return {"list": self._parse_video_list(self._get(self.SITE_URL + "/"))}

    # ============ 分类 ============

    def categoryContent(self, tid, pg, filter, extend):
        try:
            pg = int(pg) if pg else 1
        except Exception:
            pg = 1

        if extend and isinstance(extend, dict) and any(str(v).strip() for v in extend.values()):
            parts = [str(tid)]
            if extend.get("area"):
                parts += ["area", quote(extend["area"], safe="")]
            if extend.get("year"):
                parts += ["year", extend["year"]]
            path = "/".join(parts)
            url = (f"{self.SITE_URL}/freeok-show/{path}/page/{pg}.html" if pg > 1
                   else f"{self.SITE_URL}/freeok-show/{path}.html")
        elif pg > 1:
            url = f"{self.SITE_URL}/freeok-show/{tid}/page/{pg}.html"
        else:
            url = f"{self.SITE_URL}/freeok-show/{tid}.html"

        html = self._get(url)
        videos = self._parse_video_list(html)
        pagecount = self._parse_pagecount(html, pg)
        return {"list": videos, "page": pg, "pagecount": pagecount,
                "limit": 20, "total": pagecount * 20}

    # ============ 搜索 ============

    def searchContent(self, key, quick, pg=1):
        try:
            url = f"{self.SITE_URL}/freeok-search.html"
            rsp = self.fetch(url, params={"wd": key}, headers=self.HEADERS)
            rsp.encoding = "utf-8"
            return {"list": self._parse_video_list(rsp.text)}
        except Exception as e:
            print(f"[FreeOK] searchContent: {e}")
            return {"list": []}

    # ============ 详情 ============

    def detailContent(self, ids):
        vod_id = ids[0] if isinstance(ids, list) else ids
        vod_id = str(vod_id).strip().strip("/").split("/")[-1].replace(".html", "")

        detail_html = self._get(f"{self.SITE_URL}/freeok-detail/{vod_id}.html")
        play_html = self._get(f"{self.SITE_URL}/freeok-play/{vod_id}-1-1.html")

        d = {"vod_id": str(vod_id), "vod_name": "", "vod_pic": "",
             "vod_content": "", "vod_actor": "", "vod_director": "",
             "vod_year": "", "vod_area": "", "vod_remarks": "",
             "vod_play_from": "", "vod_play_url": ""}

        m = (re.search(r'<h1 class="title_name">([^<]+)</h1>', detail_html)
             or re.search(r'<h1 class="title">([^<]+)</h1>', detail_html)
             or re.search(r'<h1[^>]*>([^<]+)</h1>', detail_html))
        if m:
            d["vod_name"] = m.group(1).strip()

        m = (re.search(r'<img[^>]+class="[^"]*cover-img[^"]*"[^>]+src="([^"]+)"', detail_html)
             or re.search(r'<img[^>]+class="lazyload"[^>]*?(?:data-original|src)="([^"]+)"', detail_html))
        if m:
            d["vod_pic"] = m.group(1).strip()

        m = re.search(r'<a class="tag" href="[^"]*/year/(\d+)\.html">', detail_html)
        if m:
            d["vod_year"] = m.group(1)

        m = re.search(r'<div class="director[^"]*"><div class="name">导演:</div>\s*([^<]+)</div>', detail_html)
        if m:
            d["vod_director"] = m.group(1).strip()

        m = re.search(r'<div class="director[^"]*"><div class="name">主演:</div>\s*([^<]+)</div>', detail_html)
        if m:
            d["vod_actor"] = m.group(1).strip()

        m = (re.search(r'<div class="wrapper_more_text">.*?<label[^>]*></label>(.*?)</div>', detail_html, re.S)
             or re.search(r'<div class="wrapper_more_text">.*?<p>(.*?)</p>', detail_html, re.S))
        if m:
            d["vod_content"] = re.sub(r'<[^>]+>', '', m.group(1)).strip()

        m = re.search(r'更新(第[^<\s]+集|至第[^<\s]+集|至[^<\s]+)', detail_html)
        if m:
            d["vod_remarks"] = m.group(0).strip()

        d["vod_play_from"], d["vod_play_url"] = self._parse_playlist(play_html, vod_id)
        return {"list": [d]}

    def _parse_playlist(self, html, vod_id):
        if not html:
            return "", ""

        vod_id = str(vod_id)
        sid_order, sid_to_name = [], {}

        # 线路顺序：PC 端 swiper（nav-tabs）按真实顺序排列
        m = (re.search(r'<ul[^>]*class="[^"]*swiper-wrapper[^"]*nav-tabs[^"]*"[^>]*>(.*?)</ul>', html, re.S)
             or re.search(r'<ul[^>]*class="[^"]*nav[^"]*swiper-wrapper[^"]*nav-tabs[^"]*"[^>]*>(.*?)</ul>', html, re.S))
        if m:
            for mm in re.finditer(
                r'<a\b[^>]*href="/freeok-play/' + re.escape(vod_id) +
                r'-(\d+)-\d+\.html"[^>]*>(.*?)</a>', m.group(1), re.S):
                sid, inner = mm.group(1), mm.group(2)
                if sid in sid_order:
                    continue
                for sm in re.finditer(r'<span[^>]*>([^<]+)</span>', inner):
                    txt = sm.group(1).strip()
                    if txt and not txt.isdigit():
                        sid_order.append(sid)
                        sid_to_name[sid] = txt
                        break

        # 兜底：移动端 tab href="#playlistN"
        if not sid_order:
            for mm in re.finditer(r'<a\s+href="#playlist(\d+)"[^>]*>([^<]+)<span', html):
                sid, name = mm.group(1), mm.group(2).strip()
                if sid not in sid_order and name:
                    sid_order.append(sid)
                    sid_to_name[sid] = name

        # 分集
        eps_by_sid, seen = {}, set()
        for mm in re.finditer(
            r'<a\b[^>]*href="/freeok-play/' + re.escape(vod_id) +
            r'-(\d+)-(\d+)\.html"[^>]*>([^<]*)</a>', html, re.S):
            sid, nid, name = mm.group(1), mm.group(2), mm.group(3).strip()
            key = (sid, nid)
            if key in seen:
                continue
            seen.add(key)
            eps_by_sid.setdefault(sid, []).append(
                (int(nid), name or f"第{int(nid):02d}集",
                 f"/freeok-play/{vod_id}-{sid}-{nid}.html"))

        for sid in eps_by_sid:
            if sid not in sid_order:
                sid_order.append(sid)
                sid_to_name.setdefault(sid, f"线路{sid}")

        from_list, url_list = [], []
        for sid in sid_order:
            if sid not in eps_by_sid:
                continue
            eps = sorted(eps_by_sid[sid], key=lambda x: x[0])
            from_list.append(sid_to_name.get(sid, f"线路{sid}"))
            url_list.append("#".join(f"{n}${h}" for _, n, h in eps))

        return "$$$".join(from_list), "$$$".join(url_list)

    # ============ 播放 ============

    def playerContent(self, flag, vid, vip_flags):
        hdr = {"User-Agent": self.HEADERS["User-Agent"], "Referer": self.SITE_URL + "/"}
        result = {"parse": 0, "playUrl": "", "url": "", "header": hdr, "headers": hdr}

        if isinstance(vid, str) and "$" in vid:
            vid = vid.split("$", 1)[-1]

        if isinstance(vid, str) and vid.startswith("/"):
            url = self.SITE_URL + vid
        elif isinstance(vid, str) and vid.startswith("http"):
            url = vid
        else:
            url = f"{self.SITE_URL}/freeok-play/{vid}.html"

        html = self._get(url)
        if not html:
            result["parse"] = 1
            result["url"] = url
            return result

        raw = self._extract_player_aaaa(html)
        if raw:
            pd = None
            for s in (raw, raw.replace("\\/", "/")):
                try:
                    pd = json.loads(s)
                    break
                except json.JSONDecodeError:
                    continue
            if isinstance(pd, dict):
                u = (pd.get("url") or "").replace("\\/", "/")
                if u and ("http" in u or ".m3u8" in u or ".mp4" in u):
                    result["url"] = self._safe_url_encode(u)
                    return result
                u2 = (pd.get("url_next") or "").replace("\\/", "/")
                if u2 and ("http" in u2 or ".m3u8" in u2):
                    result["url"] = self._safe_url_encode(u2)
                    return result

        text = html.replace("\\/", "/")
        m = re.search(r'(https?://[^"\'\s<>]+\.m3u8[^"\'\s<>]*)', text)
        if m:
            result["url"] = self._safe_url_encode(m.group(1))
            return result

        m = re.search(r'<iframe[^>]+src="([^"]+)"', text)
        if m and m.group(1).startswith("http") and "load.html" not in m.group(1):
            result["url"] = m.group(1)
            result["parse"] = 1
            return result

        result["parse"] = 1
        result["url"] = url
        return result

    def _extract_player_aaaa(self, html):
        idx = html.find("player_aaaa")
        if idx < 0:
            return ""
        start = html.find("{", idx)
        if start < 0:
            return ""
        depth, in_str, esc, i = 0, False, False, start
        while i < len(html):
            c = html[i]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
            else:
                if c == '"':
                    in_str = True
                elif c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        return html[start:i + 1]
            i += 1
        return ""

    @staticmethod
    def _safe_url_encode(url):
        if not url:
            return url
        try:
            return quote(url, safe=":/?#[]@!$&'()*+,;=%~")
        except Exception:
            return url

    # ============ 列表解析 ============

    def _parse_video_list(self, html):
        if not html:
            return []
        videos, seen = [], set()
        matches = list(re.finditer(r'<a href="(/freeok-detail/(\d+)\.html)"', html))
        for i, m in enumerate(matches):
            vid = m.group(2)
            if vid in seen:
                continue
            end = matches[i + 1].start() if i + 1 < len(matches) else min(m.start() + 4000, len(html))
            chunk = html[m.start():end]
            t = re.search(r'<div class="title">([^<]+)</div>', chunk)
            if not t:
                continue
            img = re.search(r'<img[^>]+?(?:data-original|src)="([^"]+)"', chunk)
            role = re.search(r'<div class="role">([^<]*)</div>', chunk)
            seen.add(vid)
            videos.append({
                "vod_id": vid,
                "vod_name": t.group(1).strip(),
                "vod_pic": img.group(1).strip() if img else "",
                "vod_remarks": role.group(1).strip() if role else "",
            })
        return videos

    def _parse_pagecount(self, html, current_pg):
        m = re.search(r'共\s*(\d+)\s*页', html)
        if m:
            return int(m.group(1))
        pages = re.findall(r'/freeok-show/\d+/page/(\d+)\.html', html)
        if pages:
            return max(int(p) for p in pages)
        return int(current_pg) + 1


def main():
    pass


if __name__ == "__main__":
    main()