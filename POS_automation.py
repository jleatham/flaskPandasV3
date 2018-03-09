##########################################################################################################
##########################################################################################################
##########################################################################################################
#   POS search and filter application
#         Internal application, hosted on Github for version control.  Not applicable for general use.
#              
#
#   Full blown Flask application to serve web pages, data,  and interact with tool
#   Files:
#       scheduler.py
#           Tests Flask application every minute and restarts if needed, also does any timed functions
#           needed periodically
#       main.py
#           flask application that serves pages and acts as middle man between user and data functions
#       POS_automation.py
#           included parent file with functions and global vars needed to seach POS files and manipulate
#       POS_filter.py
#           python script that can call functions in POS_automation
#
#
#   v3 Candidate.  All Americas
#

##########################################################################################################
##########################################################################################################
##########################################################################################################

#test edit 2

import pandas as pd
import csv
import os
import glob
import shutil
import sys
import time
from datetime import datetime,timedelta
import jellyfish
import editdistance
import itertools
import json
from bs4 import BeautifulSoup as Soup
from collections import deque
from ciscosparkapi import CiscoSparkAPI
import codecs
from io import StringIO





#/usr/local/lib/python3.4/dist-packages/unicodecsv$ sudo nano py3.py
#I added :    
# import sys
# csv.field_size_limit(sys.maxsize)
####This was so that csvtotable would work with large csv files
#

SPARK_ACCESS_TOKEN=os.environ['SPARK_ACCESS_TOKEN']
POS_ADMIN_TOKEN=os.environ['POS_ADMIN_TOKEN']
timestr = time.strftime("%Y%m%d-%H%M%S")
now = datetime.now()
#globals needed for sitewide reporting of when reports are ran
report_runtime = 0
recent_date = ""
least_recent_date = ""
currentlyProcessingReports = "0"

#home_file_path="/Users/jleatham/Documents/Programming/Python/automation/POS/" #work laptop
home_file_path="/home/cisco/houston-pos-v3/"  #ubuntu server





old_pos_file_path = home_file_path+'oldPOS/'
filtered_filepath = home_file_path+'filteredPOS/'
am_list_json_filename = home_file_path+"am_list.json"
mbr_filepath = home_file_path+'MBR/'
real_time_search_file_path = filtered_filepath +'realtimesearch/'
all_data ="current_data.csv"
all_data_csv_filename = home_file_path + "filteredPOS/"+all_data

all_html_data = "all_filtered_POS_data.html"
all_data_html_filename = home_file_path + all_html_data


#monthly_data="monthly_filtered_POS_data_"+timestr+".csv"
#monthly_data_filename = home_file_path+"filteredPOS/"+monthly_data

temp_monthly_data="monthly_filtered_POS_data_temp.csv"
temp_monthly_data_filename = home_file_path+"filteredPOS/"+temp_monthly_data

non_error_pos_data="non_error_pos_data.csv"
non_error_pos_data_filename = home_file_path+"filteredPOS/"+non_error_pos_data

server_address = "http://123.changed.456:8080/filteredPOS/"

sparkapi = CiscoSparkAPI(access_token=SPARK_ACCESS_TOKEN)
roomId = "Y2lzY29zcGFyazovL3VzL1JPT00vNjhiNzc1MTAtNjAxNi0xMWU3LWFlN2MtNGJlNjIzOTJiMWI0" #Python test room
#roomId = "Y2lzY29zcGFyazovL3VzL1JPT00vOWZjODRmMjAtN2QyYi0xMWU3LThmZjQtMWJhODMwMmUyODg3" #Houston POS room



#Used to get the values of all the different teams in the database.  It returns the information in 2 formats.
#op_list : used when we need to iterate each segment pair based on name and proposed filename(no spaces)
#op_list1 : used as a list of all the filenames
def get_op_list():
    if not (os.stat(am_list_json_filename).st_size == 0):
        with open(am_list_json_filename) as data_file:
            data = json.load(data_file)  
    else:
        data = {}

    op_list = [] # used when we need to iterate each segment pair based on name and proposed filename(no spaces)
    op_list1 = [] # used as a list of all the filenames
    
    #iterate the json db
    for v in data.values():
        #these characters don't do well with filenames, so we replace them
        SL1 = v["SL1"]
        SL1 = SL1.replace(" ","_")
        SL1 = SL1.replace(".","")
        SL1 = SL1.replace("&","AND")
        SL2 = v["SL2"]
        SL2 = SL2.replace(" ","_")
        SL2 = SL2.replace(".","")
        SL2 = SL2.replace("&","AND")        
        SL3 = v["SL3"]
        SL3 = SL3.replace(" ","_")
        SL3 = SL3.replace(".","") 
        SL3 = SL3.replace("&","AND")       
        SL4 = v["SL4"]
        SL4 = SL4.replace(" ","_")
        SL4 = SL4.replace(".","") 
        SL4 = SL4.replace("&","AND")           
        op_list.append([v["SL1"],v["SL2"],v["SL3"],v["SL4"]]) #temporarily storing these
        op_list1.append([SL1,SL2,SL3,SL4])


    SL1_list = []
    SL2_list = []
    SL3_list = []
    SL4_list = []
    #taking all the list data that has the full path to each team, e.g., [[americas,commercial,csa,swso],[americas,enterprise,etc,etc]]
    #seperate the lists into type, so SL1_list = [americas,americas,americas], SL2_list = [commercial,commercial,enterprise,enterprise,etc]
    for op in op_list:
        SL1_list.append(op[0])
        SL2_list.append(op[1])
        SL3_list.append(op[2])
        SL4_list.append(op[3])


    #get rid of duplicates
    SL1_list = sorted(list(set(SL1_list)))
    SL2_list = sorted(list(set(SL2_list)))
    SL3_list = sorted(list(set(SL3_list)))
    SL4_list = sorted(list(set(SL4_list)))


    #for each new list, do the same thing and get rid of weird characters

    SL1_new= []
    for SL1 in SL1_list:
        SL1_changed = SL1
        SL1_changed = SL1_changed.replace(" ","_")
        SL1_changed = SL1_changed.replace(".","")
        SL1_changed = SL1_changed.replace("&","AND")
        SL1_new.append([SL1,SL1_changed])

    SL2_new= []
    for SL2 in SL2_list:
        SL2_changed = SL2
        SL2_changed = SL2_changed.replace(" ","_")
        SL2_changed = SL2_changed.replace(".","")
        SL2_changed = SL2_changed.replace("&","AND")
        SL2_new.append([SL2,SL2_changed])

    SL3_new= []
    for SL3 in SL3_list:
        SL3_changed = SL3
        SL3_changed = SL3_changed.replace(" ","_")
        SL3_changed = SL3_changed.replace(".","")
        SL3_changed = SL3_changed.replace("&","AND")
        SL3_new.append([SL3,SL3_changed])

    SL4_new= []
    for SL4 in SL4_list:
        SL4_changed = SL4
        SL4_changed = SL4_changed.replace(" ","_")
        SL4_changed = SL4_changed.replace(".","")
        SL4_changed = SL4_changed.replace("&","AND")
        SL4_new.append([SL4,SL4_changed])

    #create a new list: [[[americas,americas]],[[commercial,commercial],[enterprise,enterprise]],[[commercial south area,commerical_south_area],[CEA,etc]]]
    op_list = [SL1_new, SL2_new, SL3_new, SL4_new] 

    return op_list,op_list1

#not used
def to_html_v1(ALLCSV, ALLHTML):
    results = pd.read_csv(ALLCSV)
        
    with open(ALLHTML, 'w+') as f:
        results.to_html(f)

#take the CSV files in the old pos file path,
def prepare_test():
    global currentlyProcessingReports
    currentlyProcessingReports = "1"    
    for file in glob.glob(old_pos_file_path + '/*.[Cc][Ss][Vv]'):
        filename = os.path.basename(file)
        shutil.move(file, home_file_path+filename)
        print("moved: "+file)
    for file in glob.glob(home_file_path+ "filteredPOS" + '/*.*'):
        filename = os.path.basename(file)
        if not "aggressive" in filename:
            os.remove(file)
            print("removed:" + file)


