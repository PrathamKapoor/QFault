/* Transplanted from the MENTAL.AI web client (authors: shreshthgod, PrathamKapoor); reused in QFAULT with the authors' permission. See THIRD_PARTY_NOTICES.md. */
/* Only useReducedMotion is used by the hero; the remaining helpers of lib/motion.ts are not transplanted. */
import { useSyncExternalStore } from "react";

const mq = () => window.matchMedia("(prefers-reduced-motion: reduce)");

const subscribe = (cb: () => void) => {
  const m = mq();
  m.addEventListener("change", cb);
  return () => m.removeEventListener("change", cb);
};

export function useReducedMotion(): boolean {
  return useSyncExternalStore(
    subscribe,
    () => mq().matches,
    () => false
  );
}

