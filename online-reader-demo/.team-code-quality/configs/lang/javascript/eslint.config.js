import js from '@eslint/js';
import typescriptEslint from '@typescript-eslint/eslint-plugin';
import typescriptParser from '@typescript-eslint/parser';
import vueEslint from 'eslint-plugin-vue';
import vueParser from 'vue-eslint-parser';

export default [
  // Base JS rules
  js.configs.recommended,
  
  // TypeScript rules
  {
    files: ['**/*.ts', '**/*.js', '**/*.vue'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: typescriptParser,
        ecmaVersion: 2022,
        sourceType: 'module',
        extraFileExtensions: ['.vue']
      },
      // 浏览器全局对象，避免在前端代码中被报 no-undef
      globals: {
        fetch: 'readonly',
        FormData: 'readonly',
        alert: 'readonly',
        confirm: 'readonly',
        console: 'readonly',
        window: 'readonly',
        document: 'readonly'
      }
    },
    plugins: {
      '@typescript-eslint': typescriptEslint,
      'vue': vueEslint
    },
    rules: {
      // Basic rules
      'indent': ['warn', 2],
      'quotes': ['warn', 'single'],
      'semi': ['warn', 'never'],
      'no-console': 'warn',
      'no-unused-vars': 'off',
      
      // TypeScript rules
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/no-explicit-any': 'warn',
      
      // Vue rules
      'vue/multi-word-component-names': 'off'
    }
  }
];
