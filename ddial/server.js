#!/usr/bin/env node

/**
 * DDial Server - Modern TCP Implementation of the Classic Chat System
 * 
 * Inspired by the original DDial system by Bill Basham (early 1980s)
 * Official site: https://www.ddial.com
 */

const net = require('net');

class SubChannel {
  constructor(number) {
    this.number = number;
    this.clients = [];
    this.isPublic = false;
    this.locked = false;
    this.topic = '';
  }
}

class Line {
  constructor(number) {
    this.number = number;
    this.clients = [];
    this.subChannels = new Map();
    this.isLocked = false;
    this.isBusy = false;
  }
}

class DDialSystem {
  constructor(totalLines) {
    this.totalLines = totalLines || 50;
    this.lines = new Map();
    this.sysop = null;
    this.sysopHandle = 'System';
    this.welcomeMessage = 'Welcome to DDial';
    
    for (let i = 1; i <= this.totalLines; i++) {
      this.lines.set(i, new Line(i));
    }
    
    this.globalChannel = new SubChannel(0);
    this.globalChannel.isPublic = true;
  }

  getNextAvailableLine() {
    for (let i = 1; i <= this.totalLines; i++) {
      const line = this.lines.get(i);
      if (line.clients.length === 0) {
        return line;
      }
    }
    return null;
  }

  assignLine(socket, state) {
    const line = this.getNextAvailableLine();
    if (!line) return null;
    
    state.line = line.number;
    state.subChannel = 0;
    line.clients.push(socket);
    line.isBusy = true;
    
    this.broadcast(line, 'Line ' + line.number + ' assigned to ' + (state.handle || socket.remoteAddress));
    return line;
  }

  removeClient(state) {
    if (state.line) {
      const line = this.lines.get(state.line);
      const index = line.clients.findIndex(s => s === state.socket);
      if (index !== -1) {
        line.clients.splice(index, 1);
        if (line.clients.length === 0) {
          line.isBusy = false;
        }
      }
      if (state.subChannel && state.subChannel > 0) {
        this.removeFromSubchannel(state);
      }
    }
  }

  joinSubchannel(state, channelNum) {
    if (channelNum < 1 || channelNum > 999) return null;
    
    const line = this.lines.get(state.line);
    if (!line.subChannels.has(channelNum)) {
      line.subChannels.set(channelNum, new SubChannel(channelNum));
    }
    
    const channel = line.subChannels.get(channelNum);
    channel.clients.push(state.socket);
    state.subChannel = channelNum;
    return channel;
  }

  removeFromSubchannel(state) {
    if (!state.subChannel) return;
    const line = this.lines.get(state.line);
    if (line.subChannels.has(state.subChannel)) {
      const channel = line.subChannels.get(state.subChannel);
      const index = channel.clients.indexOf(state.socket);
      if (index !== -1) {
        channel.clients.splice(index, 1);
      }
    }
    state.subChannel = null;
  }

  broadcast(line, message) {
    line.clients.forEach(client => {
      if (client && !client.destroyed) {
        client.write(message + '\n');
      }
    });
  }

  broadcastToChannel(lineNum, subchannelNum, message) {
    const line = this.lines.get(lineNum);
    if (!line || !line.subChannels.has(subchannelNum)) return;
    const channel = line.subChannels.get(subchannelNum);
    channel.clients.forEach(client => {
      if (client && !client.destroyed) {
        client.write(message + '\n');
      }
    });
  }

  getBusyLines() {
    let count = 0;
    for (let i = 1; i <= this.totalLines; i++) {
      if (this.lines.get(i).isBusy) count++;
    }
    return count;
  }

  getLineStats() {
    const stats = [];
    for (let i = 1; i <= this.totalLines; i++) {
      const line = this.lines.get(i);
      stats.push({
        line: i,
        busy: line.isBusy,
        clients: line.clients.length,
        channels: Array.from(line.subChannels.keys()).length
      });
    }
    return stats;
  }
}

