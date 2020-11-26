sudo chmod 755 /home/pi/Battery/omxiv-battery
sudo apt install python-smbus
sudo sed -i '/Battery.py/d' /opt/retropie/configs/all/autostart.sh
sudo sed -i '1i\\/usr/bin/python /home/pi/Battery/Battery.py &' /opt/retropie/configs/all/autostart.sh

echo
echo "Setup Completed. Reboot after 3 Seconds."
sleep 3
reboot
