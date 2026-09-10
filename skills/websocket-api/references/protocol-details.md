# WebSocket protocol details (Tier-2 reference)

Loaded only when [SKILL.md](../SKILL.md) links here. Condensed from
[research/technologies/websocket-api.md](../../../research/technologies/websocket-api.md)
— consult that document for the full citation trail and additional
commentary.

## Handshake headers (`Sec-WebSocket-*`)

[Source: https://www.rfc-editor.org/rfc/rfc6455.html]

| Header | Direction | Purpose |
|---|---|---|
| `Upgrade: websocket` | request | Declares the protocol upgrade being requested. |
| `Connection: Upgrade` | request | Standard HTTP upgrade signal. |
| `Sec-WebSocket-Key` | request | Random 16-byte value, base64-encoded; a fresh nonce per handshake. |
| `Sec-WebSocket-Version` | request | Must be `13` for RFC-6455-conformant clients/servers. |
| `Origin` | request | Browsers always send this on WebSocket handshakes; servers should validate it as a Cross-Site WebSocket Hijacking (CSWH) mitigation — non-browser clients can forge it, so this is not a full authentication mechanism [Source: MDN Writing WebSocket servers]. |
| `Sec-WebSocket-Protocol` | request (offer) / response (selection) | Application subprotocol negotiation; the server may only select a value the client offered. |
| `Sec-WebSocket-Extensions` | request (offer) / response (selection) | Protocol extension negotiation (e.g. `permessage-deflate`); same offer/select constraint as subprotocols. |
| `Sec-WebSocket-Accept` | response | `base64(SHA-1(Sec-WebSocket-Key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"))` — proves the responder understands the WebSocket protocol rather than merely echoing an arbitrary `Upgrade`. |

**Response**: `101 Switching Protocols` on success. On failure/mismatch
(e.g. unsupported `Sec-WebSocket-Version`), MDN's recommended server pattern
is `400 Bad Request`, closing the socket immediately, and echoing the
versions the server *does* support in the `Sec-WebSocket-Version` response
header [Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers].

## Frame structure

[Source: https://www.rfc-editor.org/rfc/rfc6455.html]

Each frame carries: a `FIN` bit (last fragment of a message), 3 reserved
bits (`RSV1`-`RSV3`, used by extensions — e.g. `permessage-deflate` uses
`RSV1`), a 4-bit opcode, a `MASK` bit, a variable-length payload-length
field (7/16/64-bit forms), an optional 4-byte masking key, and the payload.

**Opcodes:** `0x0` continuation, `0x1` text, `0x2` binary, `0x8` close,
`0x9` ping, `0xA` pong; `0x3`-`0x7` and `0xB`-`0xF` are reserved.

**Masking is mandatory in one direction only**: "A client MUST mask all
frames that it sends to the server" (fresh, cryptographically random key
per message); a server must never mask frames it sends to a client, and
must close the connection if it receives an unmasked frame from a client
[Source: RFC 6455 §5.1].

**Fragmentation**: a single logical message may span multiple frames — the
first frame carries the real opcode (text/binary) with `FIN=0`,
continuation frames use opcode `0x0`, the final fragment has `FIN=1`.
Control frames (close/ping/pong, opcodes `0x8`-`0xA`) must never be
fragmented and are capped at **125 bytes** of payload.

Not documented / could not verify: an official maximum message or frame
size — the 64-bit payload-length field is a protocol-level ceiling, not a
practical/recommended one; real limits are implementation-defined per
browser/server [Source: research/technologies/websocket-api.md §8, §14].

## Close-code registry

[Source: https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent/code]
(cross-referencing RFC 6455 §7.4)

| Code | Name |
|---|---|
| 1000 | Normal Closure |
| 1001 | Going Away |
| 1002 | Protocol error |
| 1003 | Unsupported Data |
| 1004 | Reserved |
| 1005 | No Status Received (never actually sent on the wire) |
| 1006 | Abnormal Closure (never actually sent on the wire) |
| 1007 | Invalid frame payload data |
| 1008 | Policy Violation |
| 1009 | Message Too Big |
| 1010 | Mandatory Extension |
| 1011 | Internal Error |
| 1012 | Service Restart |
| 1013 | Try Again Later |
| 1014 | Bad Gateway |
| 1015 | TLS handshake (never actually sent on the wire) |
| 1016–2999 | Reserved for future protocol/extension revisions |
| 3000–3999 | Registered with IANA for library/framework/application use |
| 4000–4999 | Private use, by prior agreement between endpoints |

Codes 1005, 1006, and 1015 are explicitly documented as never actually sent
on the wire — they exist for the *local* API to report conditions where no
real close frame was received (e.g. an abrupt network drop). A `close`
handler that observes `1006` is diagnosing a client-side-observed abnormal
disconnect, not a value the remote peer chose to send.

## `permessage-deflate` negotiable parameters

[Source: https://www.rfc-editor.org/rfc/rfc7692.html]

Negotiated via `Sec-WebSocket-Extensions`:

- `server_no_context_takeover` / `client_no_context_takeover` — disable
  reuse of compression state between messages (memory-vs-ratio trade-off).
- `server_max_window_bits` / `client_max_window_bits` — LZ77 window size,
  8–15 (256–32768 bytes); RFC 7692 recommends "1,024 or more" for a useful
  compression ratio.

RFC 7692 explicitly warns of a CRIME-style compression-oracle exploit when
history-based compression is combined with a secure transport (TLS) and
attacker-influenced + secret content — integrate the extension with the
security protocol carefully rather than enabling it unconditionally.

## RFC 8441 — WebSockets over HTTP/2

[Source: https://www.rfc-editor.org/rfc/rfc8441.html]

Instead of the RFC 6455 `GET`+`Upgrade` handshake, RFC 8441 uses HTTP/2's
Extended CONNECT method with a `:protocol` pseudo-header set to
`websocket`, tunneling WebSocket framing inside a single HTTP/2 stream. The
server must advertise support via the `SETTINGS_ENABLE_CONNECT_PROTOCOL`
SETTINGS parameter for backward compatibility; once negotiated, ordinary
WebSocket framing takes over on that stream exactly as over raw TCP.
Relevant to deployments behind HTTP/2-terminating load balancers/gateways.

## Sources

See [`skill.yaml.source_references`](../skill.yaml) — all entries via
`research/technologies/websocket-api.md`, retrieved 2026-09-10.
