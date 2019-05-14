import requests
import regex
import os # to get filename based on filepath
import logging



class homeworkUploader:
    def __init__(self,url_head,cookieDict):
        '''
        :param url_head: 'https://www.educoder.net'
        # :param url_query: '/student_work/new?homework='
        # :param url_submit: '/student_work?homework='
        '''
        self.url_head = url_head
        # self.url_query = url_head + url_query
        self.url_upload = url_head + '/uploads.js'
        # self.url_submit = url_head + url_submit
        self.cookieDict = cookieDict
        # self.filePath = filePath
        # self.fileName = os.path.basename(filePath)
        # self.descript = self.fileName #description in textbox
        logging.captureWarnings(True) # no warnings when verify= False

    def __firstQuery__(self,url_query,url_submit,filePath):
        '''

        :param url_query: '/student_work/new?homework=xxx'
        :param url_submit: '/student_work?homework=xxx'
        :return:
        '''
        self.url_query = self.url_head + url_query
        self.url_submit = self.url_head + url_submit
        #firstQuery loads the uploading page
        header_firstQuery = {
            'Host': 'www.educoder.net',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'If-None-Match': 'ab9e688b33859fc43fc68b6e63709d30',
        }

        r_first = requests.request('get', self.url_query, cookies=self.cookieDict, headers=header_firstQuery, verify=False)
        if r_first.status_code == 200:
            # success
            csrfToken = regex.findall('<meta content="([\=/\w]+?)" name="csrf-token"'
                                  , r_first.text)[0]

            return self.__uploadQuery__(csrfToken,filePath)
        else:
            print("error: First query failed\n")
            return -1

    def __uploadQuery__(self,csrfToken,filePath):
        fileName = os.path.basename(filePath)

        # call for upload.js
        with open(filePath,'rb') as fo:
            stream = fo.read()
        header_upload = {
            'Host': 'www.educoder.net',
            'Connection': 'keep-alive',
            'content-length': str(len(stream)),
            'Accept': 'application/js',
            'Origin': 'https://www.educoder.net',
            'X-CSRF-Token': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
            'Content-Type': 'application/octet-stream',
            'Referer': self.url_query,
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        r_up = requests.request('post', self.url_upload, headers=header_upload, data=stream,
                         params={'attachment_id': '1', 'filename': fileName}, cookies=self.cookieDict, verify=False)
        if r_up.status_code == 200:
            return self.__submitQuery__(r_up,csrfToken,filePath,fileName)
        else:
            print("error: upload faied\n")
            return -1

    def __submitQuery__(self,r_up,csrfToken,filePath,fileName):
        '''

        :param r_up: Response object of upload Query
        :type r_up: class:`Response <Response>` object\
        '''

        descript = fileName  # description in textbox

        attach_token = regex.findall("'attachments\[1\]\[token\].+?\\.val\('(.+?)'\)", r_up.text)[0]
        attach_id = regex.findall("'attachments\[1\]\[attachment_id\].+?\\.val\('(.+?)'\)", r_up.text)[0]

        submit_body = 'utf8=%E2%9C%93&'
        submit_body += 'authenticity_token={}&'.format(csrfToken)
        submit_body += 'student_work%5Bdescription%5D={}&'.format(descript)
        submit_body += 'attachments%5B1%5D%5Bfilename%5D={}&'.format(fileName)
        submit_body += 'attachments%5B1%5D%5Btoken%5D={}&'.format(attach_token)
        submit_body += 'attachments%5B1%5D%5Battachment_id%5D={}&'.format(attach_id)
        submit_body += 'attachments%5Bdummy%5D%5Bfile%5D={}'.format(fileName)

        header_submit={
            'Host': 'www.educoder.net',
            'Connection': 'keep-alive',
            'Content-Length': str(len(submit_body)),
            'Cache-Control': 'max-age=0',
            'Origin': 'https://www.educoder.net',
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Referer': self.url_query,
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        r_sub = requests.request('post', self.url_submit, data=submit_body, headers=header_submit, cookies=self.cookieDict, verify=False)
        if r_sub.status_code == 200:
            print("Successful!\n")
            return 0
        else:
            print("error: submit failed\n")
            return -1

    def uploadFile(self,url_query,url_submit,filePath):
        return self.__firstQuery__(url_query,url_submit,filePath)
