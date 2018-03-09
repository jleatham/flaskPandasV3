from flask import Flask, request, render_template, send_from_directory
from flask.json import jsonify
import json
from POS_automation import *
app = Flask(__name__)

# @ signifies a decorator - way to wrap a function and modify its behavior



@app.route('/')
def index():
    #need to change this to /CSA
    #need to change CSA reports to include CSA_ tag and only display those... so that I can add more areas later
    global report_runtime, recent_date, least_recent_date #used to check date of last POS report
    html_files = []
    agg_html_files = []
    #make sure the update doesn't get ran everytime the page is loaded
    curr_time = int(time.time())
    try:
        if curr_time - report_runtime > 500:
            report_runtime = curr_time
            recent_date,least_recent_date = get_time_frame(all_data_csv_filename)
            #print("report date was updated")
    except:
        recent_date = "Not ran yet"
        least_recent_date = "Not ran yet" 
        
    for file in glob.glob(filtered_filepath + '/*.[Hh][Tt][Mm][Ll]'):
        filename = os.path.basename(file)
        if "aggressive" in filename:
            agg_html_files.append(filename)     
        else:
            html_files.append(filename)
    
    #html_files is sent to web page, and jinja2 takes the list and put them in a list of URLs
    try: #my curl test throws error when the main report is running
        agg_html_files = sorted(agg_html_files)
        html_files = sorted(html_files) #sort list alphabetically
        #html_files.insert(0,html_files.pop(html_files.index("current_data.html"))) #move to beginning of list
        html_files.pop(html_files.index("current_data.html")) #remove from list as I put it as a button on page
        html_files.append(html_files.pop(html_files.index("non_error_pos_data.html"))) #move to end of list
    except:
        print("cannot process files as report is being ran")

    title = "POS Tool"
    description = "Not that kind of POS"
    pageType = 'test'    
    return render_template("index.html", title=title, description=description, pageType=pageType,recent=recent_date,least_recent=least_recent_date,files=html_files,aggfiles=agg_html_files)

