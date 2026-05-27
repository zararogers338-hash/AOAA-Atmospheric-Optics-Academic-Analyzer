# AI Backends / AI 后端

AOAA can run without any AI backend.

AOAA 可以在没有 AI 后端的情况下运行。

Optional backend types:

1. `llama-cpp-python`: local GGUF inference
2. `Ollama`: local model service
3. `OpenAI-compatible API`: external or self-hosted compatible APIs
4. `Ensemble / Hybrid`: multi-backend interpretation and fallback

Be careful with external APIs: document excerpts and prompts may be sent to remote services depending on your configuration.

请谨慎使用外部 API：根据你的配置，文档片段和提示词可能会被发送到远程服务。
