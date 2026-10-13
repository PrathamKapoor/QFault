/* Entry composition transplanted from the MENTAL.AI web client web/src/pages/Start.tsx (authors: shreshthgod,
   PrathamKapoor); reused in QFAULT with the authors' permission.
   Kept: Grainient atmosphere, back word plane -> NeuralStage sculpture -> front word plane, vignette, rules, labels,
   copy block, timings (letters, 2000 ms sculpture appearance) and the 70/30 handover layout.
   Removed: authentication, login/welcome panels, router, session greeting. The handover (entry--split) is driven by
   QFAULT's Enter Workbench action instead of a login, and the right column holds QFAULT's workspace-access panel. */
import React, { lazy, Suspense, useEffect, useState, type MouseEvent } from "react";
import { WordPlane } from "./Wordmark";
import { useReducedMotion } from "./motion";
import "./hero-base.css";
import "./entry.css";
import "./hero.css";

const NeuralStage = lazy(() => import("./NeuralStage"));
const Grainient = lazy(() => import("./Grainient/Grainient").then((m) => ({ default: m.Grainient })));

const HERO_APPEAR_MS = 2000;
const FIELD_LABELS = ["Circuit / contract", "Evidence / measured", "Recovery / verified"];

interface Props {
  /** Intro already played in this session: letters assemble quickly and the metal appears at once. */
  instant: boolean;
  /** QFAULT's Enter Workbench handover is in progress. */
  handover: boolean;
  onEnter: () => void;
  onResearch: (e: MouseEvent) => void;
}

export default function MentalHero({ instant, handover, onEnter, onResearch }: Props) {
  const reduced = useReducedMotion();
  const [live, setLive] = useState(false);
  const [heroVisible, setHeroVisible] = useState(false);

  useEffect(() => {
    const raf = requestAnimationFrame(() => setLive(true));
    const timer = window.setTimeout(() => setHeroVisible(true), instant || reduced ? 0 : HERO_APPEAR_MS);
    return () => {
      cancelAnimationFrame(raf);
      window.clearTimeout(timer);
    };
  }, [instant, reduced]);

  return (
    <div
      className={`entry ${live ? "entry--live" : ""} ${heroVisible ? "entry--hero-live" : ""} ${handover ? "entry--split" : ""}`}
      data-hero="mental"
    >
      <div className="entry__atmosphere" aria-hidden="true" />
      <Suspense fallback={null}>
        <Grainient
          className="entry__grain"
          color1="#0e0b20"
          color2="#17123a"
          color3="#030306"
          timeSpeed={0.28}
          warpStrength={0.26}
          warpFrequency={1.8}
          warpSpeed={0.11}
          warpAmplitude={55}
          blendAngle={128}
          blendSoftness={0.85}
          rotationAmount={36}
          grainAmount={0.05}
          grainScale={1.3}
          contrast={1.02}
          gamma={1.1}
          saturation={0.86}
          centerY={-0.04}
          zoom={1.9}
        />
      </Suspense>

      <div className="entry__main">
        <section className="hero-stage" aria-label="QFAULT">
          <div className="hero-stage__scene">
            <div className="entry__depth">
              <WordPlane live={live} plane="back" instant={instant} />
              <Suspense fallback={null}>
                <NeuralStage className="entry__stage" emergeDelayMs={0} focus={0} />
              </Suspense>
              <WordPlane live={live} plane="front" instant={instant} />
            </div>
            <div className="entry__vignette" aria-hidden="true" />
            <div className="entry__rules" aria-hidden="true">
              <span className="entry__rule entry__rule--gutter" />
              <span className="entry__rule entry__rule--split" />
            </div>
            <ul className="entry__labels" aria-hidden="true">
              {FIELD_LABELS.map((label, i) => (
                <li key={label} className={`entry__label entry__label--${i + 1}`}>
                  {label}
                </li>
              ))}
            </ul>
          </div>

          <div className="entry__copy">
            <p className="label label--accent">Quantum failure analysis / Qiskit</p>
            <h2 className="entry__headline">Find the fault. Test the fix.</h2>
            <p className="entry__sub">
              Investigate quantum circuit failures, evaluate evidence, test bounded recovery, and verify the result.
            </p>
            <div className="entry__ctas">
              <button type="button" className="cta cta--primary" disabled={handover} onClick={onEnter}>
                Enter Workbench <span className="cta__arrow" aria-hidden="true">→</span>
              </button>
              <a href="#/" className="cta cta--ghost" onClick={onResearch}>
                Explore the Research
              </a>
            </div>
          </div>
        </section>

        <section className="auth-stage" aria-label="Workspace access" aria-hidden={!handover}>
          <div className="entry__panel-slot">
            <div className="entry__panel-inner">
              <p className="label label--accent">QFAULT / Workspace access</p>
              <p className="entry__heading">Your quantum laboratory is ready.</p>
              <p className="entry__sub">Continue to the local workbench. Simulation only: Qiskit and Qiskit Aer.</p>
              <p className="entry__micro">Execute · Diagnose · Recover · Verify</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
