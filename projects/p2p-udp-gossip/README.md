# P2P UDP Gossip

Run two local peers that exchange JSON messages directly over UDP.

This is a small learning project for peer identity, datagram transport, duplicate detection,
and why production P2P systems add NAT traversal, encryption, discovery, and backpressure.

## Run

```bash
node projects/p2p-udp-gossip/peer.test.mjs
node projects/p2p-udp-gossip/peer.mjs
```

The demo binds random localhost ports, sends a message both ways, prints the received
messages, and closes the sockets.
