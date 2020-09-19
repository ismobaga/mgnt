# Docker deployer

##  Setup
### Build
```
pyinstaller --clean --onefile  --exclude-module numpy  --name docker-deployer deploy.py

```
### Run 

Supported default filenames: `mgnt.yml`, `mgnt.yaml` `mgnt.json`

```
./docker-deployer up # default config file will be use or 
./docker-deployer -f path/to/config.yml

```
### Run on Startup
Copy `docker-deployer.service` into `/etc/systemd/system`

Start with
```
systemctl start docker-deployer.service
```
To start this service when startup, run systemctl enable `docker-deployer.service` only once.

> Edit the `docker-deployer.service` if needed.




## Requirements
```
pip install docker pyinstaller
```