git init .
git add .
git rm --cached -r -f .idea
git commit -m  "commit %time%,%date%"
git remote add origin https://github.com/nagasitaramthigulla/sanvi-bot-django.git
git push -u origin master