def check_mbr_v1(POS):
    #for POS number, get various data fields of that row
    #get MBR data, check dates within a +/- 10 days period, that have similar product IDs, and customer fields
    #open results in new window, for now just print to screen
    # end result is to click on a row in browser, and run this function
    #if df.index[df["POS Transaction ID/Unique ID"] == POS]:
    start = time.time()
    results_pos = pd.DataFrame([])
    results_pos_list = []
    results_pos_pid_list = []
    results_mbr = pd.DataFrame([])

    #I could just pass the values I need here (Party ID and PID), directly into the search lists if I wanted.  If the
    #solution eventually is HTML, then jquery would just pass it in on click.
    print('{:^25}{:^25}{:^25}{:^25}{:^25}{:^25}{:^25}'.format('POS ID',"Posted Date",'Product ID','Value',"End Customer","Party ID","Salesrep Name"))

    #had to take encoding='cp1252' out because it was throwing an error:
    #  UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d in position 25: character maps to <undefined>
    df = pd.read_csv(non_error_pos_data_filename) 
    #print(len(df.index))
    df2 = pd.read_csv(all_data_csv_filename)
    #print(len(df2.index))
    df3 = pd.concat([df,df2])
    #df.merge(df2)
    #print(len(df3.index))
    #function 1 works, was slow
    #works but interrows is slow compared to df[df[]]
    #for index, row in df.iterrows():
        #if index == POS:
            #print(str(row["Posted Date"]) + "     "+str(row["Salesrep Name"]))
    
    #results = df[df.index == POS]
    '''
    #function 2 works, but wasn't any faster
    for index, row in results.iterrows():
        if (pd.notnull(row["Salesrep Name"])):
            if (index == POS):
                print(str(row["Salesrep Name"])+ "   POS# " +str(index) +"   Posted Date: " +str(row["Posted Date"]) )
                print(str(row))
                results_pos = results_pos.append(row)
    '''
    #function 3 was more elegant, but also not faster...
    for row in df3[df3["POS ID"] == POS].itertuples():
        #print(str(row))
        print("#########################  FROM POS REPORT  ###############################")
        print('{:^25}{:^25}{:^25}{:^25}{:^25}{:^25}{:^25}'.format(str(row[1]),str(row[2]),str(row[6]),str(row[7]),str(row[5]),str(row[10]),str(row[4])))
        results_pos_list.append(row[10]) 
        results_pos_pid_list.append(str(row[6]))          
              
    mbr_file = max(glob.iglob(mbr_filepath + '*.[Cc][Ss][Vv]'), key=os.path.getctime)
    df_mbr = pd.read_csv(mbr_file, usecols=["Sales Order Number","End Customer Company Name","Transaction Date","Total Bookings","Sales Agent Name","Product ID","Branch Party ID"]) #.set_index("Branch Party ID")              
    
    #print("test\n\ntest")
    #print(str(results_pos_list))
    #print(str(results_pos_pid_list))
    #print("end test\n")

    #produces double results for mbr if multiple POS statements found
    '''
    for index, row in results_pos.iterrows():
        if (pd.notnull(row["End Customer CR Party ID"])):
            results_temp = df_mbr[(df_mbr.index == row["End Customer CR Party ID"]) & (df_mbr["Product ID"].str.contains(row["Product ID"]))]
            results_mbr = results_mbr.append(results_temp)
    '''
    '''
    for row in results_pos.itertuples():
        for row_mbr in df_mbr.itertuples():
            if (row["End Customer CR Party ID"] == row_mbr["Branch Party ID"]):
                results_mbr.append(row_mbr)  
    '''
    results_mbr = df_mbr[(df_mbr["Branch Party ID"].isin(results_pos_list)) & (df_mbr["Product ID"].isin(results_pos_pid_list))]

    end = time.time()
    print("\n#########################  FROM MBR  ###############################")
    print('{:^25}{:^25}{:^25}{:^25}{:^25}{:^25}{:^25}'.format('SO#','Posted Date',"Product ID",'Total Bookings',"End Customer","Party ID","Salesrep Name"))
    for row in results_mbr.itertuples():
        print('{:^25}{:^25}{:^25}{:^25}{:^25}{:^25}{:^25}'.format(str(row[1]),str(row[3]),str(row[6]),str(row[4]),str(row[2]),str(row[7]),str(row[5])))
    print ("Time to process: "+ str(end - start))

def to_csv_from_json_v2(FILES,ALLCSV,NONERRORCSV):
    #750% faster than v1
    global currentlyProcessingReports
    currentlyProcessingReports = "1"
    start = time.time()
    #open json file and load to memory, create empty file if can't find json
    if not (os.stat(am_list_json_filename).st_size == 0):
        with open(am_list_json_filename) as data_file:
            data = json.load(data_file)  
    else:
        data = {}

    #add all new files into a single dataframe, then run through each json item and search individually.  add
    #all results to single large dataframe and write to csv all at once
    frames = [] #used to concat all files
    for file in FILES:
        filename = os.path.basename(file)
        if not os.path.isfile(old_pos_file_path+filename): #if there is not a duplicate in olPOS already
            try:
                with codecs.open(file,'r', 'windows-1252', errors="replace") as f:
                    text = f.read()
                FILEDATA = StringIO(text)
                df = pd.DataFrame() # create empty dataframe                       
                df = pd.read_csv(FILEDATA,low_memory=False, usecols=["POS Transaction ID/Unique ID","POS Trx SCA Date",	'POS Split Adjusted Value USD', 'Product ID','POS SCA Mode','Ship-To Source Customer Name','Sold-To Source Customer Name',"End Customer Source Customer Name","End Customer CR Party ID","Salesrep Email","Salesrep Name","Salesrep #"])
                shutil.move(file, old_pos_file_path+filename)
                print ("processed: "+filename)
                frames.append(df)
            except Exception as e:
                print ("file not readable in pandas: "+ file)
                print (e)
                print("Trying to fix")
                #check if csv headers are not 1st line
                #will rewrite the file and the program will try again next time it checks for new files
                try:
                    df2 = pd.read_csv(FILEDATA)
                    i = 0
                    if "POS Transaction ID/Unique ID" not in df.columns:
                        while i < 4:
                            df2 = pd.read_csv(FILEDATA,skiprows=[i])
                            if "POS Transaction ID/Unique ID" not in df2.columns:
                                print("Couldn't find POS data in row "+str(i))
                                i += 1
                            else:
                                print("Found POS data in row "+str(i))
                                i = 5
                                with open(file, 'w') as f:
                                    df2.to_csv(f, index=False)
                                    print("re-wrote file: "+filename)
                    else:
                        print("headers are correct, not sure the issue")
                    #end check   
                except Exception as e:
                    print (e)
                    print ("could not fix file: "+ file)
                    msg = "could not fix file: "+ file
                    send_msg_to_spark(roomId,msg)               

            #add newly created dataframe to frames list
            
            # dynamically populated and then put the df data into each
        else: #file is a duplicate
            print("file already exists in " +old_pos_file_path+": "+filename+"  ...removing")
            os.remove(file)

    #concate all df's in frames
    for frame in frames:
        print("length of frame: "+str(len(frame.index)))
    master_df = pd.concat(frames, ignore_index=True)
    #df = master_df #is this necessary, or can I call it df, even though all the concating files are df as well?
    master_df.reset_index()
    print("length of master frame: "+str(len(master_df.index)))
    print("Added all files to master data frame for processing")
    #print(df.head())
    #print(df.tail())
    
    #narrow down the search fields to only stuff I care about, saves a lot of time in processing
    json_accounts = []
    json_email = []
    for v in data.values():
        for account in v["accounts"]:
            json_accounts.append(str(account)) #problem with some accounts not being strings, but which?  and how?
        json_email.append(str(v["email"])) 
    print("done with getting json")
    df = master_df[(master_df['End Customer Source Customer Name'].astype(str).isin(json_accounts)) | (master_df['Ship-To Source Customer Name'].astype(str).isin(json_accounts)) | (master_df['Sold-To Source Customer Name'].astype(str).isin(json_accounts)) | (master_df["Salesrep Email"].astype(str).isin(json_email)) | (master_df["Salesrep #"].astype(str).isin(json_email)) ]
    print("done with narrowing search results")
    print("filtered df length: "+str(len(df.index)))
    db_length = len(data)
    print("items in db = "+str(db_length))
    time.sleep(3)
    frames = [] #re-initialize frames so we can concat below df's
    frames_non_error = []
    y = 0
    #note, before narrowing down, would have a few issues with below, might still need some TLC later on, e.g., ValueError: cannot set a frame with no defined index and a scalar
    for v in data.values():
        y += 1
        #can reuse this code elsewhere if : def build_df(v)
        #build_df(v)

        #can probably speed things up if I remove items from the df as I find them, maybe speed up, not sure.
        EMAIL = str(v["email"])
        if EMAIL.isnumeric():
            #repNumber = int(float(EMAIL))
            repNumber = EMAIL
            #print(str(repNumber))
        else:
            repNumber = '10555' #some random number
        REGION = str(v["SL5"])
        OPERATION = str(v["SL4"])
        AREA = str(v["SL3"])
        SL2 = str(v["SL2"])
        SL1 = str(v["SL1"])
        ACCOUNTS = [] #probably not needed but I added it when there were a few errors in the database
        for account in v["accounts"]:
            ACCOUNTS.append(str(account))
        FALSE = v["false_positives"]
        
        results1 = df[ (df['End Customer Source Customer Name'].astype(str).isin(ACCOUNTS)) | (df['Ship-To Source Customer Name'].astype(str).isin(ACCOUNTS)) | (df['Sold-To Source Customer Name'].astype(str).isin(ACCOUNTS)) ]
        results = results1[ (~results1["Salesrep Email"].str.contains(EMAIL)) & (~results1["Salesrep #"].astype(str).str.contains(repNumber)) ]
        #add false positives later on results3 = results2[~results2['End Customer Source Customer Name'].astype(str).isin(FALSE)]]
        # old search:   results = df[(df['End Customer Source Customer Name'].astype(str).isin(ACCOUNTS) | df['Ship-To Source Customer Name'].astype(str).isin(ACCOUNTS) | df['Sold-To Source Customer Name'].astype(str).isin(ACCOUNTS)) & (~df["Salesrep Email"].str.contains(EMAIL)) & (~df["Salesrep #"].astype(int) == repNumber ) & (~df['End Customer Source Customer Name'].astype(str).isin(FALSE))] 
        # the old search above was difficult to get the logic right, so I broke it up
        #results.index.names = ['POS ID']
        results.rename(columns = {'POS Transaction ID/Unique ID':'POS ID','POS Trx SCA Date':'Date','POS Split Adjusted Value USD':'$$$','Ship-To Source Customer Name':'Ship-To','Sold-To Source Customer Name':'Sold-To','End Customer Source Customer Name':'End Customer','End Customer CR Party ID':'Party ID','POS SCA Mode':'Mode','Salesrep Name':'AM Credited'}, inplace=True)
        #results.loc[:,'Sort Here'] = EMAIL
        results["Sort Here"] = EMAIL
        #results.loc[:,'Region Sort'] = REGION
        results["Region"] = REGION
        results["Operation"] = OPERATION
        results["Area"] = AREA
        results["SL2"] = SL2
        results["SL1"] = SL1
        results = results[['POS ID','Date','Sort Here','AM Credited','End Customer','Product ID','$$$','Ship-To','Sold-To','Party ID','Mode','Region','Operation','Area','SL2','SL1']]
        results['Date'] = pd.to_datetime(results['Date'], errors='coerce')


        non_error_results = df[(df["Salesrep Email"].str.contains(EMAIL)) | (df["Salesrep #"].astype(str).str.contains(repNumber)) ]#& len(df.index)<20
        #non_error_results.index.names = ['POS ID']
        non_error_results.rename(columns = {'POS Transaction ID/Unique ID':'POS ID','POS Trx SCA Date':'Date','POS Split Adjusted Value USD':'$$$','Ship-To Source Customer Name':'Ship-To','Sold-To Source Customer Name':'Sold-To','End Customer Source Customer Name':'End Customer','End Customer CR Party ID':'Party ID', 'POS SCA Mode':'Mode','Salesrep Name':'AM Credited'}, inplace=True)                    
        non_error_results["Sort Here"] = EMAIL
        #non_error_results.loc[:,'Sort Here'] = EMAIL
        non_error_results["Region"] = REGION
        non_error_results["Operation"] = OPERATION
        non_error_results["Area"] = AREA
        non_error_results["SL2"] = SL2
        non_error_results["SL1"] = SL1        
        #non_error_results.loc[:,'Region Sort'] = REGION
        non_error_results = non_error_results[['POS ID','Date','Sort Here','AM Credited','End Customer','Product ID','$$$','Ship-To','Sold-To','Party ID','Mode','Region','Operation','Area','SL2','SL1']]
        non_error_results['Date'] = pd.to_datetime(non_error_results['Date'], errors='coerce')

        frames.append(results) #add each results df to list for cancat
        frames_non_error.append(non_error_results)
        print(str(y)+" finished searching for: "+EMAIL)

    print("finished all searches, adding to CSV")
    #add the respective dfs together using concat
    master_results = pd.concat(frames, ignore_index=True)
    master_results.reset_index()
    master_non_error_results = pd.concat(frames_non_error, ignore_index=True)
    master_non_error_results.reset_index()

    #change the index before writing to CSV
    #master_results.set_index("POS ID")
    #master_non_error_results.set_index("POS ID")
    print("size of results = "+str(len(master_results.index)))
    print("size of non error results = "+str(len(master_non_error_results.index)))

    #write respective dfs to CSV
    if os.path.isfile(ALLCSV):
        with open(ALLCSV, 'a') as f:
            master_results.to_csv(f, header=False, index=False)
    else:
        master_results.to_csv(ALLCSV, index=False)

    if os.path.isfile(NONERRORCSV):
        with open(NONERRORCSV, 'a') as f:
            master_non_error_results.to_csv(f, header=False, index=False)
    else:
        master_non_error_results.to_csv(NONERRORCSV, index=False)  

    #signal that function has ended and give processing time
    end = time.time()
    currentlyProcessingReports = "0"
    print ("Time to process: "+ str(end - start))
          




