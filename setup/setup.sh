# create sudo user for kris
#adduser kris
#usermod -aG sudo kris
#su - kris

# update apt
sudo apt update

# install python3 and alias python to it
sudo apt install python3
alias python=python3

# install pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo apt-get install python3-distutils
sudo python3 get-pip.py

# install python dependencies
sudo python3 -m pip install apscheduler selenium flask twilio gspread oauth2client python-telegram-bot pypath-magic

# install chromium
sudo apt-get install chromium-browser

# enable credentials storing
git config --global credential.helper store
git config --global user.email "brethower.k@gmail.com"
git config --global user.name "brethower-k"

# clone repo
git clone https://github.com/brethower-k/nu-crushes-autoposter.git
cd nu-crushes-autoposter

# download ngrok to bin folder
mkdir bin
cd bin
curl https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip --output "ngrok.zip"
sudo apt install unzip
unzip ngrok.zip
rm ngrok.zip
cd ..
# this is the auth token for nucrushesofficial@gmail.com
./bin/ngrok authtoken 1YkeUEQQSfmbnXwRAp4tWiWDSxz_6oZk2j7J2beg5sk4QeJjY

# set permissions on file as executable
chmod +x app.py

# set timezone to new york
sudo timedatectl set-timezone America/New_York

# set top level pypath
sudo pypath add .

# run file in background
tmux
python3 app.py
# to exit without closing the process, press CTRL+B, then D
# to scroll through previous lines, press CTRL+B then [
# next time you want to join, run 'tmux attach'