class DDialServer {
  constructor(config) {
    this.port = config.port || 6502;
    this.ddialSystem = new DDialSystem(config.lines || 50);
    this.ddialSystem.sysop = config.sysop || 'System';
    this.ddialSystem.welcomeMessage = config.welcomeMessage || 'Welcome to DDial';
    this.server = null;
    this.connections = new Set();
    this.trafficStats = { bytesIn: 0, bytesOut: 0 };
    this.connectionLog = [];
    this.maxLogEntries = 100;
  }

  start() {
    const self = this;
    this.server = net.createServer((socket) => {
      const state = {
        line: null,
        socket: socket,
        handle: null,
        subChannel: 0,
        joinTime: Date.now()
      };
      
      self.connections.add(state);
      
      self.connectionLog.push({
        time: new Date().toISOString(),
        address: socket.remoteAddress,
        port: socket.remotePort,
        event: 'connect'
      });
      
      if (self.connectionLog.length > self.maxLogEntries) {
        self.connectionLog.shift();
      }
      
      socket.write('DDial Server - Classic Chat System\n');
      socket.write('Sysop: ' + self.ddialSystem.sysop + '\n');
      socket.write('----------------------------------------\n');
      socket.write('Welcome: ' + self.ddialSystem.welcomeMessage + '\n');
      socket.write('----------------------------------------\n');
      socket.write('Lines busy: ' + self.ddialSystem.getBusyLines() + '/' + self.ddialSystem.totalLines + '\n');
      
      const line = self.ddialSystem.assignLine(socket, state);
      
      if (line) {
        socket.write('Line ' + line.number + ' assigned.\n');
        socket.write('Enter message or /help for commands.\n');
        socket.write('Prompt> ');
      } else {
        socket.write('All lines busy. Please try later.\n');
        setTimeout(() => socket.destroy(), 1000);
        return;
      }
      
      socket.on('data', (data) => {
        self.trafficStats.bytesIn += data.length;
        const message = data.toString().replace(/\r\n?|\r/, '').trim();
        
        if (message) {
          if (message.charAt(0) === '/') {
            self.handleCommand(self, socket, state, message);
          } else if (state.subChannel > 0) {
            const timestamp = new Date().toLocaleTimeString();
            const msg = '[' + timestamp + '] ' + (state.handle || '*') + ': ' + message;
            self.ddialSystem.broadcastToChannel(state.line, state.subChannel, msg);
            socket.write(msg + '\n');
            socket.write('Prompt> ');
          } else {
            const timestamp = new Date().toLocaleTimeString();
            const msg = '[' + timestamp + '] ' + (state.handle || '*') + ': ' + message;
            const line = self.ddialSystem.lines.get(state.line);
            if (line) self.ddialSystem.broadcast(line, msg);
            socket.write(msg + '\n');
            socket.write('Prompt> ');
          }
        } else {
          socket.write('Prompt> ');
        }
      });
      
      socket.on('close', () => {
        if (state.line) {
          self.ddialSystem.removeClient(state);
          const line = self.ddialSystem.lines.get(state.line);
          if (line) self.ddialSystem.broadcast(line, 'Line ' + state.line + ' released.');
        }
        self.connections.delete(state);
      });
    });
    
    this.server.listen(this.port, () => {
      console.log('DDial Server - Classic Chat System');
      console.log('========================================');
      console.log('Listening on port: ' + this.port);
      console.log('Lines available: ' + this.ddialSystem.totalLines);
      console.log('Sysop: ' + this.ddialSystem.sysop);
      console.log('========================================');
    });
  }

