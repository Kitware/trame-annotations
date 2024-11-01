import js from "@eslint/js";
import ts from "typescript-eslint";
import vue from "eslint-plugin-vue";
import eslintConfigPrettier from "eslint-config-prettier";

export default ts.config(
  js.configs.recommended,
  ...ts.configs.recommended,
  ...vue.configs["flat/recommended"],
  eslintConfigPrettier,
  {
    files: ["*.vue", "**/*.vue"],
    languageOptions: {
      parserOptions: {
        parser: "@typescript-eslint/parser",
      },
    },
  },
);