def to_csv_from_json_v1(FILES,ALLCSV, NONERRORCSV):
    global currentlyProcessingReports
    currentlyProcessingReports = "1"
    start = time.time()
    if not (os.stat(am_list_json_filename).st_size == 0):
        with open(am_list_json_filename) as data_file:
            data = json.load(data_file)  
    else:
        data = {}

    for file in FILES:
        filename = os.path.basename(file)
        if not os.path.isfile(old_pos_file_path+filename): #if there is not a duplicate in olPOS already
            try:
                # encoding='cp1252'  , fixes the problem of some CSVs not loading due to weird characters
                df = pd.read_csv(file, encoding='cp1252',low_memory=False, usecols=["POS Transaction ID/Unique ID","Posted Date",	'POS Split Adjusted Value USD', 'Product ID','POS SCA Mode','Ship-To Source Customer Name','Sold-To Source Customer Name',"End Customer Source Customer Name","End Customer CR Party ID","Salesrep Email","Salesrep Name"]).set_index("POS Transaction ID/Unique ID")
                #df["POS Transaction ID/Unique ID"] = pd.to_numeric(df["POS Transaction ID/Unique ID"], errors='coerce')
                #df = df.dropna(subset=["POS Transaction ID/Unique ID"]).set_index("POS Transaction ID/Unique ID")
                for v in data.values():
                    EMAIL = v["email"]
                    REGION = v["SL5"]
                    ACCOUNTS = v["accounts"]
                    FALSE = v["false_positives"]
                    results = df[(df['End Customer Source Customer Name'].isin(ACCOUNTS) | df['Ship-To Source Customer Name'].isin(ACCOUNTS) | df['Sold-To Source Customer Name'].isin(ACCOUNTS)) & ~df["Salesrep Email"].str.contains(EMAIL) & ~df['End Customer Source Customer Name'].isin(FALSE)] 
                    results.index.names = ['POS ID']
                    results.rename(columns = {'Posted Date':'Date','POS Split Adjusted Value USD':'$$$','Ship-To Source Customer Name':'Ship-To','Sold-To Source Customer Name':'Sold-To','End Customer Source Customer Name':'End Customer','End Customer CR Party ID':'Party ID','POS SCA Mode':'Mode','Salesrep Name':'AM Credited'}, inplace=True)
                    results["Sort Here"] = EMAIL
                    results["Region Sort"] = REGION
                    results = results[['Date','Sort Here','AM Credited','End Customer','Product ID','$$$','Ship-To','Sold-To','Party ID','Mode','Region Sort']]
                    results['Date'] = pd.to_datetime(results['Date'], errors='coerce')
                    if os.path.isfile(ALLCSV):
                        with open(ALLCSV, 'a') as f:
                            results.to_csv(f, header=False)
                    else:
                        results.to_csv(ALLCSV)
                    

                    non_error_results = df[df["Salesrep Email"].str.contains(EMAIL) ]#& len(df.index)<20
                    non_error_results.index.names = ['POS ID']
                    non_error_results.rename(columns = {'Posted Date':'Date','POS Split Adjusted Value USD':'$$$','Ship-To Source Customer Name':'Ship-To','Sold-To Source Customer Name':'Sold-To','End Customer Source Customer Name':'End Customer','End Customer CR Party ID':'Party ID', 'POS SCA Mode':'Mode','Salesrep Name':'AM Credited'}, inplace=True)                    
                    non_error_results["Sort Here"] = EMAIL
                    non_error_results["Region Sort"] = REGION
                    non_error_results = non_error_results[['Date','Sort Here','AM Credited','End Customer','Product ID','$$$','Ship-To','Sold-To','Party ID','Mode','Region Sort']]
                    non_error_results['Date'] = pd.to_datetime(non_error_results['Date'], errors='coerce')
                    if os.path.isfile(NONERRORCSV):
                        with open(NONERRORCSV, 'a') as f:
                            non_error_results.to_csv(f, header=False)
                    else:
                        non_error_results.to_csv(NONERRORCSV)                
                shutil.move(file, old_pos_file_path+filename)
                print ("processed: "+filename)       
            except Exception as e:
                print ("file not readable in pandas: "+ file)
                print (e)
                print("Trying to fix")
                #how to add a try block on this to avoid crashes? nested try/except
                try:
                    df = pd.read_csv(file)
                    i = 0
                    if "POS Transaction ID/Unique ID" not in df.columns:
                        while i < 4:
                            df2 = pd.read_csv(file,skiprows=[i])
                            if "POS Transaction ID/Unique ID" not in df2.columns:
                                print("Couldn't find POS data in row "+str(i))
                                i += 1
                            else:
                                print("Found POS data in row "+str(i))
                                i = 5
                                with open(file, 'w') as f:
                                    df2.to_csv(f, index=False)
                                    print("re-wrote file: "+filename)
                    else:
                        print("headers are correct, not sure the issue")                    
                except Exception as e:
                    print(e)
                    print("Can't even load file into pandas: "+ file)
                    print("trying to force encoding")
                    try:
                        with codecs.open(file,'r', 'windows-1252', errors="replace") as f:
                            text = f.read()
                        TESTDATA = StringIO(text)
                        df = pd.read_csv(TESTDATA)
                        results = df[df["POS Transaction ID/Unique ID"].str.isnumeric()]
                        with open(file, 'w') as f:
                            results.to_csv(f)
                            print("re-wrote file: "+filename)                        
                    except Exception as e:
                        print(e)
                        print("Can't force encoding")

                #print (sys.exc_info()[0])
                pass
        else: #file is a duplicate
            print("file already exists in " +old_pos_file_path+": "+filename+"  ...removing")
            os.remove(file)
    end = time.time()
    currentlyProcessingReports = "0"
    print ("Time to process: "+ str(end - start))