  handleCommand(self, socket, state, message) {
    const command = message.split(/\s+/)[0].toLowerCase();
    const args = message.split(/\s+/).slice(1);
    
    switch (command) {
      case '/help':
      case '/h':
        socket.write('DDial Commands:\n');
        socket.write('  /t# (1-999)    - Join or create subchannel\n');
        socket.write('  /list          - List subchannels\n');
        socket.write('  /status        - Server status\n');
        socket.write('  /lines         - Line status\n');
        socket.write('  /clear         - Clear screen\n');
        socket.write('  /quit          - Disconnect\n');
        socket.write('  /help          - Show this help\n');
        break;
        
      case '/t':
        const channelNum = parseInt(args[0], 10);
        if (channelNum >= 1 && channelNum <= 999) {
          const channel = self.ddialSystem.joinSubchannel(state, channelNum);
          if (channel) {
            socket.write('Joined subchannel: ' + channel.name + '\n');
            socket.write('Subchannel ' + channelNum + '> ');
          }
        } else {
          socket.write('Usage: /t# (1-999) - Enter subchannel number\n');
        }
        break;
        
      case '/list':
        const line = self.ddialSystem.lines.get(state.line);
        const channels = Array.from(line.subChannels.keys());
        socket.write('Subchannels on line ' + state.line + ': ' + channels.join(', ') + '\n');
        break;
        
      case '/status':
        socket.write('DDial Status:\n');
        socket.write('  Sysop: ' + self.ddialSystem.sysop + '\n');
        socket.write('  Lines busy: ' + self.ddialSystem.getBusyLines() + '/' + self.ddialSystem.totalLines + '\n');
        socket.write('  Total connections: ' + self.connections.size + '\n');
        break;
        
      case '/lines':
        const stats = self.ddialSystem.getLineStats();
        const busy = stats.filter(s => s.busy);
        socket.write('Busy lines: ' + busy.map(s => 'L' + s.line).join(', ') + '\n');
        socket.write('Available: ' + (self.ddialSystem.totalLines - busy.length) + '\n');
        break;
        
      case '/clear':
        socket.write(String.fromCharCode(27) + '[2J' + String.fromCharCode(27) + '[0;0f');
        break;
        
      case '/quit':
      case '/q':
        socket.write('DDial off! Goodbye.\n');
        socket.end();
        break;
        
      default:
        socket.write('Unknown command. Type /help for options.\n');
    }
    
    if (!command.startsWith('/t')) {
      socket.write('Prompt> ');
    }
  }

  getStats() {
    return {
      server: {
        sysop: this.ddialSystem.sysop,
        listeningPort: this.port,
        totalLines: this.ddialSystem.totalLines,
        busyLines: this.ddialSystem.getBusyLines()
      },
      connections: this.connections.size,
      traffic: {
        bytesIn: this.trafficStats.bytesIn,
        bytesOut: this.trafficStats.bytesOut
      }
    };
  }
}

// Parse arguments
var config = {};
var configFile = null;

for (var i = 2; i < process.argv.length; i++) {
  switch (process.argv[i]) {
    case '--port':
      config.port = parseInt(process.argv[++i]);
      break;
    case '--lines':
      config.lines = parseInt(process.argv[++i]);
      break;
    case '--config':
      configFile = process.argv[++i];
      break;
    case '--sysop':
      config.sysop = process.argv[++i];
      break;
    case '--welcome':
      config.welcomeMessage = process.argv[++i];
      break;
    case '--help':
      console.log('DDial Server - Classic Chat System');
      console.log('========================================');
      console.log('Usage: node server.js [options]');
      console.log('\nOptions:');
      console.log('  --port <number>    TCP port to listen on (default: 6502)');
      console.log('  --lines <number>   Number of lines (default: 50)');
      console.log('  --config <file>    Configuration file path');
      console.log('  --sysop <name>     Sysop name');
      console.log('  --welcome <text>   Welcome message');
      console.log('  --help             Show help');
      process.exit(0);
  }
}

if (configFile) {
  try {
    const fs = require('fs');
    const data = JSON.parse(fs.readFileSync(configFile, 'utf8'));
    Object.assign(config, data);
  } catch (err) {
    console.log('Warning: Could not load config: ' + err.message);
  }
}

// Create and start server
var server = new DDialServer(config);
server.start();

// Handle shutdown
process.on('SIGTERM', () => {
  console.log('\nShutting down DDial server...');
  if (server.server) {
    server.server.close();
  }
  process.exit(0);
});
