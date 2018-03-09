import schedule
import time
import os
import re
import datetime
import requests

port = '5000'
directory = '/home/cisco/houston-pos-v3/'
version = '3' # main vs main2 etc, for main.py use ''

search_strings_to_remove = ["127.0.0.1",
                            "foundation.css",
                            "app.css",
                            "foundation-icons.css",
                            "jquery.js",
                            "what-input.js",
                            "app.js",
                            "favicon.ico",
                            "dynatable.css",
                            "foundation.js",
                            "dynatable.js",
                            "WARNING:csvtotable",
                            "Virtual scroll is enabled",
                            "SettingWithCopyWarning",
                            "slice from a DataFrame",
                            "See the caveats in the documentation",
                            "Try using .loc",
                            "] = EMAIL",
                            "No parser was explicitly specified",
                            "The code that caused this warning",
                            "BeautifulSoup",
                            "to this:",
                            "markup_type=",
                            "editdistance.bycython.eval",
                            "TypeError: object of type"
                            ]

def check_pos_status():
    try:
        r = requests.head("http://0.0.0.0:"+port)
        #print(r.status_code)
        # prints the int of the status code. Find more at httpstatusrappers.com :)
    except requests.ConnectionError:
        #print("failed to connect")
        restart_pos_server()



def restart_pos_server():
    now = datetime.datetime.now()
    print(now.strftime("%Y-%h-%d---%H:%M %p"))
    os.system("kill $(ps aux | grep '[m]ain"+version+".py' | awk '{print $2}')") #alias to search ps aux and kill main.py
    time.sleep(1)
    os.system('nohup /usr/bin/python3 -u '+directory+'main'+version+'.py &') #alias to nohup start main.py
    print('restarting POS server')    
    
    """
    with open ('/home/cisco/houston-pos/nohup.out','r') as f:
        text=f.read()
        m = re.findall("\[[1-9].*\]",text)[-1] #last instance of string that looks like: '[20/Oct/2017 22:23:53]'
        f.close()
    lastWebRequest = datetime.datetime.strptime(m, '[%d/%b/%Y %H:%M:%S]') #turn timestamp into code readable python
    now = datetime.datetime.now()
    timeOfLastWebRequest = now - lastWebRequest
    if (timeOfLastWebRequest >= datetime.timedelta(minutes=10)):
        os.system("killpos") #alias to search ps aux and kill main.py
        time.sleep(3)
        os.system("startpos") #alias to nohup start main.py
        print('restarting POS server')
    """



def remove_lines_from_logs():
    f = open(directory+"pos_log.out","r")
    lines = f.readlines()
    f.close()
    f = open(directory+"pos_log.out","w")
    #print("starting loop")
    for line in lines:
        found_string = False
        for search_string in search_strings_to_remove:
            if search_string in line:
                found_string = True
        if not found_string:
            f.write(line)
    f.close()
    #print("finished loop")



def check_for_new_pos_files():
    os.system("/usr/bin/python3 "+directory+"POS_filter.py")



def temp_remove_lines_from_logs():
    line_before = ""
    f = open("/home/cisco/houston-pos/pos_log.out","r")
    lines = f.readlines()
    f.close()
    f = open("/home/cisco/houston-pos/pos_log.out","w")
    print("starting loop")
    for line in lines:
        if (line != line_before):
            f.write(line)
        line_before = line
    f.close()
    print("finished loop")


#schedule.every(1).minutes.do(check_pos_status)
schedule.every(1).minutes.do(check_pos_status)
#schedule.every(5).minutes.do(check_for_new_pos_files)
schedule.every(5).minutes.do(check_for_new_pos_files)
#schedule.every().hour.do(remove_lines_from_logs)
schedule.every().hour.do(remove_lines_from_logs)
#schedule.every().day.at("3:30").do(check_for_new_pos_files)
#schedule.every().monday.do(job)
#schedule.every().wednesday.at("13:15").do(job)

#run once on startup
#check_pos_status() 
check_pos_status()
#remove_lines_from_logs()
remove_lines_from_logs()
#temp_remove_lines_from_logs()


while True:
    schedule.run_pending()
    time.sleep(1)