def update_single_am_account_list(EMAIL,ACCOUNT,ACTION):
    ##Pseudo code
    #get single account name or list of account names (sanitize data? one at a time? no quotes? etc)
    #get any false positive names to add or remove
    #add or delete from JSON
    #reload JSON file to global am_list_json using json mem function
    global currentlyProcessingReports
    currentlyProcessingReports = "1"
    if not (os.stat(am_list_json_filename).st_size == 0):
        with open(am_list_json_filename) as data_file:
            data = json.load(data_file)  
    else:
        data = {}
    if ACTION == 'add':
        for v in data.values():
            if v["email"] == EMAIL:
                v["accounts"].insert(0,ACCOUNT)
                print("Added account: "+ACCOUNT+" for "+EMAIL)
    if ACTION == 'remove':
        for v in data.values():
            if v["email"] == EMAIL:
                if ACCOUNT in v["accounts"]:
                    v["accounts"].pop(v["accounts"].index(ACCOUNT))
                    print("Removed account: "+ACCOUNT+" for "+EMAIL)
                else:
                    print("couldn't find account: "+ ACCOUNT)
    
    #write results to json file
    with open(am_list_json_filename, "w") as data_file:
        json.dump(data,data_file, indent=4)     
    
    currentlyProcessingReports = "0"
    #set global json var for memory
    return data


def update_single_am_results(EMAIL,ALLCSV):
    ##Pseudo code
    #move current_data.csv into data frame
    #remove all instances of data based on email address
    #rewrite CSV file
    #move all POS files into main directory and iterate through them, only for AMs accounts
    #append df to CSV file
    #update monthly files for everyone with create_monthly function, easier and fast enough to worry about modifying each
    start = time.time()
    global currentlyProcessingReports
    currentlyProcessingReports = "1"

    if not (os.stat(am_list_json_filename).st_size == 0):
        with open(am_list_json_filename) as data_file:
            data = json.load(data_file)  
    else:
        data = {}
    emailExists = False
    for v in data.values():
        if v["email"] == EMAIL:
            emailExists = True
            if EMAIL.isnumeric():
                #repNumber = int(float(EMAIL))
                repNumber = EMAIL
                #print(str(repNumber))
            else:
                repNumber = '10555' #some random number
            REGION = str(v["SL5"])
            OPERATION = str(v["SL4"])
            AREA = str(v["SL3"])
            SL2 = str(v["SL2"])
            SL1 = str(v["SL1"])
            ACCOUNTS = [] #probably not needed but I added it when there were a few errors in the database
            for account in v["accounts"]:
                ACCOUNTS.append(str(account))
            FALSE = v["false_positives"]

    if not emailExists:
        currentlyProcessingReports = "0"
        return "Could not find this CCO ID"
    

    df = pd.read_csv(ALLCSV)
    results = df[df['Sort Here'] != EMAIL]

    with open(ALLCSV, 'w') as f: #all_data_csv_filename
        results.to_csv(f,index=False)







    frames = []
    print("adding CSVs to master df")

    
    #test_file_list = [old_pos_file_path+"US_POS_Report 01_08 to 24_08.csv",old_pos_file_path+"US POS Current Detailed Bookings Report_V1.0 _ 117952683_757818984988416547.csv"] #delete when done testing
    #for file in test_file_list:
    for file in glob.glob(old_pos_file_path + '/*.[Cc][Ss][Vv]'): #uncomment when done testing
        try:
            with codecs.open(file,'r', 'windows-1252', errors="replace") as f:
                text = f.read()
            FILEDATA = StringIO(text)
            df = pd.DataFrame() # create empty dataframe                       
            df = pd.read_csv(FILEDATA,low_memory=False, usecols=["POS Transaction ID/Unique ID","POS Trx SCA Date",	'POS Split Adjusted Value USD', 'Product ID','POS SCA Mode','Ship-To Source Customer Name','Sold-To Source Customer Name',"End Customer Source Customer Name","End Customer CR Party ID","Salesrep Email","Salesrep Name","Salesrep #"])
        except Exception as e:
            print ("file not readable in pandas: "+ file)
            print (e)


        frames.append(df)
    #concate all df's in frames
    for frame in frames:
        print("length of frame: "+str(len(frame.index)))
    master_df = pd.concat(frames, ignore_index=True)
    #df = master_df #is this necessary, or can I call it df, even though all the concating files are df as well?
    master_df.reset_index()
    print("length of master frame: "+str(len(master_df.index)))
    print("Added all files to master data frame for processing")

    df = master_df
    frames = [] #re-initialize frames so we can concat below df's
    print("building results df")


    results1 = df[ (df['End Customer Source Customer Name'].astype(str).isin(ACCOUNTS)) | (df['Ship-To Source Customer Name'].astype(str).isin(ACCOUNTS)) | (df['Sold-To Source Customer Name'].astype(str).isin(ACCOUNTS)) ]
    results = results1[ (~results1["Salesrep Email"].str.contains(EMAIL)) & (~results1["Salesrep #"].astype(str).str.contains(repNumber)) ]
    #add false positives later on results3 = results2[~results2['End Customer Source Customer Name'].astype(str).isin(FALSE)]]
    # old search:   results = df[(df['End Customer Source Customer Name'].astype(str).isin(ACCOUNTS) | df['Ship-To Source Customer Name'].astype(str).isin(ACCOUNTS) | df['Sold-To Source Customer Name'].astype(str).isin(ACCOUNTS)) & (~df["Salesrep Email"].str.contains(EMAIL)) & (~df["Salesrep #"].astype(int) == repNumber ) & (~df['End Customer Source Customer Name'].astype(str).isin(FALSE))] 
    # the old search above was difficult to get the logic right, so I broke it up
    #results.index.names = ['POS ID']
    results.rename(columns = {'POS Transaction ID/Unique ID':'POS ID','POS Trx SCA Date':'Date','POS Split Adjusted Value USD':'$$$','Ship-To Source Customer Name':'Ship-To','Sold-To Source Customer Name':'Sold-To','End Customer Source Customer Name':'End Customer','End Customer CR Party ID':'Party ID','POS SCA Mode':'Mode','Salesrep Name':'AM Credited'}, inplace=True)
    #results.loc[:,'Sort Here'] = EMAIL
    results["Sort Here"] = EMAIL
    #results.loc[:,'Region Sort'] = REGION
    results["Region"] = REGION
    results["Operation"] = OPERATION
    results["Area"] = AREA
    results["SL2"] = SL2
    results["SL1"] = SL1
    results = results[['POS ID','Date','Sort Here','AM Credited','End Customer','Product ID','$$$','Ship-To','Sold-To','Party ID','Mode','Region','Operation','Area','SL2','SL1']]
    results['Date'] = pd.to_datetime(results['Date'], errors='coerce')

    if os.path.isfile(ALLCSV):
        with open(ALLCSV, 'a') as f:
            results.to_csv(f, header=False, index=False)
    else:
        results.to_csv(ALLCSV,index=False)











    '''

    for file in glob.glob(old_pos_file_path + '/*.[Cc][Ss][Vv]'):
        filename = os.path.basename(file)

        try:
            # encoding='cp1252'  , fixes the problem of some CSVs not loading due to weird characters
            df = pd.read_csv(file, encoding='cp1252',low_memory=False, usecols=["POS Transaction ID/Unique ID","Posted Date",	'POS Split Adjusted Value USD', 'Product ID','POS SCA Mode','Ship-To Source Customer Name','Sold-To Source Customer Name',"End Customer Source Customer Name","End Customer CR Party ID","Salesrep Email","Salesrep Name"]).set_index("POS Transaction ID/Unique ID")
            #df["POS Transaction ID/Unique ID"] = pd.to_numeric(df["POS Transaction ID/Unique ID"], errors='coerce')
            #df = df.dropna(subset=["POS Transaction ID/Unique ID"]).set_index("POS Transaction ID/Unique ID")
            for v in data.values():
                if v["email"] == EMAIL:
                    ACCOUNTS = v["accounts"]
                    REGION = v["SL5"]
                    FALSE = v["false_positives"]
                    results = df[(df['End Customer Source Customer Name'].isin(ACCOUNTS) | df['Ship-To Source Customer Name'].isin(ACCOUNTS) | df['Sold-To Source Customer Name'].isin(ACCOUNTS)) & ~df["Salesrep Email"].str.contains(EMAIL) & ~df['End Customer Source Customer Name'].isin(FALSE)] 
                    results.index.names = ['POS ID']
                    results.rename(columns = {'Posted Date':'Date','POS Split Adjusted Value USD':'$$$','Ship-To Source Customer Name':'Ship-To','Sold-To Source Customer Name':'Sold-To','End Customer Source Customer Name':'End Customer','End Customer CR Party ID':'Party ID','POS SCA Mode':'Mode','Salesrep Name':'AM Credited'}, inplace=True)
                    results["Sort Here"] = EMAIL
                    results["Region Sort"] = REGION
                    results = results[['Date','Sort Here','AM Credited','End Customer','Product ID','$$$','Ship-To','Sold-To','Party ID','Mode','Region Sort']]
                    results['Date'] = pd.to_datetime(results['Date'], errors='coerce')
                    if os.path.isfile(ALLCSV):
                        with open(ALLCSV, 'a') as f:
                            results.to_csv(f, header=False)
                    else:
                        results.to_csv(ALLCSV)
              
            print ("processed: "+filename)       
        except Exception as e:
            print ("file not readable in pandas: "+ file)
            print (e)
            #print (sys.exc_info()[0])
            pass
    '''    
    #create_monthly_csv(ALLCSV)
    create_area_reports(all_data_csv_filename,non_error_pos_data_filename,op_list) #should either bring these vriables from function
    # or change the area_report function to not have them passed in, just assigned as global
    create_html_tables()

    end = time.time()
    print ("Time to process: "+ str(end - start))

    currentlyProcessingReports = "0"
    return ("completed in "+ str(end - start)+" seconds")
    

