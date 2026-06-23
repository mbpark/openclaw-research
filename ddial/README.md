# DDial Server - Classic Chat System

Modern TCP/IP implementation of the classic DDIAD/STS/Dial chat system, created by Bill Basham in the early 1980s.

**Official DDial Community:** https://www.ddial.com

---

## History

DDial has been running continuously for over 40 years - one of the oldest online systems still active today with 8+ people connected right now.

### Timeline

| Year | Event |
|------|-------|
| Early 1980s | Created by Bill Basham, ran on Apple //e with 7 AppleCAT modems at 300 baud |
| 1980s-1990s | Golden age with 100+ systems across North America |
| Late 1980s | Ported to IBM as "Synergy" or **STS** |
| 2000s | Ported to UNIX as ENTchat, continued on internet |
| 2006 | RMAC BBS system started, still running today |
| 2008 | Mouse #059 emulates AppleCAT modems on Linux |
| 2010s | Facebook groups reconnect old DDial users |
| 2022 | Web DDial++ (Magviz) launched - modernizing the system |
| 2024-2026 | 12+ active platforms, still growing |

## Current Active Platforms (from https://www.ddial.com)

| Platform | Type | Sysop |
|----------|------|-------|
| Magviz | Web | James Quick |
| Land of the Lost | Telnet | Winter |
| Phosphor.chat | Web | MerZz |
| The Jungle | Telnet/Web | Marc |
| ENTchat | Telnet/Web | DaveZX |
| RetroDial systems | Telnet/Web | Various |
| Carriersync | Telnet/Web | - |
| DigitalDial | Telnet/Web | SwitchBlade |
| IRC #ddial channel | IRC | - |

### Telnet Systems

```
Land of the Lost:  telnet landofthelost.ca 2300   # Uses Primal Chat interface
The Jungle:        telnet junglebbs.com           # Original Jungle STS (16 lines!)
Carriersync:       telnet rdial.carriersync.com:2300
DigitalDial:       telnet digitaldial.homeunix.com:2300
```

## Protocol

- Client connects, gets auto-assigned first available line (1-50)
- Chat messages broadcast to line
- `/t# (1-999)` joins/creates subchannels (private/public)
- Multiple users per line in standard mode
- Commands start with `/`

---

## Installation

```bash
cd workspace/ddial
```

## Quick Start

```bash
# Start server (50 lines by default)
node server.js

# Start with custom options
node server.js --port 6502 --lines 50 --sysop "YourName" --welcome "Welcome message"

# Connect with telnet client
node client.js 127.0.0.1 6502

# Or connect to remote DDial systems
node client.js landofthelost.ca 2300   # Land of the Lost
node client.js junglebbs.com 23         # The Jungle
```

## DDial Commands

```
/message       Send message to current line
/t# (1-999)   Join or create subchannel
/list         List subchannels on line
/status       Show server status
/lines        Show line status
/clear        Clear screen
/quit         Disconnect
/help         Show help
```

## Configuration

```json
{
  "port": 6502,
  "lines": 50,
  "sysop": "System",
  "welcomeMessage": "Welcome to DDial"
}
```

## Project Structure

```
ddial/
├── server.js           # DDial chat server
├── client.js           # Telnet client
├── config-example.json # Sample configuration
├── test.js             # Test script
└── README.md           # Documentation
```

## References

- **Official DDIAD:** https://www.ddial.com
- **Magviz Web:** https://www.magviz.ca
- **Station Instructions:** http://www.300bps.com/text/DIALINST.TXT