'''
@app.route('/CSA/SWSO')
def SWSO():
    global report_runtime, recent_date, least_recent_date #used to check date of last POS report
    html_files = []
    agg_html_files = []
    #make sure the update doesn't get ran everytime the page is loaded
    curr_time = int(time.time())
    if curr_time - report_runtime > 500:
        report_runtime = curr_time
        recent_date,least_recent_date = get_time_frame(all_data_csv_filename)
        #print("report date was updated")
    
    for file in glob.glob(filtered_filepath + '/*.[Hh][Tt][Mm][Ll]'):
        filename = os.path.basename(file)
        if "SWSO_aggressive" in filename:
            agg_html_files.append(filename)     
        elif "SWSO" in filename:
            html_files.append(filename)
    
    #html_files is sent to web page, and jinja2 takes the list and put them in a list of URLs
    try: #my curl test throws error when the main report is running
        agg_html_files = sorted(agg_html_files)
        html_files = sorted(html_files) #sort list alphabetically
        #html_files.insert(0,html_files.pop(html_files.index("current_data.html"))) #move to beginning of list
        html_files.pop(html_files.index("SWSO_current_data.html")) #remove from list as I put it as a button on page
        html_files.append(html_files.pop(html_files.index("SWSO_non_error_pos_data.html"))) #move to end of list
    except:
        print("cannot process files as report is being ran")

    title = "SWSO Reports"
    description = "Find mis-booked POS items for SWSO"
    pageType = 'test'    
    return render_template("swso.html", title=title, description=description, pageType=pageType,recent=recent_date,least_recent=least_recent_date,files=html_files,aggfiles=agg_html_files)
     
@app.route('/CSA/SESO')
def SESO():
    global report_runtime, recent_date, least_recent_date #used to check date of last POS report
    html_files = []
    agg_html_files = []
    #make sure the update doesn't get ran everytime the page is loaded
    curr_time = int(time.time())
    if curr_time - report_runtime > 500:
        report_runtime = curr_time
        recent_date,least_recent_date = get_time_frame(all_data_csv_filename)
        #print("report date was updated")
    
    for file in glob.glob(filtered_filepath + '/*.[Hh][Tt][Mm][Ll]'):
        filename = os.path.basename(file)
        if "SESO_aggressive" in filename:
            agg_html_files.append(filename)     
        elif "SESO" in filename:
            html_files.append(filename)
    
    #html_files is sent to web page, and jinja2 takes the list and put them in a list of URLs
    try: #my curl test throws error when the main report is running
        agg_html_files = sorted(agg_html_files)
        html_files = sorted(html_files) #sort list alphabetically
        #html_files.insert(0,html_files.pop(html_files.index("current_data.html"))) #move to beginning of list
        html_files.pop(html_files.index("SESO_current_data.html")) #remove from list as I put it as a button on page
        html_files.append(html_files.pop(html_files.index("SESO_non_error_pos_data.html"))) #move to end of list
    except:
        print("cannot process files as report is being ran")

    title = "SESO Reports"
    description = "Find mis-booked POS items for SESO"
    pageType = 'test'    
    return render_template("seso.html", title=title, description=description, pageType=pageType,recent=recent_date,least_recent=least_recent_date,files=html_files,aggfiles=agg_html_files)
    
@app.route('/CSA/STO')
def STO():
    global report_runtime, recent_date, least_recent_date #used to check date of last POS report
    html_files = []
    agg_html_files = []
    #make sure the update doesn't get ran everytime the page is loaded
    curr_time = int(time.time())
    if curr_time - report_runtime > 500:
        report_runtime = curr_time
        recent_date,least_recent_date = get_time_frame(all_data_csv_filename)
        #print("report date was updated")
    
    for file in glob.glob(filtered_filepath + '/*.[Hh][Tt][Mm][Ll]'):
        filename = os.path.basename(file)
        if "STO_aggressive" in filename:
            agg_html_files.append(filename)     
        elif "STO" in filename:
            html_files.append(filename)
    
    #html_files is sent to web page, and jinja2 takes the list and put them in a list of URLs
    try: #my curl test throws error when the main report is running
        agg_html_files = sorted(agg_html_files)
        html_files = sorted(html_files) #sort list alphabetically
        #html_files.insert(0,html_files.pop(html_files.index("current_data.html"))) #move to beginning of list
        html_files.pop(html_files.index("STO_current_data.html")) #remove from list as I put it as a button on page
        html_files.append(html_files.pop(html_files.index("STO_non_error_pos_data.html"))) #move to end of list
    except:
        print("cannot process files as report is being ran")

    title = "STO Reports"
    description = "Find mis-booked POS items for STO"
    pageType = 'test'    
    return render_template("sto.html", title=title, description=description, pageType=pageType,recent=recent_date,least_recent=least_recent_date,files=html_files,aggfiles=agg_html_files)
    
'''
@app.route('/reports/<SL1_page>')
def SL1_reports(SL1_page):
    
    global report_runtime, recent_date, least_recent_date, op_list1
    html_files = []
    agg_html_files = []
    #make sure the update doesn't get ran everytime the page is loaded
    curr_time = int(time.time())
    if curr_time - report_runtime > 500:
        report_runtime = curr_time
        recent_date,least_recent_date = get_time_frame(all_data_csv_filename)

    page = "{0}".format(SL1_page)
    #print("We made it here")
    #print("We got globals"+str(op_list1))
    #print("page we are looking for: "+page)
    for i in op_list1:
        page_list_SL1 = "{0}".format(i[0])

        if page==page_list_SL1:
            for file in glob.glob(filtered_filepath + '/*.[Hh][Tt][Mm][Ll]'):
                filename = os.path.basename(file)
                if "{0}_aggressive".format(i[0]) in filename:
                    agg_html_files.append(filename)     
                elif "{0}_current".format(i[0]) in filename:
                    current_filename = filename                
                elif "{0}".format(i[0]) in filename:
                    html_files.append(filename)
            try: #my curl test throws error when the main report is running
                agg_html_files = sorted(agg_html_files)
                html_files = sorted(html_files) #sort list alphabetically
                #html_files.insert(0,html_files.pop(html_files.index("current_data.html"))) #move to beginning of list
                #html_files.pop(html_files.index("{1}_current_data.html".format(i[1]))) #remove from list as I put it as a button on page
                html_files.append(html_files.pop(html_files.index("{0}_non_error_pos_data.html".format(i[0])))) #move to end of list
            except:
                print("cannot process files as report is being ran")
            title = "{0} Reports".format(i[0])
            description = "Find mis-booked POS items for {0}".format(i[0])
            pageType = 'test'            
            return render_template('report_page.html', title=title, description=description, pageType=pageType,recent=recent_date,least_recent=least_recent_date,files=html_files,aggfiles=agg_html_files,current_filename=current_filename)

    return "Could not find page"