def create_aggressive_search_csv_for_am(EMAIL,DISTANCE):
    ##Pseudo Code
    #create file for an AMs levenshtein search, trying to get results to html page seem like too much work
    #run levenshtein function to get an aggressive search for an AM
    #post CSV to file list for them to go through at their leisure
    global currentlyProcessingReports,op_list
    currentlyProcessingReports = "1"

    
    start = time.time()
    
    if not (os.stat(am_list_json_filename).st_size == 0):
        with open(am_list_json_filename) as data_file:
            data = json.load(data_file)  
    else:
        data = {}


    #new algorithm
    #Pseudo code
    #get every account in JSON and put in account_list
    #get every account of every AM from all POS CSVs and put in pos_list
    #eliminate duplicates from pos_list
    #make a matrix to pair up every POS customer name with every AM account
    #run editdistance on every pair and put in final_pos_list if within a distance of 3
    #loop through all CSV files again, and if end customer name is listed in final_pos_list, add to levenshtein csv
    account_list = []

    for v in data.values():
        if v["email"] == EMAIL:
            account_list = v["accounts"]
            operation = v["SL4"]
            for SL in op_list[3]:
                if SL[0] == operation:
                    operation = SL[1]
            print("Creating aggressive search for: "+EMAIL)
            aggressive_search_file = filtered_filepath+EMAIL+"_"+operation+"_aggressive_search.csv"
            if os.path.isfile(aggressive_search_file):
                os.remove(aggressive_search_file)
                print("Removed old aggressive search file")            

    if not account_list:
        currentlyProcessingReports = "0"
        return "Could not find this CCO ID"

    #for row in data['am3']['accounts']:
        #account_list.append(row)

    account_array=[]
    pos_list=[]
    final_pos_list = []

    #[editdistance.eval(s1,s2) < 3  for s1,s2 in account_array ]

    for file in glob.glob(old_pos_file_path + '/*.[Cc][Ss][Vv]'):
        try:
            df = pd.read_csv(file,encoding='cp1252', usecols=["End Customer Source Customer Name"]) #maybe add the ship-to sold-to into list and then set
            pos_list.extend(df["End Customer Source Customer Name"].tolist())
        except Exception as e:
            print ("file not readable in pandas: "+ file)
            print (e)
    
    #print("creating account array")

    pos_list = set(pos_list)
    account_array = list(itertools.product(pos_list, account_list))        
    for s1,s2 in account_array:
        s1 = str(s1)
        s2 = str(s2)
        if (len(s2) <= 2):
            pass
        elif (len(s2) <= 4):
            if(editdistance.eval(s1,s2) <= 1):
                final_pos_list.append([s1,s2])
        elif (len(s2) <= 12):
            if(editdistance.eval(s1,s2) <= 2):
                final_pos_list.append([s1,s2])
        elif (len(s2) <= 24):
            if(editdistance.eval(s1,s2) <= 2):
                final_pos_list.append([s1,s2])
        else:
            if(editdistance.eval(s1,s2) <= 3):
                final_pos_list.append([s1,s2])                                                               
    #print("creating file")
    #take all files and add to single df like in v2 function
    #take above and change to final_pos_list.append([s1,s2])
    #iterate though master_df and search for s1 in customer list, add s2 as a column, save as a [df1,df2,df3,etc]
    #then concat all the dfs together like we do on v2 function,=.  That way we can see what we matched against.
    frames = []
    print("adding CSVs to master df")

    
    #test_file_list = [old_pos_file_path+"US_POS_Report 01_08 to 24_08.csv",old_pos_file_path+"US POS Current Detailed Bookings Report_V1.0 _ 117952683_757818984988416547.csv"] #delete when done testing
    #for file in test_file_list:
    for file in glob.glob(old_pos_file_path + '/*.[Cc][Ss][Vv]'): #uncomment when done testing
        try:
            with codecs.open(file,'r', 'windows-1252', errors="replace") as f:
                text = f.read()
            FILEDATA = StringIO(text)
            df = pd.DataFrame() # create empty dataframe                       
            df = pd.read_csv(FILEDATA,low_memory=False, usecols=["POS Transaction ID/Unique ID","POS Trx SCA Date",	'POS Split Adjusted Value USD', 'Product ID','POS SCA Mode','Ship-To Source Customer Name','Sold-To Source Customer Name',"End Customer Source Customer Name","End Customer CR Party ID","Salesrep Email","Salesrep Name","Salesrep #"])
        except Exception as e:
            print ("file not readable in pandas: "+ file)
            print (e)


        frames.append(df)
    #concate all df's in frames
    for frame in frames:
        print("length of frame: "+str(len(frame.index)))
    master_df = pd.concat(frames, ignore_index=True)
    #df = master_df #is this necessary, or can I call it df, even though all the concating files are df as well?
    master_df.reset_index()
    print("length of master frame: "+str(len(master_df.index)))
    print("Added all files to master data frame for processing")

    #filter out the data to process faster
    print("filtering out unnecessary data")
    temp_account_filter = []
    for account in final_pos_list:
        temp_account_filter.append(str(account[0]))
    df = master_df[(master_df['End Customer Source Customer Name'].astype(str).isin(temp_account_filter)) | (master_df['Ship-To Source Customer Name'].astype(str).isin(temp_account_filter)) | (master_df['Sold-To Source Customer Name'].astype(str).isin(temp_account_filter)) ]

    frames = [] #re-initialize frames so we can concat below df's
    print("building aggressive df")
    for account in final_pos_list:
        results = df[(df['End Customer Source Customer Name'].astype(str).str.contains(account[0])) | (df['Ship-To Source Customer Name'].astype(str).str.contains(account[0])) | (df['Sold-To Source Customer Name'].astype(str).str.contains(account[0])) ]
        #results.index.names = ['POS ID']
        results.rename(columns = {'POS Transaction ID/Unique ID':'POS ID','POS Trx SCA Date':'Date','POS Split Adjusted Value USD':'$$$','Ship-To Source Customer Name':'Ship-To','Sold-To Source Customer Name':'Sold-To','End Customer Source Customer Name':'End Customer','End Customer CR Party ID':'Party ID','POS SCA Mode':'Mode','Salesrep Name':'AM Credited'}, inplace=True)
        #results.rename(columns = {'Posted Date':'Date','POS Split Adjusted Value USD':'$$$','Ship-To Source Customer Name':'Ship-To','Sold-To Source Customer Name':'Sold-To','End Customer Source Customer Name':'End Customer','End Customer CR Party ID':'Party ID','POS SCA Mode':'Mode','Salesrep Name':'AM Credited'}, inplace=True)
        results["Sort Here"] = EMAIL
        results["Account Name"] = str(account[1])
        results = results[['POS ID','Date','Sort Here','AM Credited','Account Name','End Customer','Product ID','$$$','Ship-To','Sold-To','Party ID','Mode']]
        #results = results[['Date','Sort Here','AM Credited','End Customer','Product ID','$$$','Ship-To','Sold-To','Party ID','Mode']]
        results['Date'] = pd.to_datetime(results['Date'], errors='coerce')

        frames.append(results) #add each results df to list for cancat

    print("finished all searches, adding to CSV")
    #add the respective dfs together using concat
    master_results = pd.concat(frames, ignore_index=True)
    master_results.reset_index()


    #change the index before writing to CSV
    #master_results.set_index("POS ID")
    #master_non_error_results.set_index("POS ID")
    print("size of results = "+str(len(master_results.index)))

    #write respective dfs to CSV
    if os.path.isfile(aggressive_search_file):
        with open(aggressive_search_file, 'a') as f:
            master_results.to_csv(f, header=False,index=False)
            #print("result loop posted")
    else:
        master_results.to_csv(aggressive_search_file, index=False)
        #print("result loop posted")

    end = time.time()
    print ("Time to process: "+ str(end - start)) 
    create_html_tables()
    currentlyProcessingReports = "0"
    return ("completed in "+ str(end - start)+" seconds")


def send_csv_to_spark(ROOMID, CSV):
    msg="\n\n New POS File"
    sparkapi.messages.create(ROOMID, text=msg, files=[CSV])

def send_link_to_spark(ROOMID):
    msg="To download the latest POS file with all data: " +server_address+all_data
    sparkapi.messages.create(ROOMID, text=msg)
    msg="To browse older POS files by month: " +server_address
    sparkapi.messages.create(ROOMID, text=msg)

def send_msg_to_spark(ROOMID, msg):
    sparkapi.messages.create(ROOMID, text=msg)

