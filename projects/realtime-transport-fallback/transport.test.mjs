import assert from "node:assert/strict";
import { chooseTransport } from "./transport.mjs";

assert.equal(
  chooseTransport({
    secureContext: true,
    webTransport: true,
    webSocket: true,
    eventSource: true,
  }).name,
  "webtransport",
);

assert.equal(
  chooseTransport({
    secureContext: false,
    webTransport: true,
    webSocket: true,
    eventSource: true,
  }).name,
  "websocket",
);

assert.equal(
  chooseTransport({
    secureContext: false,
    webTransport: false,
    webSocket: false,
    eventSource: true,
  }).name,
  "sse",
);

assert.equal(
  chooseTransport({
    secureContext: false,
    webTransport: false,
    webSocket: false,
    eventSource: false,
  }).name,
  "long-polling",
);

console.log("ok");
