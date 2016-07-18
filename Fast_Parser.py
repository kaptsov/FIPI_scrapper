from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from bs4 import BeautifulSoup
import math
import time
from urllib.request import urlopen
import os
import codecs
import psycopg2
################################################################################

def parse_chapter(examName, subjectName, chapter_name, cxn, cur, chap_link ):    
    browser.get( chap_link) 
    soup = BeautifulSoup(browser.page_source,  "html5lib")
    question_count = int(''.join(x for x in soup.find("td", {"width":"100%","align":"center","height":"30"}).string if x.isdigit())) #получить цифры из названия раздела
    try:
        print('Parsing chapter: ' + chapter_name + ' - ' + str(question_count)) 
    except:
        print('Chapter name contain unreadble characters. Question count ' + str(question_count))
    
    if 20160 > question_count > 0:
        f = open(soup.find("td", {"width":"100%","align":"center","height":"30"}).string+'.html', 'w', encoding='utf8')
        
        f.write('<head><meta charset="utf-8"><script type="text/javascript" async src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-MML-AM_CHTML"> </script></head><body class="printbody" style="font-size:11pt">')
        image_src = 'src="' + browser.current_url[:browser.current_url.find("/xmodules")] + "/docs"
        mp3_src = "javascript:var wnd=window.open('http://85.142.162.119/os11/"
        page_count = int(question_count // 10 + math.ceil(question_count % 10 / 10))
        #if page_count > 1: page_count = 2 # debug
        #chapter_skip = 0
        CurrentTime = time.time()
        
        for j in range(page_count-1):   
            time.sleep(1)
            soup = BeautifulSoup(browser.page_source,  "html5lib")
            soup.prettify()

            
            for qw in soup.find_all("table", {"bgcolor":"gray", "cellspacing":"1", "width":"100%", "border":"0"}):
                for matht in qw.find_all("span", {"role":"presentation", "tabindex":"0"}):
                    tt = matht.find("math", {"xmlns":"http://www.w3.org/1998/Math/MathML"})
                    try:
                        matht.replaceWith(tt) 
                    except:
                        pass
                for smth in qw.find_all("script", {'type':'math/mml'}): 
                    smth.decompose()  
                    
                curr_ = str(qw).replace('src="../../docs', image_src).replace('gray', 'white').replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&').replace("javascript:var wnd=window.open('../../", mp3_src)                     
                
                try:
                    f.write(curr_)
                    problemText = curr_
                    
                    cur.execute(('SELECT id FROM exam_chapter WHERE "chapterName" = (%s) ORDER BY id DESC'), (chapter_name,))
                    chapter_id = cur.fetchone()
                    cur.execute('INSERT INTO exam_problem ("problemText", "chapter_id") VALUES (%s, %s)', (curr_, chapter_id,))
                    cxn.commit()
                except UnicodeError:
                    print('Unicode error on page number ' + str(j))
                    f.write('Unicode error on page number ' + str(j))
                
            print('complete: ' + str(round(100*j/page_count)) + '%')
            if (page_count > 1):
                browser.find_element_by_link_text("["+ str(j+2) +"]").click()
            
        
        print(str(round(time.time()-CurrentTime)//60) + ' min '+str(round(time.time()-CurrentTime)%60)+' seconds per chapter')    
        try:
            print(f.name) 
        except:
            pass 
        f.write('</body></html>')
        f.close()


################################################################################
print('Database connecting..')

cxn = psycopg2.connect(user='postgres', database = 'fipi_db', password ='111', host = 'kapets', port = '5432')
cxn.autocommit = True
cur = cxn.cursor()      

print('Browser loading..')
#browser = webdriver.Chrome('C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')
browser = webdriver.PhantomJS()
#browser=webdriver.Firefox()


print('Fipi connecting..')

levels = ['ege', 'oge']       
for level in levels:
    if (level == 'ege'):
        rusLevel = 'ЕГЭ'
        link_to = 'http://85.142.162.119/os11/xmodules/qprint/'
    else:
        rusLevel = 'ОГЭ'
        link_to = 'http://85.142.162.126/os/xmodules/qprint/'
    cur.execute('INSERT INTO exam_examtype("examName") VALUES (%s)', (rusLevel,))     
    try:
        os.chdir(rusLevel)
    except:
        os.mkdir(rusLevel)
        os.chdir(rusLevel)
        
    browser.get("http://www.fipi.ru/content/otkrytyy-bank-zadaniy-" + level)
    soup = BeautifulSoup(browser.page_source,  "html5lib")   
################################################################ - парсим линки предметов  
    #debug = soup.find_all("p", {"class":"rtecenter rteindent1"}) # debug
    for subjects in soup.find_all("p", {"class":"rtecenter rteindent1"}):
        sub_link = subjects.find("a", href=True)
        subject = subjects.find("a").getText()
        print(str(sub_link['href']) + '  ' + subject)    
        #sub_link = debug[14].find("a", href=True) # debug
        browser.get(str(sub_link['href']) )                         # переходим к предмету
        
        print('Subject open: ' + subject)
        soup = BeautifulSoup(browser.page_source,  "html5lib")
        
        folder_name = soup.find('a').string[soup.find('a').string.find("/")+1:].strip()
        
        try:
            os.chdir(folder_name)
        except:
            os.mkdir(folder_name)
            os.chdir(folder_name)
            
        cur.execute(('SELECT id FROM exam_examtype WHERE "examName" = (%s) ORDER BY id DESC'), (rusLevel,))   
        exam_id = cur.fetchone()
        cur.execute('INSERT INTO exam_subject ("subjectName", "exam_id") VALUES (%s, %s)', (folder_name, exam_id,))
        
        for link in soup.find_all('a', href=True)[1:]:
            cur.execute(('SELECT id FROM exam_subject WHERE "subjectName" = (%s) ORDER BY id DESC'), (folder_name,))
            subject_id = cur.fetchone()
            cur.execute('INSERT INTO exam_chapter ("chapterName", "subject_id") VALUES (%s, %s)', (link.string.strip(), subject_id,))    
            parse_chapter(rusLevel, subject, link.string.strip(), cxn, cur, link_to + str(link['href']) )
               
            
        os.chdir('..')
               
    os.chdir('..')
   
browser.quit()
cxn.close()
print('errything is cool! nice job')