def create_monthly_csv(FILE):
    df = pd.read_csv(FILE).set_index("POS ID")
    df['Date']= pd.to_datetime(df['Date'])
    


    #3rd attempt
    #Find the first date month/year, find the last date month/year.  start with the current month-1
    #create the dataframe that fit into each month/year, and write the file

    #really shouldn't be wr-writing these files each time but might need to since my update functions don't
    #pass the new data into this function.  We just grab it from the master and re-write everything each time.
    #in order to iterate through the months, we use divmod.

    min = df['Date'].min()
    max = df['Date'].max()

    #using months and years, 12 months in a year so month is smallest single unit(aka multiply by 1)
    # so start year x 12, + start month x 1, added together will give you a number, same for max
    #using divmod, when we divide each number in between the range by 12, we will get the year by how many
    #times it is divisable, aka, the quotient.  The remainder, will be a range between 0 and 11 (if it is 12,
    #then it would be divisiable again).  So if we add 1 to the remainder, it will give the month.
    #got this algorithm from stackoverflow
    ym_start= 12*min.year + min.month - 1 
    ym_end= 12*max.year + max.month - 1 

    for ym in range( ym_start, ym_end ):
        y, m = divmod( ym, 12 )
        df_month = df[(df['Date'].dt.month == m+1) & (df['Date'].dt.year == y)]
        if not df_month.empty:
            t = datetime(y, m+1, 1)
            monthly_csv_filename = filtered_filepath+t.strftime("%Y-%B-monthly-data.csv")
            with open(monthly_csv_filename, 'w') as f:
                df_month.to_csv(f)            
            print("Created file: "+t.strftime("%Y-%B-monthly-data.csv"))    



    '''
    #2nd attempt at this
    #problem with this is that it is only catching the month, and then assuming the year, so if I rerun the reports
    #on january, all the older month files,e.g., december, will get re-written with the new year, not the previous correct year
    months = []
    for month in df['Date'].dt.month:
        months.append(month)
    months = set(months)
    for month in months:
        if month != now.month: #don't make a file unless the month is done
            #print(month)
            #print(now.month)
            df_month = df[df['Date'].dt.month == month]
            if not df_month.empty:
                t = datetime(now.year, month, 1)
                monthly_csv_filename = filtered_filepath+t.strftime("%Y-%B-monthly-data.csv")
                print("Created file: "+t.strftime("%Y-%B-monthly-data.csv"))
                with open(monthly_csv_filename, 'w') as f:
                    df_month.to_csv(f)     
        #else:
            #print(month)
    '''

    '''
    #first attempt at this
    i = 1
    #change this?  Not sure if it works come January, or at least won't update previous months
    while (i < now.month):
        df_month = df[df['Date'].dt.month == i]
        if not df_month.empty:
            t = datetime(now.year, i, 1)
            monthly_csv_filename = filtered_filepath+t.strftime("%Y-%B-monthly-data.csv")
            print("Created file: "+t.strftime("%Y-%B-monthly-data.csv"))
            with open(monthly_csv_filename, 'w') as f:
                df_month.to_csv(f)
        i = i+1
    '''


def create_area_reports(ALLCSV,NONERRORCSV,OPLIST):
  

    df = pd.read_csv(ALLCSV).set_index("POS ID")

    ne_df = pd.read_csv(NONERRORCSV).set_index("POS ID")

    #OPLIST has every SL1,2,3,4 in a list, as well as a duplicate with no spaces for filenames
    #iterate through each and create files for every SL level.
    #I need to create a file for all segments as well, which means I need to know which SL level I am iterating
    #so I can df search appropriately

    #[[[SL1_1a,SL1_1b]],[[SL2_1a,SL2_1b],[SL2_2a,SL2_2b]]]
    #the a entry is the actual name in db, the b is without spaces for file names
    SL_loop = 0
    for SL in OPLIST:
        SL_loop += 1
        for i in SL:
            if (SL_loop == 1):
                i_df = df[df["SL1"].str.contains(i[0])] 
                ne_i_df = ne_df[ne_df["SL1"].str.contains(i[0])]
                print(str(i[0]))
            elif (SL_loop == 2):
                i_df = df[df["SL2"].str.contains(i[0])] 
                ne_i_df = ne_df[ne_df["SL2"].str.contains(i[0])] 
                print(str(i[0]))   
            elif (SL_loop == 3):
                i_df = df[df["Area"].str.contains(i[0])] 
                ne_i_df = ne_df[ne_df["Area"].str.contains(i[0])]
                print(str(i[0]))
            elif (SL_loop == 4):                           
                i_df = df[df["Operation"].str.contains(i[0])] 
                ne_i_df = ne_df[ne_df["Operation"].str.contains(i[0])]
                print(str(i[0]))
            else:
                print("something wrong with report creating")

            #create monthly reports per operation
            #explanation for this is in old monthly report function
            
            print('length of data: '+str(len(i_df.index)))
            print('length of ne data: '+str(len(ne_i_df.index)))
            if ((len(i_df.index) > 0) and (len(ne_i_df.index) > 0)):
                i_df['Date']= pd.to_datetime(i_df['Date'], errors='coerce') #to parse the time column
                i_df = i_df.dropna(subset=['Date']) #get rid of all rows that don't have a date in date column
                min = i_df['Date'].min()
                print('min: '+str(min))
                print('min.year / month:  '+str(min.year)+'     '+str(min.month))
                max = i_df['Date'].max()
                print('max: '+str(max))
                print('max.year / month:  '+str(max.year)+'     '+str(max.month))
                ym_start= 12*min.year + min.month - 1 
                ym_end= 12*max.year + max.month - 1 
                print('ym_start'+str(ym_start))
                print('ym_end'+str(ym_end))
                for ym in range( ym_start, ym_end ):
                    y, m = divmod( ym, 12 )
                    df_month = i_df[(i_df['Date'].dt.month == m+1) & (i_df['Date'].dt.year == y)]
                    if not df_month.empty:
                        #df_month.set_index('POS ID')
                        t = datetime(y, m+1, 1)
                        monthly_csv_filename = filtered_filepath+i[1]+"_"+t.strftime("%Y-%B-monthly-data.csv")
                        with open(monthly_csv_filename, 'w') as f:
                            df_month.to_csv(f)            
                        print("Created file: "+i[1]+"_"+t.strftime("%Y-%B-monthly-data.csv"))  



            #op_df.set_index('POS ID')
            #ne_op_df.set_index('POS ID')




            print("Filename: "+home_file_path+i[1]+"_"+all_data)
            with open(filtered_filepath+i[1]+"_"+all_data, 'w') as f:
                i_df.to_csv(f)
            with open(filtered_filepath+i[1]+"_"+non_error_pos_data, 'w') as f:
                ne_i_df.to_csv(f)





    '''
    for operation in OPLIST:
        op_df = df[df["Operation"].str.contains(operation[6])] #name of op
        ne_op_df = ne_df[ne_df["Operation"].str.contains(operation[6])]

        #create monthly reports per operation
        #explanation for this is in old monthly report function
        op_df['Date']= pd.to_datetime(op_df['Date']) #to parse the time column
        min = op_df['Date'].min()
        max = op_df['Date'].max()
        ym_start= 12*min.year + min.month - 1 
        ym_end= 12*max.year + max.month - 1 

        for ym in range( ym_start, ym_end ):
            y, m = divmod( ym, 12 )
            df_month = op_df[(op_df['Date'].dt.month == m+1) & (op_df['Date'].dt.year == y)]
            if not df_month.empty:
                #df_month.set_index('POS ID')
                t = datetime(y, m+1, 1)
                monthly_csv_filename = filtered_filepath+operation[7]+"_"+t.strftime("%Y-%B-monthly-data.csv")
                with open(monthly_csv_filename, 'w') as f:
                    df_month.to_csv(f)            
                print("Created file: "+operation[7]+"_"+t.strftime("%Y-%B-monthly-data.csv"))  



        #op_df.set_index('POS ID')
        #ne_op_df.set_index('POS ID')




        print("Filename: "+home_file_path+operation[7]+"_"+all_data)
        with open(filtered_filepath+operation[7]+"_"+all_data, 'w') as f:
            op_df.to_csv(f)
        with open(filtered_filepath+operation[7]+"_"+non_error_pos_data, 'w') as f:
            ne_op_df.to_csv(f)
    '''

#def move_last_year_files_to_dif_folder()
    #To do

