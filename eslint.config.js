export default [
  {
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "script",
      globals: {
        console: "readonly",
        window: "readonly",
        document: "readonly",
        localStorage: "readonly",
        setTimeout: "readonly",
        setInterval: "readonly",
        clearInterval: "readonly",
        fetch: "readonly",
        WebSocketClient: "readonly",
        wsClient: "writable",
        Sortable: "readonly",
        FormData: "readonly",
        URLSearchParams: "readonly",
        encodeURIComponent: "readonly",
        parseInt: "readonly",
        isNaN: "readonly",
        Date: "readonly",
        Array: "readonly",
        Math: "readonly",
        JSON: "readonly",
        String: "readonly",
        Number: "readonly",
        Object: "readonly",
        Set: "readonly",
        alert: "readonly",
        XMLHttpRequest: "readonly",
        drawSparkline: "readonly"
      }
    },
    rules: {
      "no-unused-vars": ["warn", { "argsIgnorePattern": "^_|^e$|^data$", "varsIgnorePattern": "^_|^sidebar$|^categoryDiv$" }],
      "no-console": "off",
      "no-undef": "error",
      "no-redeclare": "error",
      "no-constant-condition": "warn"
    }
  }
];
