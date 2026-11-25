# Gold Lotus project map

The canonical map is [`services/7lotus/docs/repositories.md`](../services/7lotus/docs/repositories.md).
The architecture diagram and runtime boundaries are in
[`services/7lotus/docs/architecture.md`](../services/7lotus/docs/architecture.md).

The local interface lives in [`services/1lotus/`](../services/1lotus/README.md) and listens
on `127.0.0.1:7771`. It owns the shared navigation and forwards requests to the
six remaining services over local Unix sockets. Documentation is served from a
static build. Service ownership and runtime contracts remain with the six Lotus
service directories in `services/`. Live MT5 and Runner state lives in
`/home/ai-agent/lotus-runtime`; versioned backtests and bundles stay with their
own directories.

This pointer stays at the workspace root because Codex starts here when working across the seven
project areas. Update the canonical files in `services/7lotus` when ownership changes.
