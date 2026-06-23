#!/usr/bin/env node
/** Quick test for DDial server */

const net = require('net');

function test(msg, timeout, cb) {
  const socket = new net.Socket();
  
  socket.connect(6502, '127.0.0.1', () => {
    console.log('Connected!');
    if (msg) {
      socket.write(msg + '\n');
    }
  });
  
  socket.on('data', (d) => {
    process.stdout.write(d.toString());
  });
  
  socket.on('close', () => {
    if (cb) cb();
  });
  
  setTimeout(() => socket.end(), timeout);
}

console.log('Test 1: Basic connection');
console.log('========================');
test('Hello world', 1500, () => {
  console.log('\nTest 2: /help command');
  console.log('====================');
  test('/help', 1500, () => {
    console.log('\nTest 3: /status command');
    console.log('======================');
    test('/status', 1500, () => {
      console.log('\nTest 4: /lines command');
      console.log('=====================');
      test('/lines', 1500, () => {
        console.log('\nAll tests complete');
        process.exit(0);
      });
    });
  });
});
