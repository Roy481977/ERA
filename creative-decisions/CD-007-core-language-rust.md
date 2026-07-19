# CD-007 — The authoritative core is written in Rust

| Field | Value |
|---|---|
| ID | CD-007 |
| Date | 2026-07-19 |
| Status | **PROPOSED** — CKO decision at Roy's direction; awaiting ratification. |
| Domain | Implementation / architecture (logical core) |

## The decision

ERA's **authoritative simulation core** (the Town Engine brain and the persistent
world state) is implemented in **Rust**. This is the *core/runtime language only*
— it explicitly does **not** choose the game engine (Unreal/Unity), which remains
an open question in IP-003. Chosen to optimize for the final production
architecture, not development speed.

## Links

- IP-003 (federation of systems, one world state; engine choice open), CD-006
  (Town Engine), `research/town-engine-technical-strategy.md` (build-the-brain /
  buy-the-muscles; keep the brain engine-decoupled and headless), DS-001.

## Alternatives considered

- **Python** — fastest to iterate; used for the Phase-1 spike. Rejected for the
  core: no path to deterministic, GC-free, large-scale production simulation.
- **C++** — native to Unreal, maximal performance; heavier and memory-unsafe,
  biases the engine choice toward Unreal, slower/riskier to keep clean.
- **C# / .NET** — production-grade; via Unity DOTS/ECS + Burst it scales well and
  shares a language with Unity. Rejected as the *default* because it biases toward
  one engine and has more runtime nondeterminism sources than Rust.
- **Go** — simple concurrency, but GC pauses and non-ECS shape make it a weak fit
  for a deterministic agent simulation.

## Why this won

The architecture demands a **sovereign, engine-decoupled brain** that owns world
truth. Rust delivers it best: it compiles to a native lib (FFI to Unreal C++ or
Unity C#), to WASM (observability/tooling), or a standalone server, so it never
locks the open engine decision. It gives the tightest control over evaluation
order and arithmetic needed for **bit-reproducible deterministic replay** (a core
promise), **GC-free performance** for hundreds of agents and offscreen
simulation, an **ECS-native** shape that matches "federation of systems over one
shared state," and **memory safety** for a foundation meant to outlive its
authors. Python optimizes for speed (rejected by Roy's directive); C#/C++ bias the
engine choice.

## What it rejects / supersedes

- Supersedes the Sprint-1 provisional Python logical core (migrated to Rust while
  the codebase was four small files).

## Consequences

- The core is a headless Rust crate with deterministic, testable modules; front
  ends (Unreal/Unity/web) embed or link to it later.
- FFI/embedding boundaries must be designed when the engine is chosen (a future
  work item), but no engine is committed now.

## Open threads

- Game-engine choice (Unreal vs Unity) — still open (IP-003).
- Fixed-point vs float policy for cross-platform determinism — to settle before
  any float enters simulation math.

## Authority

Proposed by the CKO at Roy's explicit direction. **Awaiting Roy's ratification.**
