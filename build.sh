#DEPLOY=/var/www/django
REPO=/var/git/mad-man
echo "[madman] Deploying $REPO"
mysql -uroot -pttoorr -hlocalhost --execute="drop database IF EXISTS madmanDjango; create database madmanDjango;"

python $REPO/mysite/manage.py syncdb

echo "[madman] Converting database tables to utf8"
python $REPO/scripts/fix_mysql.py 
echo "[madman] Installing madman"
python $REPO/mysite/manage.py minstall
echo "[madman] Build complete."
