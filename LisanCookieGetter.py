import browser_cookie3
import urllib.parse
import requests

# def __getAuthenToken__(url):
#     #token looks like:
#     #<input name="authenticity_token" type="hidden" value="imTK6Cy0MCZl6dJqWIjRpgSfW9laIuskxUNIfHYRG0s=">
#     r = requests.get(url)
#     pattern = '<input name="authenticity_token".+?value="(.+?)"'
#
#     token = regex.findall(pattern,r.text)[0]
#     return token

def __makeCookieDict__(cookieThing):
    cookieDict = {}
    for name, cookie in cookieThing.items():
        cookieDict[name] = cookie.value
    return cookieDict

def getLoginCookie(domain,url_login,username,password):
    cj = browser_cookie3.chrome(domain_name=domain)
    if 'autologin_trustie' in cj._cookies[domain]['/'].keys():
        #already have cookie, return it
        return __makeCookieDict__(cj._cookies[domain]['/'])
    #else, make one
    # token = __getAuthenToken__(url_login)
    postDict = {
        'utf8': '✓',
        # 'authenticity_token': token,
        'back_url': 'https://www.educoder.net/',
        'username': username,
        'password': password,
        'autologin': '1',
    }
    postData = urllib.parse.urlencode(postDict)
    header = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    req = requests.post(url_login,postData,headers=header)
    resp = req.request
    if 'autologin_trustie' in resp._cookies._cookies[domain]['/'].keys():
        #login successful
        return __makeCookieDict__(resp._cookies._cookies[domain]['/'])
    #fail
    return {}