def create_html_tables():

    now = datetime.now()
    ago = now-timedelta(minutes=10)
    #html = """   <script>$(document).change(function(){$('tr').click(function get_my_data(e){var row = e.currentTarget;var cell = row.getElementsByTagName('td');var POS = cell[0].innerHTML;console.log(POS);window.location = "mailto:eiwalsh@cisco.com?subject=Please%20claim%20POS%20order-"+cell[0].innerHTML+"-"+cell[2].innerHTML+"&body=%0D%0AI%20believe%20this%20order%20should%20be%20credited%20to%20me.%20%20Here%20is%20what%20I%20know:%0D%0A%0D%0APOSID:%09:%09"+cell[0].innerHTML+"%0D%0ADATE:%09:%09"+cell[1].innerHTML+"%0D%0AMy%20CCOID:%09:%09"+cell[2].innerHTML+"%0D%0ACredited:%09:%09"+cell[3].innerHTML+"%0D%0AEnd%20customer:%09:%09"+cell[4].innerHTML+"%0D%0AShipped%20to:%09:%09"+cell[7].innerHTML+"%0D%0ASold%20to:%09:%09"+cell[8].innerHTML+"%0D%0AParty%20ID:%09:%09"+cell[9].innerHTML+"%0D%0AProduct%20ID:%09:%09"+cell[5].innerHTML+"%0D%0AValue:%09%09:%09"+cell[6].innerHTML+"%0D%0A";});});</script> """
    #html = """ <script>$(document).on('click', 'td', function(e){var cell = e.currentTarget.innerHTML;var row = e.currentTarget.closest('tr');var cells = row.getElementsByTagName('td');var POS = cells[0].innerHTML;if (cell == POS){window.location = "mailto:onecommercial@cisco.com?subject=Please%20claim%20POS%20order-"+cells[0].innerHTML+"-"+cells[2].innerHTML+"&cc=jleatham@cisco.com&body=%0D%0AI%20believe%20this%20order%20should%20be%20credited%20to%20me.%20%20Details:%0D%0A%0D%0APOSID:%09:%09"+cells[0].innerHTML+"%0D%0ADATE:%09:%09"+cells[1].innerHTML+"%0D%0AMy%20CCOID:%09:%09"+cells[2].innerHTML+"%0D%0ACredited:%09:%09"+cells[3].innerHTML+"%0D%0AEnd%20customer:%09:%09"+cells[4].innerHTML+"%0D%0AShipped%20to:%09:%09"+cells[7].innerHTML+"%0D%0ASold%20to:%09:%09"+cells[8].innerHTML+"%0D%0AParty%20ID:%09:%09"+cells[9].innerHTML+"%0D%0AProduct%20ID:%09:%09"+cells[5].innerHTML+"%0D%0AValue:%09%09:%09"+cells[6].innerHTML+"%0D%0A";}});</script> """
    html = """ <script>$(document).on('click', 'td', function(e){var cell = e.currentTarget.innerHTML;var row = e.currentTarget.closest('tr');var cells = row.getElementsByTagName('td');var POS = cells[0].innerHTML;var dollarValue = cells[6].innerHTML;var cellDate = cells[1].innerHTML;var amCredit = cells[3].innerHTML;var date1 = new Date(cellDate);var date2 = new Date();var timeDiff = Math.abs(date2.getTime() - date1.getTime());var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24)); 			if ((cell == POS) && (diffDays <= 60) && (dollarValue >= 3000)){console.log('made it here');location.href = "mailto:onecommercial@cisco.com?subject=Please%20claim%20POS%20order-"+cells[0].innerHTML+"-"+cells[2].innerHTML+"&cc=jleatham@cisco.com&body=%0D%0AI%20believe%20this%20order%20should%20be%20credited%20to%20me.%20%20Details:%0D%0A%0D%0APOSID:%09:%09"+cells[0].innerHTML+"%0D%0ADATE:%09:%09"+cells[1].innerHTML+"%0D%0AMy%20CCOID:%09:%09"+cells[2].innerHTML+"%0D%0ACredited:%09:%09"+cells[3].innerHTML+"%0D%0AEnd%20customer:%09:%09"+cells[4].innerHTML+"%0D%0AShipped%20to:%09:%09"+cells[7].innerHTML+"%0D%0ASold%20to:%09:%09"+cells[8].innerHTML+"%0D%0AParty%20ID:%09:%09"+cells[9].innerHTML+"%0D%0AProduct%20ID:%09:%09"+cells[5].innerHTML+"%0D%0AValue:%09%09:%09"+cells[6].innerHTML+"%0D%0A";}else if ((cell == POS) && (diffDays > 60) ) {alert("POS policy: Claim must be within 60 days.")}	else if ((cell == POS) && (dollarValue < 3000) ) {alert("POS policy: Claim must be a line-item above above 3K or overall deal above 30K.  Check MBR first before submitting a claim.")}});</script> """
    
    html2 = """ <script>window.onload = function() {if(!window.location.hash) {window.location = window.location + '#loaded';window.location.reload();}}</script> """
    for file in glob.glob(filtered_filepath + '/*.[Cc][Ss][Vv]'):
        #only create HTML files that were modified recently
        st = os.stat(file)
        mtime = datetime.fromtimestamp(st.st_mtime)
        if (mtime > ago): #modified less than 10 minutes ago
            print("{0}     modified     {1}".format(file, mtime))        
            filename = os.path.basename(file)
            filename = os.path.splitext(filename)[0]
            os.system("csvtotable -o -vs=0 "+file+" "+filtered_filepath + filename+".html")
            with open(filtered_filepath + filename+".html", 'r') as f:
                webpage = f.read()

            soup = Soup(webpage)

            style = soup.find('style')
            style.insert_before(html)
            style.insert_before(html2)

            metatag1 = soup.new_tag('meta')
            metatag1.attrs['http-equiv'] = 'Cache-Control'
            metatag1.attrs['content'] = 'no-cache, no-store, must-revalidate'
            soup.head.append(metatag1)

            metatag2 = soup.new_tag('meta')
            metatag2.attrs['http-equiv'] = 'Pragma'
            metatag2.attrs['content'] = 'no-cache'
            soup.head.append(metatag2)

            metatag3 = soup.new_tag('meta')
            metatag3.attrs['http-equiv'] = 'Expires'
            metatag3.attrs['content'] = '0'
            soup.head.append(metatag3)                

            newsoup = soup.prettify(formatter=None)
            with open(filtered_filepath + filename+".html", 'w') as f:
                f.write(str(newsoup))


        #print("Jquery added to current_data.html")
    print("HTML files created")

    #HTML to inject into html table
    #html = """ <script>$(document).change(function(){$('tr').click(function get_my_data(e){var row = e.currentTarget;var cell = row.getElementsByTagName('td');var POS = cell[0].innerHTML;$.ajax({url: "/current_data.html",data: {pos_value: POS},type: 'POST',success: function(response){alert(response)},error: function(error){console.log(error);}});});});</script> """



def get_time_frame(FILE):
    #should try/catch this incase something happens to the current_data file, it will throw an error
    df = pd.read_csv(FILE, usecols=['Date'])
    df['Date']= pd.to_datetime(df['Date'])
    least_recent_date = df['Date'].min()
    recent_date = df['Date'].max()
    recent_date = recent_date.strftime("%B %d, %Y")
    least_recent_date = least_recent_date.strftime("%B %d, %Y")
    return recent_date,least_recent_date 

def flask_load_json_to_mem(FILE):
    if not (os.stat(FILE).st_size == 0):
        with open(FILE) as data_file:
            return json.load(data_file)  
    else:
        print("could not find/load JSON file")
        return {}

def set_global(val):
    global currentlyProcessingReports
    currentlyProcessingReports = val #string 1 or 0
    return currentlyProcessingReports

def getCurrentlyProcessingReportsGlobal():
    global currentlyProcessingReports
    #print("getting global")
    return currentlyProcessingReports

def display_logs():
    x = "<p>Last 100 lines in file:</p><p>...</p>"
    f = open(home_file_path+"pos_log.out","r")
    m = deque(f, maxlen=100)
    for line in m:
        x += "<p>"+line+"</p>"

    x += "<p>...</p><p>...</p><p>Logfile from start:</p><p>...</p><p>...</p>"
    f.close
    f = open(home_file_path+"pos_log.out","r")
    lines = f.readlines()
    f.close()
    for line in lines:
        x += "<p>"+line+"</p>"
    return x


