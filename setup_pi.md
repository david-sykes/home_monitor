List of steps taken to setup Rasperry Pi

1. Change password on pi user
2. Setup wifi
3. Enable SSH in raspi-config
4. Setup SSH keys and disabled SSH password using these instrcutions: https://www.raspberrypi.org/documentation/configuration/security.md
5. `sudo pip3 install virtualenv virtualenvwrapper=='4.8.4'`
6. Add below to ~/.profile
```
VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv
export PATH=/usr/local/bin:$PATH
export WORKON_HOME=~/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
```
7. `pip install smbus2`
8. Install screen `sudo apt install screen`
9. 
To Do
- Download and analyse file
- Write temperature monitoring python
- Write Reading class to take reading and post it to endpoint
- Write temperature and air quality classes
- Write script to run reading classes one after the other
- Setup API Gateway endpoint
- Setup lambda function to write to Postgres
- Make Github repo
