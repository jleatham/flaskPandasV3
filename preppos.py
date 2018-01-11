import os

#port = '5001'
directory = "/home/cisco/houston-pos-v3/"
version = '3' # main vs main2 etc, for main.py use ''

try:
    os.system("cd "+directory+" && git pull")
    os.system("kill $(ps aux | grep '[s]cheduler"+version+".py' | awk '{print $2}')")
    os.system("kill $(ps aux | grep '[m]ain"+version+".py' | awk '{print $2}')")
	#think this messes up the logs
	#os.system('nohup /usr/bin/python3 -u /home/cisco/houston-pos/scheduler.py >> /home/cisco/houston-pos/pos_log.out &')

except:
    print("something went wrong")