@app.route('/reports/<SL1_page>/<SL2_page>')
def SL2_reports(SL1_page,SL2_page):
    
    global report_runtime, recent_date, least_recent_date, op_list1
    html_files = []
    agg_html_files = []
    #make sure the update doesn't get ran everytime the page is loaded
    curr_time = int(time.time())
    if curr_time - report_runtime > 500:
        report_runtime = curr_time
        recent_date,least_recent_date = get_time_frame(all_data_csv_filename)

    page = "{0}/{1}".format(SL1_page,SL2_page)
    #print("We made it here")
    #print("We got globals"+str(op_list1))
    #print("page we are looking for: "+page)
    for i in op_list1:
        page_list_SL2 = "{0}/{1}".format(i[0],i[1])

        if page==page_list_SL2:
            #print("went to SL2 if statement")
            for file in glob.glob(filtered_filepath + '/*.[Hh][Tt][Mm][Ll]'):
                filename = os.path.basename(file)
                if "{0}_aggressive".format(i[1]) in filename:
                    agg_html_files.append(filename)     
                elif "{0}_current".format(i[1]) in filename:
                    current_filename = filename                
                elif "{0}".format(i[1]) in filename:
                    html_files.append(filename)
            try: #my curl test throws error when the main report is running
                agg_html_files = sorted(agg_html_files)
                html_files = sorted(html_files) #sort list alphabetically
                #html_files.insert(0,html_files.pop(html_files.index("current_data.html"))) #move to beginning of list
                #html_files.pop(html_files.index("{1}_current_data.html".format(i[1]))) #remove from list as I put it as a button on page
                html_files.append(html_files.pop(html_files.index("{0}_non_error_pos_data.html".format(i[1])))) #move to end of list
            except:
                print("cannot process files as report is being ran")
            title = "{0} Reports".format(i[1])
            description = "Find mis-booked POS items for {0}".format(i[1])
            pageType = 'test'            
            return render_template('report_page.html', title=title, description=description, pageType=pageType,recent=recent_date,least_recent=least_recent_date,files=html_files,aggfiles=agg_html_files,current_filename=current_filename)

    return "Could not find page"


@app.route('/reports/<SL1_page>/<SL2_page>/<SL3_page>')
def SL3_reports(SL1_page,SL2_page,SL3_page):
    
    global report_runtime, recent_date, least_recent_date, op_list1
    html_files = []
    agg_html_files = []
    #make sure the update doesn't get ran everytime the page is loaded
    curr_time = int(time.time())
    if curr_time - report_runtime > 500:
        report_runtime = curr_time
        recent_date,least_recent_date = get_time_frame(all_data_csv_filename)

    page = "{0}/{1}/{2}".format(SL1_page,SL2_page,SL3_page)
    #print("We made it here")
    #print("We got globals"+str(op_list1))
    #print("page we are looking for: "+page)
    for i in op_list1:
        page_list_SL3 = "{0}/{1}/{2}".format(i[0],i[1],i[2])

        if page==page_list_SL3:
            for file in glob.glob(filtered_filepath + '/*.[Hh][Tt][Mm][Ll]'):
                filename = os.path.basename(file)
                if "{0}_aggressive".format(i[2]) in filename:
                    agg_html_files.append(filename)     
                elif "{0}_current".format(i[2]) in filename:
                    current_filename = filename                
                elif "{0}".format(i[2]) in filename:
                    html_files.append(filename)
            try: #my curl test throws error when the main report is running
                agg_html_files = sorted(agg_html_files)
                html_files = sorted(html_files) #sort list alphabetically
                #html_files.insert(0,html_files.pop(html_files.index("current_data.html"))) #move to beginning of list
                #html_files.pop(html_files.index("{1}_current_data.html".format(i[1]))) #remove from list as I put it as a button on page
                html_files.append(html_files.pop(html_files.index("{0}_non_error_pos_data.html".format(i[2])))) #move to end of list
            except:
                print("cannot process files as report is being ran")
            title = "{0} Reports".format(i[2])
            description = "Find mis-booked POS items for {0}".format(i[2])
            pageType = 'test'            
            return render_template('report_page.html', title=title, description=description, pageType=pageType,recent=recent_date,least_recent=least_recent_date,files=html_files,aggfiles=agg_html_files,current_filename=current_filename)

    return "Could not find page"


