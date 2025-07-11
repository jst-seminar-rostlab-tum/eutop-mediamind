// @ts-check

import eslint from "@eslint/js";
import tseslint from "typescript-eslint";

export default tseslint.config(
  {
    ignores: ["**/.react-router/**"],
  },
  {
    files: ["**/*.{js,jsx,ts,tsx}"],
  },
  eslint.configs.recommended,
  tseslint.configs.recommended,
);
