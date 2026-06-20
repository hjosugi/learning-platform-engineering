import assert from "node:assert/strict";
import { GossipPeer, waitFor } from "./peer.mjs";

const alice = new GossipPeer("alice");
const bob = new GossipPeer("bob");

await alice.start();
await bob.start();

try {
  const sent = await alice.send(bob.port(), { topic: "hello", value: 1 });
  await waitFor(() => bob.received.length === 1);

  assert.equal(bob.received[0].id, sent.id);
  assert.equal(bob.received[0].from, "alice");
  assert.deepEqual(bob.received[0].body, { topic: "hello", value: 1 });
  console.log("ok");
} finally {
  alice.close();
  bob.close();
}
