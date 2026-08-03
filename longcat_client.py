#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LongCat 调用客户端（OpenAI 兼容 /openai/v1/chat/completions）

安全约束：
  - 密钥 ONLY 从 ~/.config/longcat/config.json 或环境变量 LONGCAT_* 读取
  - 脚本内绝不硬编码明文密钥

限制（LongCat API 明确说明，务必遵守）：
  - 此 endpoint 仅支持【纯文本】输入
  - 不支持图片输入（切勿传 image_url / 多模态 content）
  - 不支持 thinking 思考模式（切勿传 thinking 参数）

用法：
  python3 longcat_client.py "你的提示词"
作为库：
  from longcat_client import call, reply_text
  resp = call("hello")
  text = reply_text("hello")
"""
import json
import os
import sys
import urllib.request
import urllib.error

CONFIG_PATH = os.path.expanduser("~/.config/longcat/config.json")
DEFAULT_ENDPOINT = "https://api.longcat.chat/openai/v1/chat/completions"


def load_cfg():
    cfg = {
        "endpoint": os.environ.get("LONGCAT_ENDPOINT", ""),
        "api_key": os.environ.get("LONGCAT_API_KEY", ""),
        "model": os.environ.get("LONGCAT_MODEL", ""),
    }
    # 环境变量缺项时回退读私有配置文件
    if not (cfg["endpoint"] and cfg["api_key"] and cfg["model"]):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                c = json.load(f)
            cfg["endpoint"] = cfg["endpoint"] or c.get("endpoint") or DEFAULT_ENDPOINT
            cfg["api_key"] = cfg["api_key"] or c.get("api_key", "")
            cfg["model"] = cfg["model"] or c.get("model", "")
        except Exception:
            pass
    if not cfg["endpoint"]:
        cfg["endpoint"] = DEFAULT_ENDPOINT
    return cfg


def call(prompt, system="You are a helpful assistant.", max_tokens=1024,
         temperature=0.7, timeout=120):
    cfg = load_cfg()
    if not cfg["api_key"]:
        raise RuntimeError("未找到 LongCat API 密钥（请配置 " + CONFIG_PATH + " 或 LONGCAT_API_KEY）")
    # 注意限制：纯文本、不传 thinking、不传图片
    payload = {
        "model": cfg["model"],
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(cfg["endpoint"], data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + cfg["api_key"])
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode("utf-8", "replace")}
    except Exception as e:
        return {"error": "exception", "msg": str(e)}


def reply_text(prompt, **kw):
    """便捷：只返回模型文本回复内容。"""
    out = call(prompt, **kw)
    if isinstance(out, dict) and "choices" in out:
        return out["choices"][0]["message"]["content"]
    return out


if __name__ == "__main__":
    p = " ".join(sys.argv[1:]) or "Reply with exactly one short sentence proving you are reachable."
    out = call(p)
    if isinstance(out, dict) and "choices" in out:
        print(out["choices"][0]["message"]["content"])
    else:
        import pprint
        pprint.pprint(out)
