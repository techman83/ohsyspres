# Openhab Syslog Presence
A highly overengineered, extensible project for listening to syslog events, parsing out device ids, and updating OpenHAB items.

## Rational
After getting frustrated that Google Routines (Ok Google, you already know I'm #@%$ing home!) still required me to vocally announce my presence and MikroTik scirpting not quite as responsive as I'd like (you can poll the logs with a schedule), I figured I could write a syslog listener and got entirely carried away.

## Installation
```bash
git clone https://github.com/techman83/ohsyspres.git
pip3 install ohsyspres/.
ohsyspres --help
Usage: ohsyspres [OPTIONS]

Options:
  --host TEXT                     IP to advertise on, default 0.0.0.0
  --port INTEGER                  Port to listen on, default 1514
  --openhab-url TEXT              URL for OpenHAB  [required]
  --router-host TEXT              Router ip for guest count lookup
  --router-creds <TEXT TEXT>...   Username Password for router, Scoped Read
                                  Only account recommended,export
                                  ROUTER_CREDS="username reallygoodropassword

  -w, --watch-device DEVICE...    devices to watch/item names. ie -w
                                  846969F9D00F Phone -w 07559D07C215 Laptop

  --append-network                Append Wifi Network to item, ie Phone_MyWiFi
  -i, --ignore-device MACADDRESS  Devices to ignore. ie -i 846969F9D01F
  -g, --guest-network TEXT        Guest networks for simple device counts
  --debug                         Enable debug logging
  --log-file FILE                 Path to log file
  --help                          Show this message and exit.
```

## Running
```bash
ohsyspres --openhab-url http://openhab2.hostname/ -w 'DA:7E:63:A1:97:5D' My_Phone_Item -w '728E05701B2D' Other_House_Member
[2020-09-03 17:31:51,358] [INFO    ] 'da7e63a1975d' updated 'My_Phone_Item' with state 'ON'
[2020-09-03 17:31:51,358] [INFO    ] 'da7e63a1975d' updated 'My_Phone_Item' with state 'OFF'
[2020-09-03 17:32:16,058] [INFO    ] '728e05701b2d' updated 'Other_House_Member' with state 'ON'
```

## SystemD
Sample service file for startup via systemd - `/etc/systemd/system/ohsyspres.service`
```
[Unit]
Description=ohsyspres - OpenHAB Syslog Presence Service
After=syslog.target network.target

[Service]
Type=simple
User=leon
WorkingDirectory=/usr/local/ohsyspres
ExecStart=/usr/local/ohsyspres/venv/bin/python /usr/local/ohsyspres/venv/bin/ohsyspres --openhab-url http://openhab/ -w 'DA:7E:63:A1:97:5D' My_Phone_Item -w '728E05701B2D' Other_House_Member --log-file /var/log/ohsyspres/ohsyspres.log
Restart=on-abort

[Install]
WantedBy=multi-user.target
```

## Syslog
Whilst only MikroTik endpoints are currently supported, with a little work this could be expanded and has been written with that in mind.

### Configure MikroTik Logging to Syslog Endpoint
Tested on 6.47.x
```
/system logging action
add bsd-syslog=no name=automation remote=<HOST IP HERE> remote-port=1514 src-address=0.0.0.0 syslog-facility=daemon syslog-severity=auto syslog-time-format=bsd-syslog target=remote
/system logging
add action=automation disabled=no prefix="" topics=wireless
```

## Example Openhab 2 Config

### Items
```
Group DevicePresence
Switch My_Phone_Item        "My Phone"  (DevicePresence)
Switch Other_House_Member   "Other House Member's Phone"  (DevicePresence)
Switch H_Occupied           "House Occupied"
Switch H_Empty              "House Empty"    { expire="5m,state=OFF" }
```

### Rules
```java
rule "DeviceConnected"
when
    Member of DevicePresence changed to ON
then
    H_Occupied.sendCommand(ON)
    logInfo("rules", "House Occupied, triggered by '{}'", triggeringItem.label)
end

rule "DeviceDisconnected"
when
    Member of DevicePresence changed to OFF
then
    var boolean present = false
    DevicePresence.members.forEach[
        i | if (i.state == ON) {
            present = true

        }
    ]
    if (present !== true) {
        logInfo("rules", "Last device left, setting empty timer, triggered by '{}'", triggeringItem.label)
        H_Empty.sendCommand(ON)
    }
end

rule "EmptyCheck"
when
    Item H_Empty changed to OFF
then
    var boolean present = false
    DevicePresence.members.forEach[
        i | if (i.state == ON) {
            present = true

        }
    ]
    if (present !== true) {
        logInfo("rules", "House Empty, setting unoccupied")
        H_Occupied.sendCommand(OFF)
    }
end

rule "HouseOccupied"
when
    Item H_Occupied changed to ON
then
    if (IsItDark.state == ON) {
        logInfo("rules", "I'm home, it's dark, turn the lights on!")
        Lights_Power.sendCommand(ON)
    }
end

rule "HouseUnoccupied"
when
    Item H_Occupied changed to OFF
then
    logInfo("rules", "Well I've left, no sense leaving these on!")
    Lights_Power.sendCommand(OFF)
end
```