@app.route('/reports/<SL1_page>/<SL2_page>/<SL3_page>/<SL4_page>')
def SL4_reports(SL1_page,SL2_page,SL3_page,SL4_page):
    
    global report_runtime, recent_date, least_recent_date, op_list1
    html_files = []
    agg_html_files = []
    #make sure the update doesn't get ran everytime the page is loaded
    curr_time = int(time.time())
    if curr_time - report_runtime > 500:
        report_runtime = curr_time
        recent_date,least_recent_date = get_time_frame(all_data_csv_filename)

    page = "{0}/{1}/{2}/{3}".format(SL1_page,SL2_page,SL3_page,SL4_page)
    #print("We made it here")
    #print("We got globals"+str(op_list1))
    #print("page we are looking for: "+page)
    for i in op_list1:
        page_list_SL4 = "{0}/{1}/{2}/{3}".format(i[0],i[1],i[2],i[3])
        #print("iteration : "+page_list_SL4)

        if page==page_list_SL4:
            for file in glob.glob(filtered_filepath + '/*.[Hh][Tt][Mm][Ll]'):
                filename = os.path.basename(file)
                if "{0}_aggressive".format(i[3]) in filename:
                    agg_html_files.append(filename)     
                elif "{0}_current".format(i[3]) in filename:
                    current_filename = filename                
                elif "{0}".format(i[3]) in filename:
                    html_files.append(filename)
            try: #my curl test throws error when the main report is running
                agg_html_files = sorted(agg_html_files)
                html_files = sorted(html_files) #sort list alphabetically
                #html_files.insert(0,html_files.pop(html_files.index("current_data.html"))) #move to beginning of list
                #html_files.pop(html_files.index("{1}_current_data.html".format(i[1]))) #remove from list as I put it as a button on page
                html_files.append(html_files.pop(html_files.index("{0}_non_error_pos_data.html".format(i[3])))) #move to end of list
            except:
                print("cannot process files as report is being ran")
            title = "{0} Reports".format(i[3])
            description = "Find mis-booked POS items for {0}".format(i[3])
            pageType = 'test'            
            return render_template('report_page.html', title=title, description=description, pageType=pageType,recent=recent_date,least_recent=least_recent_date,files=html_files,aggfiles=agg_html_files,current_filename=current_filename)

    return "Could not find page"



