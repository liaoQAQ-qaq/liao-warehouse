module.exports = {
  extends: [
    "@typescript-eslint/recommended",
    "@vue/eslint-config-typescript"
  ],
  parser: "vue-eslint-parser",
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: "module",
    parser: "@typescript-eslint/parser"
  },
  plugins: ["@typescript-eslint", "vue"],
  env: {
    browser: true,
    node: true,
    es2022: true
  },
  rules: {
    indent: ["error", 2],
    quotes: ["error", "single"],
    semi: ["error", "never"],
    "no-console": "warn",
    "no-unused-vars": "off",
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "@typescript-eslint/no-explicit-any": "warn",
    "vue/multi-word-component-names": "off"
  },
  ignorePatterns: ["dist/", "node_modules/", "*.d.ts"]
}
