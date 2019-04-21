# -*- coding: UTF-8 -*-
import requests
import urllib3
import json
import time
import sched
import subprocess
import shlex

site_list = ['北京','上海','成都','武汉','广州']
weather_list = ['大雨','阴天','小雨','多云']

def extract(text):
    info = {}
    for site in site_list:
        if text.find(site) != -1:
            info['site'] = site

    for weather in weather_list:
        if text.find(weather) != -1:
            info['weather'] = weather
    return info


class weiboMonitor():
    def __init__(self, value ,containerid):
        self.session = requests.session()
        self.weiboInfo = "https://m.weibo.cn/api/container/getIndex?type=uid&value={}&containerid={}".format(value,containerid)

        self.reqHeaders = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://passport.weibo.cn/signin/login',
            'Connection': 'close',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'
        }

    #获取containerid( https://m.weibo.cn/api/container/getIndex?type=uid&value=6179067755)
    def getWBQueue(self):
        net_disabled()
        response = self.session.get(self.weiboInfo, headers=self.reqHeaders)
        self.items = set()
        for item in response.json()["data"]["cards"]:
            print(item['scheme'])
            self.items.add(item['scheme'])
        return self.items
       
def startMonitor(obj):
    new_weibo_list = list()
    response = obj.session.get(obj.weiboInfo, headers=obj.reqHeaders)
    for card in response.json()["data"]['cards']:
        if str(card['scheme']) not in obj.items:
            obj.items.add(card['scheme'])
            return_dict = {}
            #return_dict['created_at'] = card['mblog']['created_at']
            
            return_dict['text'] = card['mblog']['text']
            #return_dict['scheme'] = card['scheme']
            info = extract(return_dict['text'])
            
            if len(info)==2:
                new_weibo_list.append(info)
    if new_weibo_list:
        net_enabled()#打开本地连接 向服务器发送消息
        restapi_post(json.dumps(new_weibo_list,ensure_ascii=False).encode("UTF-8"),"http://192.168.0.9:10000/api/rest/das/meteorological/data/access")
        net_disabled() #发送完毕就关闭本地连接

def restapi_post(data, requrl):
    http=urllib3.PoolManager();
    print(data)
    res=http.request("POST",requrl,body=data,headers={"Content-Type":"application/json"})
    print(res.status)
    if str(res.status) == "200":
            
            return True
    else:
            return False

def net_disabled():
    args=shlex.split('netsh interface set interface "本地连接" disabled')
    print(args)
    subprocess.Popen(args,shell=False)
    
def net_enabled():
    args=shlex.split('netsh interface set interface "本地连接" enabled')
    print(args)
    subprocess.Popen(args,shell=False)


if __name__ == "__main__":
    weibo =weiboMonitor(value="6179067755",containerid="1076036179067755")
    weibo.getWBQueue()
    s = sched.scheduler(time.time, time.sleep)
    while True:
        time.sleep(2)
        s.enter(3, 0, startMonitor, argument=(weibo,))
        s.run()








