import requests
import json,re,os,sys,time
from datetime import timezone
from datetime import timedelta
from datetime import datetime
requests.packages.urllib3.disable_warnings()

        
headers = {
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'
}

def dingdingsend(text):  # 钉钉发信模块
    dingdingurl = 'https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxx'
    headers = {
        'Content-Type': 'application/json',
    }
    data = {"msgtype": "text", "text": {"content": text}}
    try:
        r = requests.post(dingdingurl, json=data, headers=headers)
    except:
        pass

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

    with open(filePath,'r+') as f:
        url = f.readline()
        if source == url:
            return False
        else:
            f.write(source)
            return True


def getContent(UserId,containerid):
    url = "https://m.weibo.cn/api/container/getIndex?jumpfrom=weibocom&type=uid&value={}&containerid={}".format(UserId,containerid)
    content = requests.get(url, headers=headers,timeout=15,verify=False).text
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
    content = requests.get(url, headers=headers,timeout=15,verify=False).text
    containerid = (json.loads(content))['data']['tabsInfo']['tabs'][1]['containerid']
    return containerid

#微博获得历史记录需要三个参数:用户id，fid，containerid
def getFid(UserId):
    url = "https://m.weibo.cn/u/{}?jumpfrom=weibocom".format(UserId)
    content = requests.get(url, headers=headers,timeout=15,verify=False)
    setCookie = content.headers
    fid = re.findall("%3D(.*?)%26", setCookie['Set-Cookie'])[0]
    return fid

def getUser(UserId):
    while True:
        for id in UserId:
            id = id.strip('\n')
            fid = getFid(id)
            containerid = getContainerid(fid,id)
            response = getContent(id,containerid)
            content = response[0] #发布的微博内容
            source = response[1] #发布的微博URL地址
            if saveContent(id,source):
                dingdingTime = str(getTime())[0:-13] #境外服务器时间协调后的当前时间
                # print("#微博监控\ntime: {}\ncontent: {}\naddress: {}".format(dingdingTime,content,source))
                dingdingsend("#微博监控\ntime: {}\ncontent: {}\naddress: {}".format(dingdingTime,content,source))
            time.sleep(10)
        time.sleep(30)

if __name__ == "__main__":
    with open('weiboID.txt','r') as r:
        getUser(r)
