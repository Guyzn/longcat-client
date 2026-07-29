# longcat-client

美团「龙猫」大模型 **LongCat** 的 OpenAI 兼容 API 客户端。

纯标准库实现（`urllib` only），**零第三方依赖**，支持环境变量与配置文件双通道。

## 特性

- OpenAI 兼容 `/openai/v1/chat/completions` 接口
- 密钥从 `~/.config/longcat/config.json` 或环境变量 `LONGCAT_*` 读取
- 脚本内绝不硬编码明文密钥
- 支持作为库调用（`from longcat_client import call, reply_text`）

## 配置

**方式一：配置文件**

`~/.config/longcat/config.json`：

```json
{
  "endpoint": "https://api.longcat.chat/openai/v1/chat/completions",
  "api_key": "sk-xxxx",
  "model": "LongCat-2.0"
}
```

**方式二：环境变量**

```bash
export LONGCAT_ENDPOINT="https://api.longcat.chat/openai/v1/chat/completions"
export LONGCAT_API_KEY="sk-xxxx"
export LONGCAT_MODEL="LongCat-2.0"
```

## 用法

命令行：

```bash
python3 longcat_client.py "讲一个关于钢铁的冷笑话"
```

作为库：

```python
from longcat_client import call, reply_text

resp = call("你好")
text = reply_text("你好")
print(text)
```

## 限制（LongCat API 明确说明）

- 此 endpoint 仅支持**纯文本**输入
- 不支持图片输入（切勿传 `image_url` / 多模态 content）
- 不支持 thinking 思考模式（切勿传 `thinking` 参数）

## License

MIT
