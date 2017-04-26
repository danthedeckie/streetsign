#!/bin/sh
###############################################
# Kiosk Setup Script for Raspberry pi (basic)
###############################################

URL='https://streetsign.org.uk/'

# Set up Simple Redirecter (nicer errors if it cannot connect,
# auto reconnecting, etc.)

cd /tmp/
git clone https://bitbucket.org/dfairhead/simple-redirect-server.git
cd simple-redirect-server
cp simple_redirect.py /usr/local/bin/
chmod +x /usr/local/bin/simple_redirect.py

echo '[server]' > /boot/redirect.conf
echo "redirect_to_url=$URL" >> /boot/redirect.conf

cd ..
rm -rf simple-redirect-server

# set up pi user:

echo '@lxpanel --profile LXDE-pi' > /home/pi/.config/lxsession/LXDE-pi/autostart
echo '@/usr/local/bin/simple_redirect.py /boot/redirect.conf' >> /home/pi/.config/lxsession/LXDE-pi/autostart
echo '@/usr/local/bin/kiosk.sh' >> /home/pi/.config/lxsession/LXDE-pi/autostart

sed -e 's/autohide=0/autohide=1/' -i /home/pi/.config/lxpanel/LXDE-pi/panels/panel

# and let's move a few common networking files to /boot for easier access:

mv /etc/network/interfaces /boot/network_interfaces
ln -s /boot/network_interfaces /etc/network/interfaces

mv /etc/wpa_supplicant/wpa_supplicant.conf /boot/wpa_supplicant.conf
ln -s /boot/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf

cat > /usr/local/bin/kiosk.sh << EOF
#!/bin/sh

xset s off # no screensaver
xset -dpms # no display power saving
xset s noblank # no screensaver blanking
unclutter & # hide the mousepointer

chromium-browser --start-fullscreen --bwsi --disable-extensions --disable-default-apps --app='http://localhost:8080/'
EOF
chmod +x /usr/local/bin/kiosk.sh