#currently not using this, used to send MBR data on click, replaced it with email capabilities via jquery
@app.route('/current_data.html',methods=['POST'])
def get_my_data():
    POS = int(request.form['pos_value'])
    #print(POS)
    #print(type(POS))

    #####from other scripts
    results_pos_list = []
    results_pos_pid_list = []
    file_list = [non_error_pos_data_filename,all_data_csv_filename] 
    return_string = ''

    print("#########################  FROM POS REPORT  ###############################")
    print('{:^25}{:^25}{:^25}{:^25}{:^25}{:^25}{:^25}'.format('POS ID',"Posted Date",'Product ID','Value',"End Customer","Party ID","Salesrep Name"))

    for file in file_list:
        df = pd.read_csv(file)
        for row in df[df["POS ID"] == POS].itertuples():
            #print(str(row))
            
            print('{:^25}{:^25}{:^25}{:^25}{:^25}{:^25}{:^25}'.format(str(row[1]),str(row[2]),str(row[6]),str(row[7]),str(row[5]),str(row[10]),str(row[4])))
            results_pos_list.append(row[10]) 
            results_pos_pid_list.append(str(row[6])) 

    mbr_file = max(glob.iglob(mbr_filepath + '*.[Cc][Ss][Vv]'), key=os.path.getctime)
    df_mbr = pd.read_csv(mbr_file, usecols=["Sales Order Number","End Customer Company Name","Transaction Date","Total Bookings","Sales Agent Name","Product ID","Branch Party ID"]) #.set_index("Branch Party ID")              
    
    results_mbr = df_mbr[(df_mbr["Branch Party ID"].isin(results_pos_list)) & (df_mbr["Product ID"].isin(results_pos_pid_list))]


    print("\n#########################  FROM MBR  ###############################")
    return_string = return_string + "    FROM MBR    \n"
    
    print('{:^25}{:^25}{:^25}{:^25}{:^25}'.format('SO#','Posted Date',"Product ID",'Total Bookings',"End Customer"))
    return_string = return_string + '{:^25}{:^25}{:^25}{:^25}{:^25}'.format('SO#','Posted Date',"Product ID",'Total Bookings',"End Customer") + '\n'
    for row in results_mbr.itertuples():
        print('{:^25}{:^25}{:^25}{:^25}{:^25}'.format(str(row[1]),str(row[3]),str(row[6]),str(row[4]),str(row[2])))
        return_string = return_string + '{:^25}{:^25}{:^25}{:^25}{:^25}'.format(str(row[1]),str(row[3]),str(row[6]),str(row[4]),str(row[2])) + '\n'

    #return json.dumps({'value': int(my_data)})
    return return_string

#contains some CSS code  in html file that I refer too sometimes
@app.route('/test4')
def test4():
    global report_runtime, recent_date, least_recent_date
    #make sure the update doesn't get ran everytime the page is loaded
    curr_time = int(time.time())
    if curr_time - report_runtime > 500:
        report_runtime = curr_time
        recent_date,least_recent_date = get_time_frame(all_data_csv_filename)
        #print("report date was updated")
    
    title = "POS Tool Test4"
    description = "Not that kind of POS"
    pageType = 'test'    
    return render_template("test4.html", title=title, description=description, pageType=pageType,recent=recent_date,least_recent=least_recent_date)


#if you click a link with the path of /SWSO/whatever it will just return any file of same name
#I use this so I can build the links dynamic from files in filteredPOS and still serve them from flask
@app.route('/files/<path:path>')
def files(path):
    return send_from_directory(home_file_path+'/filteredPOS/',path)


#main tool for AMs to update their account list
@app.route('/amlist',methods=['GET','POST'])
def amlist():
    global am_list_json #JSON in memory so I don't have to load from the file everytime
    #global currentlyProcessingReports
    #print (currentlyProcessingReports)


    #print("made it to main.py amlist GET")
    if request.method=='POST': #if one of the forms is submitted
        currentlyProcessingReports = getCurrentlyProcessingReportsGlobal()
        if currentlyProcessingReports == "1":
            print("currently running a report\n\n")
            #return "Another user is currently running a report, please try again soon"
            return jsonify({"status":"Another user is currently running a report, please try again soon"})

        #print("made it to main.py amlist POST")
        if request.form['function'] == 'accountAction':
            #print("Made it to python accountAction function")
            #print("Account to be added: "+request.form['account'])
            #print("AM list to modify: "+request.form['email'])
            #send the email and account to be added/removed, it will write to json, load new json into global var, and return
            am_list_json = update_single_am_account_list(request.form['email'],request.form['account'],request.form['action'])
            for v in am_list_json.values():
                if v["email"] == request.form['email']:
                    return jsonify({"accounts":v["accounts"]})
            else:
                return jsonify({"status":"Can't find that email"})            
        elif request.form['function'] == 'searchForm':
            print("Searching accounts for: "+request.form['email'])
            if request.form['email'] == 'test case': #to test the timeout of 10 seconds
                time.sleep(11)
            for v in am_list_json.values():
                if v["email"] == request.form['email']:
                    return jsonify({"accounts":v["accounts"]})
            else:
                return jsonify({"status":"Can't find that email"})
                
        elif request.form['function'] == 'runReport':
            #print("made it to runReport")
            status = update_single_am_results(request.form['email'],all_data_csv_filename)
            #return status
            return jsonify({"status":status})
        #return app.response_class(data, content_type='application/json')
    title = "AM Account List Tool "
    description = "Displays your account search list, and might one day allow you to modify"
    pageType = 'test'    
    return render_template("amlist.html", title=title, description=description, pageType=pageType)    

