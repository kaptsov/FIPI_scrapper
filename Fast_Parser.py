from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from bs4 import BeautifulSoup
import math
import time
from urllib.request import urlopen
import os
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.common.exceptions import NoSuchFrameException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
################################################################################

def parse_chapter(chapter_name):    
    browser.find_element_by_link_text(chapter_name).click() 
    soup = BeautifulSoup(browser.page_source,  "html5lib")
    question_count = int(''.join(x for x in soup.find("td", {"width":"100%","align":"center","height":"30"}).string if x.isdigit())) #ÔÓÎÛ˜ËÚ¸ ˆËÙ˚ ËÁ Ì‡Á‚‡ÌËˇ ‡Á‰ÂÎ‡
    print('Parsing chapter: ' + chapter_name +' - ' + str(question_count)) 
    
    if question_count > 0:
        f = open(soup.find("td", {"width":"100%","align":"center","height":"30"}).string+'.html', 'w')
        f.write('<html xmlns:m="http://www.w3.org/1998/Math/MathML"><head><meta charset="windows-1251"></head><body class="printbody" style="font-size:11pt">')
        image_src = 'src="' + browser.current_url[:browser.current_url.find("/xmodules")] + "/docs"
        #page_count = int(question_count // 10 + math.ceil(question_count % 10 / 10))
        page_count = 2
        CurrentTime = time.time()
        
        for j in range(page_count-1):             
            soup = BeautifulSoup(browser.page_source,  "html5lib")
            for qw in soup.find_all("table", {"width":"100%", "border":"0", "cellspacing":"1", "bgcolor":"gray"}):
                curr_ = str(qw).replace('src="../../docs', image_src).replace('gray', 'white')
                f.write(curr_)
                
            print('complete: ' + str(round(100*j/page_count)) + '%')
            browser.find_element_by_link_text("["+ str(j+2) +"]").click()
            
        
        print(str(round(time.time()-CurrentTime)//60) + ' min '+str(round(time.time()-CurrentTime)%60)+' seconds per chapter')    
        print(f.name) 
        f.write('</body></html>')
        f.close()


################################################################################
        
print('Browser loading..')
#browser = webdriver.Chrome('C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')
#browser = webdriver.PhantomJS()
browser=webdriver.Firefox(firefox_profile='tor')


print('Fipi connecting..')
subject = u"Ã¿“≈Ã¿“» ¿"
level = 'oge'

subjects = [u'¡»ŒÀŒ√»ﬂ', u'»—“Œ–»ﬂ', u'Œ¡Ÿ≈—“¬Œ«Õ¿Õ»≈', u'√≈Œ√–¿‘»ﬂ', u'¿Õ√À»…— »… ﬂ«€ ', u'Õ≈Ã≈÷ »… ﬂ«€ ',u'‘–¿Õ÷”«— »… ﬂ«€ ',u'»—œ¿Õ— »… ﬂ«€ ',u'À»“≈–¿“”–¿',u'–”—— »… ﬂ«€ ', u'Ã¿“≈Ã¿“» ¿',u'‘»«» ¿',u'’»Ã»ﬂ',u'»Õ‘Œ–Ã¿“» ¿ Ë » “']

levels = ['ege', 'oge']       
for level in levels:
    try:
        os.chdir(level)
    except:
        os.mkdir(level)
        os.chdir(level)   
        
    for subject in subjects:
        browser.get("http://www.fipi.ru/content/otkrytyy-bank-zadaniy-" + level)     
        browser.find_element_by_link_text(subject).click()
        
        print('Subject open..')
        time.sleep(1)
        for handle in browser.window_handles:
            browser.switch_to.window(handle)
        time.sleep(1)
        
        
        Chapter_names = []
        soup = BeautifulSoup(browser.page_source,  "html5lib")
        
        folder_name = soup.find('a').string[soup.find('a').string.find("/")+1:].strip()
        
        try:
            os.chdir(folder_name)
        except:
            os.mkdir(folder_name)
            os.chdir(folder_name)
        
        for link in soup.find_all('a')[1:]:
            parse_chapter(link.string.strip())
               
       # for chapter_name in Chapter_names[1:]:
       #     parse_chapter(chapter_name.strip())
            
        os.chdir('..')
        
    browser.quit()    
    os.chdir('..')
    
    
browser.close()

