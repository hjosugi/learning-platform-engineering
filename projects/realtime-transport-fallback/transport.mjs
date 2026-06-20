export function detectCapabilities(scope = globalThis) {
  return {
    secureContext: Boolean(scope.isSecureContext),
    webTransport: typeof scope.WebTransport === "function",
    webSocket: typeof scope.WebSocket === "function",
    eventSource: typeof scope.EventSource === "function",
  };
}

export function chooseTransport(capabilities = detectCapabilities()) {
  if (capabilities.webTransport && capabilities.secureContext) {
    return {
      name: "webtransport",
      reason: "HTTP/3-capable bidirectional streams and datagrams are available.",
    };
  }

  if (capabilities.webSocket) {
    return {
      name: "websocket",
      reason: capabilities.webTransport
        ? "WebTransport exists, but the current context is not secure."
        : "WebSocket is the broadest bidirectional realtime fallback.",
    };
  }

  if (capabilities.eventSource) {
    return {
      name: "sse",
      reason: "Only server-to-client streaming is available.",
    };
  }

  return {
    name: "long-polling",
    reason: "No native realtime transport was detected.",
  };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const capabilities = detectCapabilities(globalThis);
  console.log(JSON.stringify({ capabilities, decision: chooseTransport(capabilities) }, null, 2));
}
