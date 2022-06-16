import json
import re
import string
import urllib.request

import xlrd
import xlwt
from pypinyin import lazy_pinyin, pinyin

import requests
from bs4 import BeautifulSoup

from tqdm import tqdm

corona_virus = []
cities_virus = []
cs = []


class ConronVirusSpider(object):
    def __init__(self):
        self.url = 'https://ncov.dxy.cn/ncovh5/view/pneumonia'

    def chinesedata(self):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        }
        # url，网址
        url = 'http://www.hkwb.net/node_32247.html'
        # 通过request类来构造请求
        res = urllib.request.Request(url, headers=headers)
        # 通过urlopen方法访问页面并返回 HTTPResposne 对象
        response = urllib.request.urlopen(res)
        # 通过read()方法读取字节流并解码成字符串
        html = response.read().decode('utf-8')
        pattren1 = re.compile(r'(?:<.+font-size:16px; height:30px; line-height:30px; tex'
                              r't-align:center; font-weight:bold; color:#900;">)(.+)(?:</div>)')
        confirmedCount = re.findall(pattren1, html)[0]
        pattren2 = re.compile(r'(?:<.+font-size:12px; height:30px; line-height:30px; tex'
                              r't-align:center; font-weight:bold; color:#900;">)(.+)(?:</div>)')
        confirmedCountIntr = re.findall(pattren2, html)[0]
        pattren3 = re.compile(r'(?:<.+font-size:16px; height:30px; line-height:30px; tex'
                              r't-align:center; font-weight:bold; color:#C63;">)(.+)(?:</div>)')
        curedCount = re.findall(pattren3, html)[0]
        pattren4 = re.compile(r'(?:<.+font-size:12px; height:30px; line-height:30px; tex'
                              r't-align:center; font-weight:bold; color:#c63;">)(.+)(?:</div>)')
        curedIncr = re.findall(pattren4, html)[0]
        pattren5 = re.compile(r'(?:<.+font-size:16px; height:30px; line-height:30px; tex'
                              r't-align:center; font-weight:bold; color:#093;">)(.+)(?:</div>)')
        pattren6 = re.compile(r'(?:<.+font-size:12px; height:30px; line-height:30px; tex'
                              r't-align:center; font-weight:bold; color:#093;">)(.+)(?:</div>)')
        deadCount = re.findall(pattren5, html)[0]
        deadIncr = re.findall(pattren6, html)[0]
        pattren7 = re.compile(r'(?:<.+font-size:13px; height:30px; line-height:30px; tex'
                              r't-align:center; font-weight:bold; color:#333;">)(.+)(?:</div>)')
        outsideInputCount = re.findall(pattren7, html)[0]
        pattren8 = re.compile(r'(?:<.+font-size:12px; height:30px; line-height:30px; tex'
                              r't-align:center; font-weight:bold; color:#333;">)(.+)(?:</div>)')
        outsideInputIncr = re.findall(pattren8, html)[0]

        asymptomaticInfectionCount = re.findall(pattren7, html)[1]
        asymptomaticInfectionIncr = re.findall(pattren8, html)[1]

        data = {}
        data["confirmedCountIncr"] = int(confirmedCountIntr)
        data["confirmedCount"] = int(confirmedCount)
        data["deadIncr"] = int(deadIncr)
        data["deadCount"] = int(deadCount)
        data["outsideInputCount"] = int(outsideInputCount)
        data["outsideInputIncr"] = int(outsideInputIncr)
        data["asymptomaticInfectionIncr"] = int(asymptomaticInfectionIncr)
        data["asymptomaticInfectionCount"] = int(asymptomaticInfectionCount)
        data["curedCount"] = int(curedCount)
        data["curedIncr"] = int(curedIncr)
        chinesedata = []
        chinesedata.append(data)
        self.save(chinesedata, './chinesedata.json')


    def get_content_from_url(self, url):
        response = requests.get(url)
        return response.content.decode()

    def parse_html(self, html):
        soup = BeautifulSoup(html, 'lxml')
        script = soup.find(id="getAreaStat")
        text = script.text
        json_str = re.findall(r'\[.+\]', text)[0]
        data = json.loads(json_str)
        return data

    def save(self, data, path):
        with open(path, 'w', encoding="utf-8") as fp1:
            json.dump(data, fp1, ensure_ascii=False)

    def crawl_lastday_conron_virus(self):
        # 发送请求获取首页内容
        home_page = self.get_content_from_url(self.url)
        # 解析首页内容获取最近一天的数据
        lastday_conron_virus = self.parse_html(home_page)
        # 保存数据
        self.save(lastday_conron_virus, "./last_day_corona_virus.json")

    # 汉字中加入间隔符号’
    def chinese(self, s):
        t = ""
        for i in range(len(s)):
            t = t + "‘" + s[i]
        return t

    def crawl_conron_virus(self):

        with open('./last_day_corona_virus.json', encoding="utf-8") as fp2:
            last_day_corona_virus = json.load(fp2)
        i = 1
        city_viurs = {}
        for province in tqdm(last_day_corona_virus):
            statistics_data_url = province['statisticsData']
            cities_data = province["cities"]
            statistics_data_json_str = self.get_content_from_url(statistics_data_url)
            statistics_data = json.loads(statistics_data_json_str)["data"]
            for aa in cities_data:

                del(aa["suspectedCount"])
                del (aa["curedCount"])
                del (aa["deadCount"])
                del (aa["highDangerCount"])
                del (aa["midDangerCount"])
                del (aa["locationId"])
                del(aa["currentConfirmedCountStr"])
                aa["provinceShortName"] = province["provinceShortName"]
            cities_virus.extend(cities_data)
            if province["provinceShortName"] == "山西":
                province["provinceShortName"] = "三晋"

            lp = lazy_pinyin(province["provinceShortName"])

            for one_day in statistics_data:
                # one_day["provinceName"]=province["provinceName"]
                if len(lp) == 2:
                    one_day["provinceShortName"] = lp[0] + lp[1]
                if len(lp) == 3:
                    one_day["provinceShortName"] = lp[0] + lp[1] + lp[2]
            corona_virus.extend(statistics_data)

        self.save(corona_virus, './corona_virus.json')
        self.save(cities_virus, './cities_virus.json')

    def run(self):
        self.crawl_conron_virus()
        self.chinesedata()





if __name__ == '__main__':
    spider = ConronVirusSpider()
    spider.run()
