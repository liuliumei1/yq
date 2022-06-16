import json
import urllib.request
import re

from bs4 import BeautifulSoup
from lxml import etree
#我是
headers = {
    'user-agent': 'http://www.sy72.com/covid19/'
}
# url，网址
url = 'https://ncov.dxy.cn/ncovh5/view/pneumonia'
# 通过request类来构造请求
res = urllib.request.Request(url, headers=headers)
# 通过urlopen方法访问页面并返回 HTTPResposne 对象
response = urllib.request.urlopen(res)
# 通过read()方法读取字节流并解码成字符串
html = response.read().decode('utf-8')

soup = BeautifulSoup(html, 'lxml')
text = soup.find(id="getAreaStat")

json_str = re.findall(r'\[.+\]', str(text))[0]
last_day_corona_virus = json.loads(json_str)
print(last_day_corona_virus)

with open('./last_day_corona_virus.json','w',encoding="utf-8") as fp :
    json.dump(last_day_corona_virus,fp,ensure_ascii=False)

