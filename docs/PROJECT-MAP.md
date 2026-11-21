# Gold Lotus project map

The canonical map is [`services/1lotus/docs/repositories.md`](../services/1lotus/docs/repositories.md).
The architecture diagram and runtime boundaries are in
[`services/1lotus/docs/architecture.md`](../services/1lotus/docs/architecture.md).

The local interface lives in [`apps/unified-ui/`](../apps/unified-ui/README.md) and listens
on `127.0.0.1:7771`. It owns the shared navigation and forwards requests to the
five existing services over local Unix sockets. Documentation is served from a
static build. Service ownership and runtime contracts remain with the five Lotus
service directories in `services/`. Live MT5 and Runner state lives in
`/home/ai-agent/lotus-runtime`; versioned backtests and bundles stay with their
own directories.

This pointer stays at the workspace root because Codex starts here when working across the six
project areas. Update the canonical files in `services/1lotus` when ownership changes.
