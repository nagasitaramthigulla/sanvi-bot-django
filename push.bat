@echo off
git init .
git add .
git commit -m  "commit %time%,%date%"
git rm  --cached SaanviDashboard -r
git rm --cached .idea -r
git remote add -m origin qnaforum https://github.com/nagasitaramthigulla/sanvi-bot-django.git
git push -u origin master
