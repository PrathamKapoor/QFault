# Attribution

QFAULT code was independently implemented. The evidence/review design draws on SAT-SA, Closure-Trace and Quantum-Secure-MLOps; QFT convention checks draw on QFT-Lab; resource/uncertainty discipline draws on Q-TRUST; causal-evaluation lessons draw on QuantumAttack. No historical performance claims transfer. See docs/reuse-inventory.md.

These related source notices are retained for attribution. No AGPL Muskit code or unlicensed QuantumAttack/Quantum-Simulator code is copied.

## SAT-SA / Closure-Trace / Quantum-Secure-MLOps / Q-TRUST

MIT License

Copyright (c) 2026 Pratham Kapoor

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

## QFT-Lab

MIT License

Copyright (c) 2026 QFT-Lab contributors

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

## Installed libraries

Qiskit is Apache-2.0 licensed; NumPy and SciPy use BSD licenses; React, TypeScript, Vite, Pydantic, FastAPI, Uvicorn, pytest and httpx retain their upstream package licenses. Dependencies are installed separately rather than vendored. React production notices are retained by the normal Vite bundle.

## Cinematic frontend (2026-10-12)

React Bits PixelSwap (and, since D041, Grainient) are adapted within QFAULT; Hyperspeed, MoltenMetal and TechText were removed from the landing in D041. Copyright (c) 2026 David Haz. They are governed by the retained MIT + Commons Clause terms in docs/licenses/react-bits.md, not the root MIT license alone. See docs/frontend-sources.md for exact revisions and modifications. Three.js and OGL are separately installed MIT dependencies. Mental.ai and Vantage informed original implementations; no unlicensed donor code was copied.

## MENTAL.AI landing hero (2026-10-13, D041)

The landing hero in web/src/components/hero (neural.ts, studioEnv.ts, engine.ts, NeuralStage.tsx, Wordmark.tsx, motion.ts, entry.css, hero-base.css, MentalHero.tsx) is transplanted from the MENTAL.AI web client (https://github.com/shreshthgod/mental.ai), authored by shreshthgod and PrathamKapoor. The repository has no license file; it is reused in QFAULT with the permission of its authors, as confirmed by the QFAULT owner (a MENTAL.AI co-author) on 2026-10-13. This permission does not extend to third parties. Grainient inside that folder is React Bits code under docs/licenses/react-bits.md. Inter Variable font files (5.3.0) are redistributed under the SIL Open Font License 1.1 (web/src/components/hero/fonts/OFL-1.1-Inter.txt). Details: docs/hero-transplant.md.
