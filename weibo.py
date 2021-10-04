import requests
import json,re,os,sys,time,random
from datetime import timezone
from datetime import timedelta
from datetime import datetime
requests.packages.urllib3.disable_warnings()

def usera():
    #user_agent 集合
    user_agent_list = [
     'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
     'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
     'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
     'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
     'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
     'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
     'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
     'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
     'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
     'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    ]
    #随机选择一个
    user_agent = random.choice(user_agent_list)
    #传递给header
    headers = { 'User-Agent': user_agent }
    return headers

def dingdingsend(text):  # 钉钉发信模块
    dingdingurl = 'https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxx'
    headers = {
        'Content-Type': 'application/json',
    }
    data = {"msgtype": "text", "text": {"content": text}}
    try:
        r = requests.post(dingdingurl, json=data, headers=headers)
    except Exception as e:
        print(e)
        # pass

def getTime():
    SHA_TZ = timezone(
        timedelta(hours=8),
        name='Asia/Shanghai',
    )
    # 协调世界时
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    beijing_now = utc_now.astimezone(SHA_TZ)
    return (beijing_now)

def saveContent(UserId,source):
    path = os.path.dirname(os.path.realpath(sys.argv[0])) + "/history"
    filePath = "{}/{}.txt".format(path,UserId)
    if not os.path.exists(filePath):
        history = open(filePath,'w')
        history.close()
    with open(filePath,'r') as r:
        url = r.readline()
        if source == url:
            return False
        else:
            with open(filePath,'w') as w:
                w.write(source)
            return True


def getContent(UserId,containerid):
    url = "https://m.weibo.cn/api/container/getIndex?jumpfrom=weibocom&type=uid&value={}&containerid={}".format(UserId,containerid)
    content = requests.get(url, headers=usera(),timeout=15,verify=False).text
    try:
        isTop = (json.loads(content))['data']['cards'][0]['mblog']['title']['text']
        if "置顶" in isTop:
            push = (json.loads(content))['data']['cards'][1]['mblog']['text']
            scheme = re.findall("status/(.*?)\?", (json.loads(content))['data']['cards'][1]['scheme'])[0]
        else:
            push = (json.loads(content))['data']['cards'][0]['mblog']['text']
            scheme = re.findall("status/(.*?)\?", (json.loads(content))['data']['cards'][0]['scheme'])[0]
    except:
        push = (json.loads(content))['data']['cards'][0]['mblog']['text']
        scheme = re.findall("status/(.*?)\?", (json.loads(content))['data']['cards'][0]['scheme'])[0]
    content = re.sub("<a.*?</a>","",push)
    source = "https://weibo.com/{}/{}".format(UserId,scheme)
    return content,source

def getContainerid(fid,UserId):
    url = "https://m.weibo.cn/api/container/getIndex?jumpfrom=weibocom&type=uid&value={}&containerid={}".format(UserId,fid)
    content = requests.get(url, headers=usera(),timeout=15,verify=False).text
    containerid = (json.loads(content))['data']['tabsInfo']['tabs'][1]['containerid']
    return containerid

#微博获得历史记录需要三个参数:用户id，fid，containerid
def getFid(UserId):
    url = "https://m.weibo.cn/u/{}?jumpfrom=weibocom".format(UserId)
    content = requests.get(url, headers=usera(),timeout=15,verify=False)
    setCookie = content.headers
    fid = re.findall("%3D(.*?)%26", setCookie['Set-Cookie'])[0]
    return fid

def getUser(UserId):
    while True:
        for id in UserId:
            try:
                id = id.strip('\n')
                fid = getFid(id)
                containerid = getContainerid(fid,id)
                response = getContent(id,containerid)
                content = response[0] #发布的微博内容
                source = response[1] #发布的微博URL地址
                dingdingTime = str(getTime())[0:-13] #境外服务器时间协调后的当前时间
                if saveContent(id,source):
                    print("#微博监控\ntime: {}\ncontent: {}\naddress: {}".format(dingdingTime,content,source))
                    dingdingsend("#微博监控\ntime: {}\ncontent: {}\naddress: {}".format(dingdingTime,content,source))
                else:
                    print("#微博监控\ntime: {}\ncontent: {}\naddress: {}".format(dingdingTime,content,source))
            except Exception as e:
                print(e)
                bark = 'https://api.day.app/BfGpbdX6ZRMUJDnWuxxxx/斯文爸爸，您的微博监控程序运行出错，请注意检查'
                requests.get(bark,verify=False,timeout=20)

            time.sleep(20)
        time.sleep(30)

if __name__ == "__main__":
    with open('weiboID.txt','r') as r:
        getUser(r)
