# License

This repository contains two kinds of material, licensed separately.

## Research content and data — CC BY 4.0

The governance documents, control data, source register, test definitions and generated model
artifacts are licensed under the
[Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).

This covers:

```text
README.md, AGENT-INSTRUCTIONS.md, GEOMETRY-CONTROL.md, SOURCE-REGISTER.md,
CONFIDENCE-MODEL.md, SCALE-HO.md
tests/*.json
viewer/metadata/*.json
cad/procedural/control_skeleton_geometry.json
mesh/glb/*
```

You are free to share and adapt this material for any purpose, including commercially, provided you
give appropriate credit and indicate if changes were made.

Cite as:

> *Manhattan Bridge Digital Twin: a source-governed control skeleton.* Ethical Tech CoLab, 2026.

## Code — MIT

The build pipeline and the browser viewer are licensed under the MIT License.

This covers:

```text
scripts/*.py
cad/procedural/build_in_blender.py
viewer/src/*, viewer/components/*, viewer/*.ts, viewer/*.json, viewer/index.html
```

```text
MIT License

Copyright (c) 2026 Ethical Tech CoLab

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Incorporated material

**Ethical Tech CoLab, *Silencing the Span* (`manhattan-bridge-noise-dumbo`), CC BY 4.0.**
Registered here as SRC-018. The floor beam depth recorded as CTL-062 and the qualitative trackform
characterisation are drawn from that work and used under its licence.

**Period engineering sources.** *Scientific American* (1908) and *The Engineering Record* (1904) are
in the public domain. HAER NY-127 photographs carry no known restrictions as U.S. Government works.
Individual sources, their licences and their verification state are recorded in
[SOURCE-REGISTER.md](SOURCE-REGISTER.md).

**Quoted material.** Short passages are quoted from copyrighted engineering literature — notably
Yanev and Gill, *Inspection, Evaluation and Maintenance of Suspension Bridges: Case Studies* (CRC
Press, 2016) — for scholarly commentary and citation. Those passages remain the property of their
respective authors and publishers. No source document is redistributed in this repository.
