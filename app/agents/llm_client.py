import os, httpx

class LLMError(Exception):
    pass

class LLMClient:
    def __init__(self, base_url=None, api_key=None, model=None, timeout=8):
        self.base_url=(base_url or os.getenv("LLM_BASE_URL","")).rstrip("/")
        self.api_key=api_key or os.getenv("LLM_API_KEY","")
        self.model=model or os.getenv("LLM_MODEL","")
        self.timeout=timeout

    def available(self):
        return bool(self.api_key) or "localhost" in self.base_url or "127.0.0.1" in self.base_url

    def chat(self, messages, tools=None):
        if not self.available():
            raise LLMError("no api key")
        payload={"model": self.model, "messages": messages}
        if tools:
            payload["tools"]=tools
        try:
            r=httpx.post(f"{self.base_url}/chat/completions",
                        headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                        json=payload, timeout=self.timeout)
            r.raise_for_status()
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            raise LLMError(str(e))
        data=r.json()["choices"][0]["message"]
        return {"content": data.get("content") or "", "reasoning": data.get("reasoning") or data.get("reasoning_content") or "", "tool_calls": data.get("tool_calls") or []}