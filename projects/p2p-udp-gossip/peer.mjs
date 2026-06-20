import dgram from "node:dgram";
import { once } from "node:events";
import { setTimeout as delay } from "node:timers/promises";

export class GossipPeer {
  constructor(name) {
    this.name = name;
    this.received = [];
    this.seen = new Set();
    this.socket = dgram.createSocket("udp4");
    this.socket.on("message", (buffer) => {
      const message = JSON.parse(buffer.toString("utf8"));
      if (this.seen.has(message.id)) {
        return;
      }
      this.seen.add(message.id);
      this.received.push(message);
    });
  }

  start(port = 0) {
    this.socket.bind({ port, address: "127.0.0.1" });
    return once(this.socket, "listening");
  }

  port() {
    return this.socket.address().port;
  }

  send(port, body) {
    const message = {
      id: `${this.name}-${Date.now()}-${Math.random().toString(16).slice(2)}`,
      from: this.name,
      body,
    };
    const payload = Buffer.from(JSON.stringify(message), "utf8");
    return new Promise((resolve, reject) => {
      this.socket.send(payload, port, "127.0.0.1", (error) => {
        if (error) {
          reject(error);
          return;
        }
        resolve(message);
      });
    });
  }

  close() {
    this.socket.close();
  }
}

export async function waitFor(predicate, timeoutMs = 1000) {
  const startedAt = Date.now();
  while (Date.now() - startedAt < timeoutMs) {
    if (predicate()) {
      return;
    }
    await delay(20);
  }
  throw new Error("condition was not met before timeout");
}

export async function demo() {
  const alice = new GossipPeer("alice");
  const bob = new GossipPeer("bob");
  await alice.start();
  await bob.start();
  try {
    await alice.send(bob.port(), { topic: "hello", value: 1 });
    await bob.send(alice.port(), { topic: "ack", value: 2 });
    await waitFor(() => alice.received.length === 1 && bob.received.length === 1);
    return { alice: alice.received, bob: bob.received };
  } finally {
    alice.close();
    bob.close();
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  console.log(JSON.stringify(await demo(), null, 2));
}
