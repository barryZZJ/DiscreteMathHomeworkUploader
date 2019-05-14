import requests
import regex
import webbrowser
import LisanCookieGetter
from uploader import homeworkUploader
import logging
import os

#class_num = '001'
class easyHomework:

    def __init__(self,domain,url_head,class_num,username,password):
        '''
        :param domain: '.educoder.net'
        :param url_head: 'https://www.educoder.net'
        :param class_num: 001

        '''
        self.class_num = class_num
        self.url_head = url_head

        self.url_search = self.url_head + '/homework_common?course=1985&homework_type=1&utf8=%E2%9C%93&search={}'.format(
            class_num) #searching for all homework infos

        self.domain = domain

        self.url_login = self.url_head + '/login'

        self.username = username
        self.password = password

        logging.captureWarnings(True)

    def __requestWithCookie__(self):
        print('Searching for class number {}...\n'.format(self.class_num))

        self.cookieDict = LisanCookieGetter.getLoginCookie(self.domain, self.url_login, self.username, self.password)

        if self.cookieDict:

            r = requests.get(self.url_search,cookies= self.cookieDict,verify=False)
            self.__searchForHomework__(r,True)
        else:
            print('Fail to login, only showing results...')
            r = requests.get(self.url_search,verify=False)
            self.__searchForHomework__(r,False)


    def __searchForHomework__(self, request, isLoggedIn):

        if isLoggedIn:
            pattern = '<div class="fl task-form-100 clearfix" style="box-sizing: border-box; padding-left: 15px;">'
            pattern += '.+?<span class="fl mr10 mt3 color-grey3">.+?</span>'
            pattern += '.+?<a href=".+?" class="edu-class-inner-list fl color-grey-3">(.+?)</a>'
            pattern += '.+?'
            pattern += '<span class=\"edu-filter-btn edu-filter-btn-green ml10 fl mt6\">已开启补交<\/span>'
            pattern += '(.+?)'
            pattern += '<div class=\"cl\"><\/div>'
            # pattern += '(?:<span class="btn-top btn-cir-orange ml10 fl mt3">(未提交)</span>)'
            pattern += '.+?'
            pattern += '<a href="(.{20,40}?)" class="white-btn orange-btn fr mr20 mt8" target="_blank">(提交|补交|修改|查看)作品</a>'
            # (0):subject title
            # (1):未提交 or ''
            # (2):submission URL
            # (3):提交|补交|修改|查看
        else:
            pattern = '<div class="fl task-form-100 clearfix" style="box-sizing: border-box; padding-left: 15px;">'
            pattern += '.+?<span.+?</span>'
            pattern += '.+?<a href="(.+?)".+?>(.+?)</a>'
            #(0):submission URL
            #(1):subject title

        pattern = pattern.replace('"','\\\\"') # " -> \"
        pattern = pattern.replace('/','\\\\/') # / -> \/

        results = regex.findall(pattern,request.text)

        self.__showResult__(isLoggedIn,results)


    def __showResult__(self, isLoggedIn,results):

        title = []
        targetURL = []
        hasSub = []
        hintTxt = []

        if isLoggedIn:

            sn=1
            for result in results:

                title.append(result[0].strip())

                if len(result[1])<20:
                    #已提交，没有多余的内容
                    hasSub.append('√')
                else:
                    hasSub.append('')

                targetURL.append(result[2])

                hintTxt.append(result[3])
                if sn <= 5:
                    # at first only show first 5
                    print("{}.{}{} {}\n".format(sn,title[sn-1],hasSub[sn-1],hintTxt[sn-1]))
                sn+=1
        else:

            # title=[]
            # subURL=[]

            sn=1

            for result in results:

                title.append(result[1])

                targetURL.append(result[0])

                if sn<=5:
                    # at first only show first 5
                    print("{}.{}\n".format(sn,title[sn-1]))
                sn+=1

        print('... (input nothing to show more)\n')

        hmwkUploder = homeworkUploader(self.url_head,self.cookieDict)
        while 1:
            num = input("Which course do you wanna submit to? (Can only submit new projects) (0 to quit)\n")
            if num == '':
                #show more
                for sn in range(6,len(results)):
                    if isLoggedIn:
                        print("{}.{}{} {}\n".format(sn, title[sn - 1], hasSub[sn - 1], hintTxt[sn - 1]))
                    else:
                        print("{}.{}\n".format(sn, title[sn - 1]))
                continue
            else:
                num = eval(num)

            if num == 0:
                exit()
            elif 0 < num <= len(results):
                if hasSub[num-1]:
                    #has submitted before, cannot do submit code
                    print("You have submitted before, opening browser...\n")
                    webbrowser.open_new_tab(self.url_head + targetURL[num-1])
                else:

                    path = input("Type file path.(0 to go back)\n")
                    if path == "0":
                        continue
                    else:
                        if not os.path.exists(path):
                            print("Invalid path.\n")
                            continue
                        else:
                            homeworkNum = targetURL[num-1].split('=')[1]
                            url_submit = '/student_work?homework='+homeworkNum
                            print('\nUploading {} ...\n'.format(path))

                            if hmwkUploder.uploadFile(targetURL[num-1],url_submit,path) == 0:

                                # if succeed, refresh data
                                r = requests.get(self.url_search, cookies=self.cookieDict, verify=False)
                                return self.__searchForHomework__(r,True)


            else:
                print("Invalid number.\n")

    def easeHomework(self):
        self.__requestWithCookie__()
