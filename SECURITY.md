# Security Policy / 安全说明

AOAA is a local research and visualization tool. Users are responsible for the documents and model backends they connect.

AOAA 是本地研究与可视化工具。用户需要自行负责输入文档和模型后端的安全性。

## Do not upload / 不要上传

- Private personal data
- Confidential institutional documents
- Sensitive research material without permission
- API keys or credentials
- Large private model files

## AI backend safety / AI 后端安全

When using local GGUF or llama-cpp-python workflows, only load model files from trusted sources. External API backends may send prompts and document excerpts to remote services, depending on configuration.

使用本地 GGUF 或 llama-cpp-python 工作流时，请只加载可信来源的模型文件。外部 API 后端可能会根据配置把提示词和文档片段发送到远程服务。

## Reporting / 报告问题

Please open a GitHub issue for non-sensitive issues. For sensitive security issues, avoid posting private data publicly.