@app.route('/aggsearch',methods=['GET','POST'])
def aggsearch():
    #print("made it to main.py aggsearch GET")
    if request.method=='POST':
        currentlyProcessingReports = getCurrentlyProcessingReportsGlobal()
        if currentlyProcessingReports == "1":
            print("currently running a report")
            return jsonify({"status":"Another user is currently running a report, please try again soon"})

        if request.form['function'] == 'aggSearchForm':
            #print("Made it to python aggSearchForm function")
            #print("AM accounts to search: "+request.form['email'])
            status = create_aggressive_search_csv_for_am(request.form['email'],'3')
            return jsonify({"status":status})

    title = "AM Aggresive Search Tool "
    description = "Find potential misspelled accounts in the POS report"
    pageType = 'test'    
    return render_template("aggsearch.html", title=title, description=description, pageType=pageType)  


#admin tool
@app.route('/posadmin',methods=['GET','POST'])
def posadmin():

    if request.method=='POST': #if one of the forms is submitted
        currentlyProcessingReports = getCurrentlyProcessingReportsGlobal()
        if currentlyProcessingReports == "1":
            print("currently running a report\n\n")
            #return "Another user is currently running a report, please try again soon"
            return jsonify({"status":"Another user is currently running a report, please try again soon"})

        #print("made it to main.py amlist POST")
        if request.form['function'] == 'adminViewLogs':
            #send the email and account to be added/removed, it will write to json, load new json into global var, and return
            status = display_logs()
            return jsonify({"status":status})
        elif request.form['function'] == 'adminRunAll':
            #print("made it to runReport")
            if request.form['secret'] == POS_ADMIN_TOKEN: #super secret password!         
                os.system('/usr/bin/python3 '+home_file_path+'POS_filter.py test')
                status = "Report is done"
                return jsonify({"status":status})
            else:
                status = "Wrong Password"
                return jsonify({"status":status})                
        #return app.response_class(data, content_type='application/json')
    title = "Admin tool "
    description = "Run all reports and view logs"
    pageType = 'test'    
    return render_template("posadmin.html", title=title, description=description, pageType=pageType)    


#RealTimeSearch
@app.route('/realtime',methods=['GET','POST'])
def realtime():

    if request.method=='POST': #if one of the forms is submitted
        currentlyProcessingReports = getCurrentlyProcessingReportsGlobal()
        if currentlyProcessingReports == "1":
            print("currently running a report\n\n")
            #return "Another user is currently running a report, please try again soon"
            return jsonify({"status":"Another user is currently running a report, please try again soon"})

        #print("made it to main.py amlist POST")
        if request.form['function'] == 'realTimeSearch':
            #send the email and account to be added/removed, it will write to json, load new json into global var, and return
            status = real_time_search(request.form['account'],request.form['email'],request.form['pos'],request.form['party'],request.form['searchAction'])
            return jsonify(status)
            #return searchResult        
        #return app.response_class(data, content_type='application/json')
    title = "Real Time Search"
    description = "Search every POS file in real time"
    pageType = 'test'    
    return render_template("realtime.html", title=title, description=description, pageType=pageType)    


@app.route('/realtimesearch/<path:path>')
def realtimepath(path):
    return send_from_directory(real_time_search_file_path,path)


if __name__ == "__main__":
    am_list_json = flask_load_json_to_mem(am_list_json_filename) #load json into memory
    #app.run(host='0.0.0.0',debug=True)
    app.run(host='0.0.0.0',threaded=True, port=5000)