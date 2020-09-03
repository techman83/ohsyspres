# Openhab Syslog Presence
A highly overengineered, extensible project for listening to syslog events, parsing out device ids, and updating OpenHAB items.

## Rational
After getting frustrated that Google Routines (Ok Google, you already know I'm #@%$ing home!) still required me to vocally announce my presence and MikroTik scirpting not quite as responsive as I'd like (you can poll the logs with a schedule), I figured I could write a syslog listener and got entirely carried away.

## Installation
```bash
git clone https://blah
pip3 install blah/.
```

## Running
```bash
ohsyspres --openhab-url http://openhab2.hostname/ -w 'DA:7E:63:A1:97:5D' My_Phone_Item -w '728E05701B2D' Other_House_Member
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
