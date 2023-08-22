from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge import service
import os
os.system("cls") #clear screen from previous sessions
import time

options = webdriver.EdgeOptions()
options.use_chromium = True
options.add_argument("start-maximized")
my_service=service.Service(r'msedgedriver.exe')
options.page_load_strategy = 'eager' #do not wait for images to load
options.add_experimental_option("detach", True)
options.add_argument('--no-sandbox')
#options.add_argument('--disable-dev-shm-usage') # uses disk instead of RAM, may be slow

from xml.dom.minidom import Text, Element #to escape < > & in text for it to be valid XML

s = 20 #time to wait for a single component on the page to appear, in seconds; increase it if you get server-side errors «try again later»

driver = webdriver.Edge(service=my_service, options=options)
action = ActionChains(driver)
wait = WebDriverWait(driver,s)

test_url = "https://any-test.ru/answers/test/upravlenie-personalom?page=1&pageSize=300" 

def scroll_to_bottom(): 
    reached_page_end= False
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    #expand the skills list:
    while not reached_page_end:
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if last_height == new_height:
            reached_page_end = True
        else:
            last_height = new_height

#to do: create a separate human-readable file with just questions and correct answers!
def reopen_files():
    with open('questions-answers-dummies.xml', 'w') as a:
        a.writelines("<?xml version=\"1.1\"?>\n<document>\n")
    with open('questions-and-answers.txt', 'w') as a:
        a.writelines("")
        
def append_to_xml(element_name, incoming_string):
    with open('questions-answers-dummies.xml', 'a') as a:
        #escape < > & etc:
        t = Text()        
        e = Element(element_name)
        t.data = incoming_string
        e.appendChild(t)
        
        a.writelines(e.toxml()+"\n")
        
def append_to_learning_file(incoming_string):
    with open('questions-and-answers.txt', 'a') as a:
        a.writelines(incoming_string)
     
def save_opened_page():
    reopen_files()
    h1 = driver.find_element(By.XPATH, '//h1').get_attribute('innerHTML').strip("\n ")
    append_to_xml("header", h1)
    append_to_xml("url", test_url)
    
    append_to_learning_file(h1+"\n\n")
    append_to_learning_file(test_url+"\n\n")
    
    scroll_to_bottom()
    
    results = driver.find_elements(By.XPATH, '//ntst-question-view')
    number_of_questions = len(results)
    append_to_xml("quantity", str(number_of_questions))
    append_to_learning_file("Количество вопросов: "+str(number_of_questions)+"\n\n")
    i=0
    for result in results:
        i+=1
        with open('questions-answers-dummies.xml', 'a') as a:
            a.writelines("<section id=\""+ str(i) +"\">\n")
            
        question_content = result.find_element(By.XPATH, './/h3[@class="mat-card-title"]').get_attribute('innerHTML').strip("\n ")
        append_to_xml("question", question_content)
        append_to_learning_file(question_content+"\n")
        answers = result.find_elements(By.XPATH, './/mat-list-item[@class="mat-list-item mat-focus-indicator d-grid answer correct ng-star-inserted"]//span')
        number_of_answers = len(answers)
        append_to_xml("number_of_answers", str(number_of_answers))
        if (number_of_answers > 0):
            for answer in answers:
                answer_to_save = answer.get_attribute('innerHTML').strip("\n \"")
                append_to_xml("answer", answer_to_save)
                append_to_learning_file(" ⟡ "+answer_to_save+"\n")
            
        dummies = result.find_elements(By.XPATH, './/mat-list-item[@class="mat-list-item mat-focus-indicator d-grid answer ng-star-inserted"]//span')
        number_of_dummies = len(dummies)
        append_to_xml("number_of_dummies", str(number_of_dummies))
        
        if (number_of_dummies > 0):
            for dummy in dummies:
                dummy_to_save = dummy.get_attribute('innerHTML').strip("\n \"")
                append_to_xml("dummy", dummy_to_save)
                
        
        with open('questions-answers-dummies.xml', 'a') as a:
            a.writelines("</section>\n")
            
        if(i != number_of_questions): append_to_learning_file("\n")
    
    with open('questions-answers-dummies.xml', 'a') as a:
        a.writelines("</document>")
        
def main():
    driver.get(test_url)
    time.sleep(10)
    scroll_to_bottom()
    time.sleep(1)
    
    save_opened_page()
    os.system("cls") #clear screen from unnecessary logs since the operation has completed successfully
    print("All questions, answers and dummies are saved! \n \nSincerely Yours, \nNAKIGOE.ORG\n")
    # Close the only tab, will also close the browser.
    driver.close()
    driver.quit()
main()
