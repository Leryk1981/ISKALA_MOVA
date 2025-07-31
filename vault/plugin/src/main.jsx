import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { initSodium } from "./core/crypto/libsodiumWrapper";

initSodium().then(() => {
  console.log("libsodium загружен");
  ReactDOM.createRoot(document.getElementById("root")).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
});
