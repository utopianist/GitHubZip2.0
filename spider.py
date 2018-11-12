from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import urllib.request
import requests
import re
import zipfile
from multiprocessing.pool import Pool

browser = webdriver.Chrome()

def paging(url):
    try:
        browser.get(url)
        paging = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#js-pjax-container > div > div.col-9.float-left.pl-2 > div.position-relative > div.paginate-container > div > a:nth-child(2)"))
        ) #定义翻页行为
        paging.click() #点击 下一页
        return browser.current_url #返回下一页 URL
    except:
        return False

def getHTML(url):
    r = requests.get(url)
    try:
        if r.status_code == 200:
            return (r.text)
    except:
        print('链接失败!')

def parsePage(html,urllist):
    pattern = re.compile('<h3>.*?<a href=".*?itemprop="name codeRepository" >(.*?)</a>.*?</h3>', re.S)
    items = re.findall(pattern, html)
    for item in items:
        zipurl = 'https://github.com/Germey/' + item[7:] + '/archive/master.zip'
        urllist.append(zipurl)

def downloadZip(urllist):
    for item in urllist:
        itemName = re.search('Germey/(.*?)/archive', item).group(1) #提取项目名称
        codesPath = 'codes' + os.path.sep + itemName + '.zip'
        if not os.path.exists(codesPath):
            try:
                print('正在下载' + itemName)
                urllib.request.urlretrieve(item,codesPath)
            except:
                continue

def unZip():
    fileList = os.listdir('codes')
    for fileName in fileList:
        filePath = 'codes' + os.path.sep + fileName
        if os.path.splitext(fileName)[1] == '.zip':
            try:
                print('正在尝试解压' + fileName)
                file_zip = zipfile.ZipFile(filePath, 'r')
                for file in file_zip.namelist():
                    file_zip.extract(file, 'codes') #选择保存路径 codes
                file_zip.close()
                os.remove(filePath)
            except:
                continue

def main(htmlurl):
    urllist = [] #装载ZIP文件的下载链接
    html = getHTML(htmlurl)
    parsePage(html, urllist)
    downloadZip(urllist)



if __name__ == '__main__':
    if not os.path.exists('codes'): #创建 codes 文件夹存放文件
        os.mkdir('codes')
    oldurl = 'https://github.com/Germey?tab=repositories' #初始URL
    htmllist = [] #装载翻页页面的URL列表
    newurl = paging(oldurl)
    htmllist.append(oldurl)
    while newurl != False:
        htmllist.append(newurl)
        newurl = paging(newurl)
    pool = Pool()
    pool.map(main,htmllist)
    pool.close()
    pool.join()
    unZip()