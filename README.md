# geiriadur-xslt
Geiriadur sy'n storio data fel XML ac sy'n rhoi canlyniadau drwy XSLT / Dictionary which stores data as XML and gives results via XSLT

(h) 2026 Geiriadur Prifysgol Cymru, Canolfan Uwchefrydiau Cymreig a Cheltaidd, Prifysgol Cymru y Drindod Dewi Sant  
(c) 2026 University of Wales Dictionary, Centre for Advanced Welsh and Celtic Studies, University of Wales Trinity St David  

gan / by Dr Talat Zafar Chaudhri

### Fersiwn / Version 0.1

### Gweler / See release_notes_v0.1.txt

### Dibyniaethau / Dependencies:

#### Gweinydd / Server

python3  
Flask  
gunicorn  
ProxyFix  

subprocess  
globals  
lxml  
urllib  
os  
sys  
re  
unicodedata  
yaml  

#### Rhaglen We / Web Application

  dim / none

### Disgrifiad / Description

Mae'r rhaglen hon yn eiriadur sy'n storio data fel XML ac sy'n rhoi canlyniadau drwy XSLT.

This program is a dictionary which stores data as XML and gives results via XSLT.

### systemd ###

/etc/systemd/system/geiriadur.service

```
[Unit]
Description=Welsh Dictionary

[Service]
ExecStart=/srv/<web_root_here>/geiriadur.sh
;ExecStart=/var/www/<web_root_here>/geiriadur.sh

User=www-data
Group=www-data

[Install]
WantedBy=multi-user.target
```

```
sudo systemctl daemon-reload
sudo systemctl enable geiriadur.service
sudo systemctl start geiriadur.service
sudo systemctl status geiriadur.service
```

### nginx ###

```
# Support Clean (aka Search Engine Friendly) URLs
location / {
    try_files $uri $uri/ /index.php?$args;
    proxy_pass http://127.0.0.1:5000;  # Flask backend on port 5000
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```
