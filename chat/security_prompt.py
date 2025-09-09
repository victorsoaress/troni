# chat/security_prompt.py
import re
import unicodedata
from llama_index.core.llms import ChatMessage

def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = s.encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s

class PromptInjectionFilter:
    def __init__(self):
        self.dangerous_patterns = [
            r'ignore\s+(all|previous|prior)?\s*instructions',
            r'ignorar\s+(todas\s+as\s+)?instru(c|ç)oes\s+anteriores',
            r'(system|assistant)\s+override',
            r'(reveal|revele)\s+(system\s+)?prompt',
            r'developer\s+mode|modo\s+desenvolvedor',
        ]
        self.fuzzy_terms = [
            'ignore','ignorar','bypass','sobrescreva','desconsidere','revele','apague','system','sistema','api','key','senha'
        ]

    def detect_injection(self, text: str) -> bool:
        t = _norm(text)
        if any(re.search(p, t, re.I) for p in self.dangerous_patterns):
            return True
        return any(term in t for term in self.fuzzy_terms)

    def sanitize_input(self, text: str) -> str:
        t = text or ""
        t = re.sub(r'<[^>]+>', ' ', t)               
        t = re.sub(r'http[s]?://\S+', ' [link] ', t) 
        t = re.sub(r'\s+', ' ', t)
        t = re.sub(r'(.)\1{3,}', r'\1', t)           
        for pattern in self.dangerous_patterns:
            t = re.sub(pattern, '[FILTERED]', t, flags=re.IGNORECASE)
        return t[:10000]

class OutputValidator:
    def __init__(self):
        self.suspicious_patterns = [
            r'SYSTEM\s*[:]\s*You\s+are',
            r'API[_\s]?KEY[:=]\s*\w+',
            r'instructions?[:]\s*\d+\.',
        ]
        self.max_len = 5000

    def validate_output(self, output: str) -> bool:
        if not output or len(output) > self.max_len:
            return False
        return not any(re.search(p, output, re.IGNORECASE) for p in self.suspicious_patterns)

    def filter_response(self, response: str) -> str:
        return response if self.validate_output(response) else "Não posso responder à essa questão por motivos de segurança."

class SecureLLMPipeline:
    def __init__(self):
        self.input_filter = PromptInjectionFilter()
        self.output_validator = OutputValidator()

    def process_request(self, context: str, user_query: str, system_instructions: str, llm_client) -> str:
        if self.input_filter.detect_injection(user_query):
            return "Não posso responder à essa questão por motivos de segurança."

        clean_user_query = self.input_filter.sanitize_input(user_query)

        messages = [
            ChatMessage(role="system", content=(system_instructions or "").strip()),
            ChatMessage(role="assistant", content=f"CONTEXT_START\n{(context or '').strip()}\nCONTEXT_END"),
            ChatMessage(role="user", content=clean_user_query.strip()),
        ]

        resp = llm_client.chat(messages)
        answer = (getattr(resp, "message", None).content or "").strip()
        return self.output_validator.filter_response(answer)


