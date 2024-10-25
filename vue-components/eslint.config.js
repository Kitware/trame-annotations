// @ts-check

import js from '@eslint/js';
import vue from 'eslint-plugin-vue'
import ts from 'typescript-eslint';

export default ts.config(
  js.configs.recommended,
  ...ts.configs.recommended,
  ...vue.configs['flat/recommended'],
  {
    files: ['*.vue', '**/*.vue'],
    languageOptions: {
      parserOptions: {
        parser: '@typescript-eslint/parser'
      }
    }
  },
  {
    "rules": {
      "@typescript-eslint/no-explicit-any": 0
    }
  },
);