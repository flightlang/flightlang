# FlightLang POC

FlightLang is an experimental proof of concept for a small domain-specific language focused on UAV mission logic.

The goal of this repository is to demonstrate the shape of the language, a simple parse and typecheck pipeline, Python code generation, and a deterministic simulator. It is intentionally incomplete and not intended for real flight or production use.

## What FlightLang is exploring

FlightLang models missions as readable state-based programs with unit-aware values, mission metadata, transitions, and simulation-first execution.

This POC exists to explore whether mission logic can be expressed in a way that is easier to read, validate, and simulate than ad hoc scripts.

## POC status

This repository is a proof of concept. Some syntax is intentionally minimal and parts of the overall language design are still being explored.

The `examples/survey.fl` example is the runnable reference example for this POC.

## Quick start

Run a mission:

```bash
python -m flightlang.cli run examples/survey.fl
```

Validate a mission without running it:

```bash
python -m flightlang.cli check examples/survey.fl
```

Build Python output only:

```bash
python -m flightlang.cli build examples/survey.fl -o out.py
python out.py
```

## Example missions

### Minimal example

```flightlang
mission HoverTest {
  state Idle {
    on arm -> Takeoff
  }

  state Takeoff {
    action climb_to(10 m)
    on reached_altitude -> Hover
  }

  state Hover {
    deadline 3000 ms
    on timeout -> Done
  }

  state Done { }
}
```

### Runnable survey example

See `examples/survey.fl`.

## Roadmap

- richer expressions and conditions.
- stronger validation and typechecking.
- additional safety-oriented checks.
- improved simulator behavior.
- future transpilation targets beyond Python.

## Safety note

This is a teaching and experimentation scaffold only. It is not suitable for real aircraft or flight operations.
