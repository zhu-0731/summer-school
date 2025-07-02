# AI 聊天系统

基于 FastAPI + Vue3 的 AI 聊天系统，支持 DeepSeek 和 Ollama 两种模式。

## 基础配置

### 1. 环境变量配置
在 `.env` 文件中配置以下参数：

```bash
# DeepSeek API密钥 (使用DeepSeek模式必需)
DEEPSEEK_API_KEY=your-api-key

# Ollama服务地址 (使用Ollama模式，可选，默认为本地地址)
OLLAMA_BASE_URL=http://localhost:11434
```

### 2. 依赖安装
```bash
pip install -r requirements.txt
```

### 3. 运行服务
```bash
python fast_app.py
```
访问 http://localhost:8000 即可使用

## 模式说明

1. DeepSeek模式
   - 使用DeepSeek API进行对话
   - 需要配置 DEEPSEEK_API_KEY

2. Ollama模式
   - 使用本地或远程的Ollama服务
   - 可通过OLLAMA_BASE_URL配置服务地址
   - 默认使用deepseek-r1:14b模型

## 功能特点

- 支持单轮/多轮对话
- 支持清空历史/查看历史
- 支持Markdown渲染
- 代码高亮显示
- 实时响应状态
- 现代化UI界面
