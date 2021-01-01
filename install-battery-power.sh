sudo apt install python3-smbus -y

rm -rf /opt/retropie/configs/all/PowerUtils/
mkdir /opt/retropie/configs/all/PowerUtils/
cp -f -r ./PowerUtils /opt/retropie/configs/all/

sudo chmod 755 /opt/retropie/configs/all/PowerUtils/omxiv-battery
sudo sed -i '/Battery.py/d' /opt/retropie/configs/all/autostart.sh
sudo sed -i '/PowerUtils/d' /opt/retropie/configs/all/autostart.sh
sudo sed -i '1i\\sudo /usr/bin/python3  /opt/retropie/configs/all/PowerUtils/BatteryPower.py &' /opt/retropie/configs/all/autostart.sh

echo
echo "Setup Completed. Reboot after 3 Seconds."
sleep 3
reboot
