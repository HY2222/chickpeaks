import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
// Fuentes autoalojadas (no dependen del wifi del evento). Ambas de bestfreefonts.com, licencia OFL.
import "@fontsource-variable/fraunces/full.css";
import "@fontsource-variable/fraunces/full-italic.css";
import "@fontsource-variable/figtree";
import "./index.css";
import App from "./App";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
