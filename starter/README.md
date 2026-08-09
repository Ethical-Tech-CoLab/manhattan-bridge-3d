# Starter kit for a new bridge repository

[AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md) in this folder is a **drop-in starting brief** for a
new source-governed bridge model — written for the Brooklyn Bridge and Williamsburg Bridge efforts,
but not specific to either.

## Use it

```powershell
# from the new repository root
Copy-Item ..\manhattan-bridge-3d\starter\AGENT-INSTRUCTIONS.md .\AGENT-INSTRUCTIONS.md
```

Then trim the sections that do not apply and work through its day-one checklist.

## Also worth porting

These three scripts are bridge-agnostic and dependency-free, and carry the parsing contract that
makes the governance rules enforceable rather than aspirational:

| From this repo | What it gives you |
|---|---|
| [scripts/control_model.py](../scripts/control_model.py) | Parses the control document; rejects a graded row with no source and a placeholder that cites one |
| [scripts/normalize_units.py](../scripts/normalize_units.py) | The single unit-conversion implementation |
| [scripts/export_gltf.py](../scripts/export_gltf.py) | glTF 2.0 / GLB writer with no third-party dependencies |

## What the guide will not do for you

It carries the method and the traps, not the dimensions. Every number in a new repository has to be
sourced there from scratch — and the Manhattan Bridge's figures are registered in
[SOURCE-REGISTER.md](../SOURCE-REGISTER.md) as a **negative control** for exactly that reason.
Three similar East River suspension bridges are the most likely way this programme produces a
confident wrong number.
