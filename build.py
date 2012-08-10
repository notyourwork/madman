#!/usr/bin/env python
import os                       
import subprocess               #for calling python 
import MySQLdb
from mysite import settings     #django site settings 
from clint.textui import puts, indent, progress, colored

def init():
    global REPO 
    global host 
    global user
    global passwd
    global dbname
    global cursor 
    REPO = os.path.dirname(os.path.realpath(__file__))
    host = "localhost" 
    if settings.DATABASES['default']['HOST'] != '':
        host = settings.DATABASES['default']['HOST']
    user = settings.DATABASES['default']['USER']
    passwd = settings.DATABASES['default']['PASSWORD']
    dbname = settings.DATABASES['default']['NAME']
    db = MySQLdb.connect(
        host=host, 
        user=user, 
        passwd=passwd, 
        db=dbname
    )
    cursor = db.cursor()
    
if __name__ == "__main__":
    init()
    puts(colored.green("[madman] Deploying from %s" % REPO))
    
    #drop database and recreate 
    cursor.execute("DROP DATABASE IF EXISTS `%s`; CREATE DATABASE %s;" % (dbname, dbname))
    cursor.close()
    manage_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'mysite/manage.py'
    )
    #call manage.py syncdb  
    subprocess.call([
        'python', 
        manage_path, 
        'syncdb']
    ) 
    puts(colored.green("[madman] Converting database tables to utf8"))
    init()
    cursor.execute("ALTER DATABASE `%s` CHARACTER SET 'utf8' COLLATE 'utf8_unicode_ci'" % dbname)
    sql = "SELECT DISTINCT(table_name) FROM information_schema.columns WHERE table_schema = '%s'" % dbname
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        sql = "ALTER TABLE `%s` convert to character set DEFAULT COLLATE DEFAULT" % (row[0])
        print sql
        cursor.execute(sql)
    cursor.close()
    
    print "[madman] Installing madman"
    subprocess.call(['python', manage_path, 'minstall'])
    print "[madman] Build complete."