def real_time_search(account,email,pos,party,searchAction):
    ##Pseudo code
    #HTML file has form field for every column(or only a few) in POS
    #on submit, return those variables in an array or dict or something
    #parse those values here and load them into individual variables
    #use df[df[]] function with 
    #before df statement, do something with columns that have no imput, 
    # # # either put a dummy value or find a clever way to deal with this
    #return what?  a long string with html already embedded?  json with each row a value?
    # # # json with each row an entry and each column a key?
    # When doing this in CLI, the df statement was fast, but the iteration of each line took longer
    # # # and it could print out in real time, ajax is an all at once type of thing
    # should include a size/time limit so as to not hose up system with stupid search
    start = time.time()
    if not account and not email and not pos and not party:
        return {"status":"<p>Must have at least 1 search variable</p>"}
    if searchAction == 'and':
        if not account:
            account = '.*'
        if not email:
            email = '.*'
        if not pos:
            pos = '.*'
        if not party:
            party = '.*'
    else:
        if not account:
            account = 'abcdefghij'
        if not email:
            email = 'abcdefghij'
        if not pos:
            pos = 'abcdefghij'
        if not party:
            party = 'abcdefghij'        
    print("RealTimeSearch:  account: "+account+"     email: "+email+"    pos: "+pos+"    party: "+party+"     searchAction: "+searchAction)
    #print("account var: "+account)
    #print("email var: "+email)
    #print("pos var: "+pos)
    #print("party var: "+party)
    #print("searchAction var: "+searchAction)


    all_files = glob.glob(os.path.join(old_pos_file_path, "*.[Cc][Ss][Vv]"))     # advisable to use os.path.join as this makes concatenation OS independent
    #print("loading dfs")
    df_from_each_file = (pd.read_csv(f, encoding='cp1252',low_memory=False, usecols=["POS Transaction ID/Unique ID","POS Trx SCA Date",	'POS Split Adjusted Value USD', 'Product ID','POS SCA Mode','Ship-To Source Customer Name','Sold-To Source Customer Name',"End Customer Source Customer Name","End Customer CR Party ID","Salesrep Email","Salesrep Name"]) for f in all_files)
    #df_from_each_file = (pd.read_csv(f, encoding='cp1252',low_memory=False).set_index("POS Transaction ID/Unique ID") for f in all_files)    
    #df   = pd.concat(df_from_each_file, ignore_index=True)
    #print("concating dfs")
    df   = pd.concat(df_from_each_file, ignore_index=True)

    #prep the integers to be searches as strings and get rid of errors
    df["End Customer CR Party ID"] = df["End Customer CR Party ID"].astype(int, errors='ignore')
    df["End Customer CR Party ID"] = df["End Customer CR Party ID"].astype(str, errors='ignore')
    df["POS Transaction ID/Unique ID"] = df["POS Transaction ID/Unique ID"].astype(int, errors='ignore')
    df["POS Transaction ID/Unique ID"] = df["POS Transaction ID/Unique ID"].astype(str, errors='ignore')
    #print("searching df")
    if searchAction == 'and':
        results = df[(df['End Customer Source Customer Name'].str.contains(account, na=False) | df['Ship-To Source Customer Name'].str.contains(account, na=False) | df['Sold-To Source Customer Name'].str.contains(account, na=False)) & df["Salesrep Email"].str.contains(email, na=False) & df["End Customer CR Party ID"].str.contains(party, na=False) & df["POS Transaction ID/Unique ID"].str.contains(pos, na=False)]
    else:
        results = df[(df['End Customer Source Customer Name'].str.contains(account, na=False) | df['Ship-To Source Customer Name'].str.contains(account, na=False) | df['Sold-To Source Customer Name'].str.contains(account, na=False)) | df["Salesrep Email"].str.contains(email, na=False) | df["End Customer CR Party ID"].str.contains(party, na=False) | df["POS Transaction ID/Unique ID"].str.contains(pos, na=False)]
    results.rename(columns = {"POS Transaction ID/Unique ID":'POS ID','POS Trx SCA Date':'Date','POS Split Adjusted Value USD':'$$$','Ship-To Source Customer Name':'Ship-To','Sold-To Source Customer Name':'Sold-To','End Customer Source Customer Name':'End Customer','End Customer CR Party ID':'Party ID','POS SCA Mode':'Mode'}, inplace=True)
    results["Sort Here"] = "Not In Use"
    results = results[['POS ID','Date','Sort Here','Salesrep Name','End Customer','Product ID','$$$','Ship-To','Sold-To','Party ID','Mode']]
    results['Date'] = pd.to_datetime(results['Date'], errors='coerce')
    # doesn't create a list, nor does it append to one  
    #print("creating csv file")  
    csv_filename = real_time_search_file_path+timestr+".csv"
    print(csv_filename)
    results.to_csv(csv_filename,index=False)
    #print(sys.getsizeof(json_file))
    


    #if sys.getsizeof(json_file) < 3000000:
        #return json_file
    #else:
        #return {"error":" Too many results, please filter"}




    #html = """   <script>$(document).change(function(){$('tr').click(function get_my_data(e){var row = e.currentTarget;var cell = row.getElementsByTagName('td');var POS = cell[0].innerHTML;console.log(POS);window.location = "mailto:eiwalsh@cisco.com?subject=Please%20claim%20POS%20order-"+cell[0].innerHTML+"-"+cell[2].innerHTML+"&body=%0D%0AI%20believe%20this%20order%20should%20be%20credited%20to%20me.%20%20Here%20is%20what%20I%20know:%0D%0A%0D%0APOSID:%09:%09"+cell[0].innerHTML+"%0D%0ADATE:%09:%09"+cell[1].innerHTML+"%0D%0AMy%20CCOID:%09:%09"+cell[2].innerHTML+"%0D%0ACredited:%09:%09"+cell[3].innerHTML+"%0D%0AEnd%20customer:%09:%09"+cell[4].innerHTML+"%0D%0AShipped%20to:%09:%09"+cell[7].innerHTML+"%0D%0ASold%20to:%09:%09"+cell[8].innerHTML+"%0D%0AParty%20ID:%09:%09"+cell[9].innerHTML+"%0D%0AProduct%20ID:%09:%09"+cell[5].innerHTML+"%0D%0AValue:%09%09:%09"+cell[6].innerHTML+"%0D%0A";});});</script> """
    #html = """ <script>$(document).on('click', 'td', function(e){var cell = e.currentTarget.innerHTML;var row = e.currentTarget.closest('tr');var cells = row.getElementsByTagName('td');var POS = cells[0].innerHTML;if (cell == POS){window.location = "mailto:onecommercial@cisco.com?subject=Please%20claim%20POS%20order-"+cells[0].innerHTML+"&cc=jleatham@cisco.com&body=%0D%0AI%20believe%20this%20order%20should%20be%20credited%20to%20me.%20%20Details:%0D%0A%0D%0APOSID:%09:%09"+cells[0].innerHTML+"%0D%0ADATE:%09:%09"+cells[1].innerHTML+"%0D%0ACredited:%09:%09"+cells[3].innerHTML+"%0D%0AEnd%20customer:%09:%09"+cells[4].innerHTML+"%0D%0AShipped%20to:%09:%09"+cells[7].innerHTML+"%0D%0ASold%20to:%09:%09"+cells[8].innerHTML+"%0D%0AParty%20ID:%09:%09"+cells[9].innerHTML+"%0D%0AProduct%20ID:%09:%09"+cells[5].innerHTML+"%0D%0AValue:%09%09:%09"+cells[6].innerHTML+"%0D%0A";}});</script> """
    html = """ <script>$(document).on('click', 'td', function(e){var cell = e.currentTarget.innerHTML;var row = e.currentTarget.closest('tr');var cells = row.getElementsByTagName('td');var POS = cells[0].innerHTML;var dollarValue = cells[6].innerHTML;var cellDate = cells[1].innerHTML;var amCredit = cells[3].innerHTML;var date1 = new Date(cellDate);var date2 = new Date();var timeDiff = Math.abs(date2.getTime() - date1.getTime());var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24)); 			if ((cell == POS) && (diffDays <= 60) && (dollarValue >= 3000)){console.log('made it here');location.href = "mailto:onecommercial@cisco.com?subject=Please%20claim%20POS%20order-"+cells[0].innerHTML+"-"+cells[2].innerHTML+"&cc=jleatham@cisco.com&body=%0D%0AI%20believe%20this%20order%20should%20be%20credited%20to%20me.%20%20Details:%0D%0A%0D%0APOSID:%09:%09"+cells[0].innerHTML+"%0D%0ADATE:%09:%09"+cells[1].innerHTML+"%0D%0AMy%20CCOID:%09:%09"+cells[2].innerHTML+"%0D%0ACredited:%09:%09"+cells[3].innerHTML+"%0D%0AEnd%20customer:%09:%09"+cells[4].innerHTML+"%0D%0AShipped%20to:%09:%09"+cells[7].innerHTML+"%0D%0ASold%20to:%09:%09"+cells[8].innerHTML+"%0D%0AParty%20ID:%09:%09"+cells[9].innerHTML+"%0D%0AProduct%20ID:%09:%09"+cells[5].innerHTML+"%0D%0AValue:%09%09:%09"+cells[6].innerHTML+"%0D%0A";}else if ((cell == POS) && (diffDays > 60) ) {alert("POS policy: Claim must be within 60 days.")}	else if ((cell == POS) && (dollarValue < 3000) ) {alert("POS policy: Claim must be a line-item above above 3K or overall deal above 30K.  Check MBR first before submitting a claim.")}});</script> """
    html2 = """ <script>window.onload = function() {if(!window.location.hash) {window.location = window.location + '#loaded';window.location.reload();}}</script> """


    filename = os.path.basename(csv_filename)
    filename = os.path.splitext(filename)[0]
    #print(filename)
    os.system("csvtotable -o -vs=0 "+csv_filename+" "+real_time_search_file_path + filename+".html")
    with open(real_time_search_file_path + filename+".html", 'r') as f:
        webpage = f.read()

    soup = Soup(webpage)

    style = soup.find('style')
    style.insert_before(html)
    style.insert_before(html2)

    metatag1 = soup.new_tag('meta')
    metatag1.attrs['http-equiv'] = 'Cache-Control'
    metatag1.attrs['content'] = 'no-cache, no-store, must-revalidate'
    soup.head.append(metatag1)

    metatag2 = soup.new_tag('meta')
    metatag2.attrs['http-equiv'] = 'Pragma'
    metatag2.attrs['content'] = 'no-cache'
    soup.head.append(metatag2)

    metatag3 = soup.new_tag('meta')
    metatag3.attrs['http-equiv'] = 'Expires'
    metatag3.attrs['content'] = '0'
    soup.head.append(metatag3)                

    newsoup = soup.prettify(formatter=None)
    with open(real_time_search_file_path + filename+".html", 'w') as f:
        f.write(str(newsoup))


    #print("Jquery added to current_data.html")
    #print("HTML files created")
    end = time.time()
    print ("Time to process: "+ str(end - start))
    return {"status":"<p><a href='/realtimesearch/"+filename+".html'  target='_blank'>Search Results</a></p>"}


op_list,op_list1 = get_op_list() #set global