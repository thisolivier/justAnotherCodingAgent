project:
  name: "my-node-app"
  language: "javascript"
  
file_rules:
  allowed_paths:
    - "src/**/*.js"
    - "tests/**/*.test.js"
  forbidden_paths:
    - "node_modules/**"
    - ".env"
    - "**/*.secret.*"

code_style:
  indent: 2
  quotes: "single"
  semicolons: false

testing:
  command: "npm test"
  required_coverage: 80

git:
  branch_prefix: "feature/"
  commit_format: "conventional"