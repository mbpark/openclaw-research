#!/usr/bin/env node

/**
 * DDial Client - Connect to DDial server and systems
 * 
 * Usage: node client.js <host> <port>
 *
 * Commands:
 *   Enter message    - Send to current line/channel
 *   /t# (1-999)      - Join or create subchannel
 *   /list             - List subchannels
 *   /status           - Server status
 *   /lines            - Line status
 *   /clear            - Clear screen
 *   /quit             - Disconnect
 *   /help             - Show help
 *
 * DDial Systems from https://www.ddial.com:
 *   Land of the Lost:  landofthelost.ca :2300
 *   The Jungle:        junglebbs.com :23
 *   Carriersync:       rdial.carriersync.com :2300
 *   DigitalDial:       digitaldial.homeunix.com :2300
 */

const net = require('net');
const readline = require('readline');

class DDialClient {
  constructor(host, port) {
    this.host = host;
    this.port = port;
    this.socket = null;
    this.rl = null;
  }

  connect() {
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    console.log('DDial Client');
    console.log('Connecting to ' + this.host + ':' + this.port + '...');

    this.socket = net.createConnection(this.port, this.host, () => {
      console.log('Connected.\n');
      this.prompt();
    });

    this.socket.on('data', (data) => {
      process.stdout.write(data.toString());
    });

    this.socket.on('error', (err) => {
      console.error('Connection error: ' + err.message);
      this.disconnect();
    });

    this.socket.on('close', () => {
      console.log('Connection closed.');
      this.disconnect();
      process.exit(0);
    });
  }

  prompt() {
    this.rl.question('Prompt> ', (input) => {
      this.socket.write(input.trim() + '\n');
      this.prompt();
    });
  }

  disconnect() {
    if (this.socket) this.socket.end();
    if (this.rl) this.rl.close();
  }
}

// Parse args
const args = process.argv.slice(2);

if (args.length < 2 || args[0] === '--help' || args[0] === '-h') {
  console.log('DDial Client - Connect to DDial systems');
  console.log('');
  console.log('Usage: node client.js <host> <port>');
  console.log('');
  console.log('DDial Systems:');
  console.log('  node client.js 127.0.0.1 6502     # Local server');
  console.log('  node client.js landofthelost.ca 2300  # Land of the Lost');
  console.log('  node client.js junglebbs.com 23     # The Jungle');
  console.log('');
  process.exit(0);
}

const client = new DDialClient(args[0], parseInt(args[1]));
client.connect();
