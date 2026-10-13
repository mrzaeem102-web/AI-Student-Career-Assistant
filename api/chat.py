import json
import os
from http.server import BaseHTTPRequestHandler
from openai import OpenAI

INSTRUCTIONS = """
You are an AI Student & Career Assistant.
Help students with academic learning, career guidance, and skill development.

Guidelines:
- Explain concepts clearly for beginners.
- Use headings and examples when helpful.
- Never invent a student's qualifications or experience.
- Be honest when uncertain and encourage verification.
- Do not promise grades, jobs, or guaranteed outcomes.
"""

TASKS = {
    "General assistance": "Help with the user's question.",
    "Academic Learning": "Explain concepts step by step and include examples.",
    "Study Planning": "Create a realistic study plan with breaks and priorities.",
    "CV Improvement": "Suggest honest, specific improvements to a student's CV.",
    "Interview Preparation": "Provide interview practice questions and feedback.",
    "Professional Writing": "Help draft clear, polite professional messages.",
}


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/api/chat":
            return self.send_json(404, {"error": "Endpoint not found."})

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 100_000:
                return self.send_json(400, {"error": "Invalid request size."})

            body = json.loads(self.rfile.read(length))
            task = body.get("task", "General assistance")
            message = body.get("message", "")
            history = body.get("history", [])

            if task not in TASKS:
                return self.send_json(400, {"error": "Unknown assistant task."})

            if not isinstance(message, str) or not message.strip():
                return self.send_json(400, {"error": "Please enter a message."})

            if len(message) > 12_000:
                return self.send_json(400, {"error": "Message is too long."})

            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                return self.send_json(500, {"error": "Server API key is not configured."})

            messages = [{
                "role": "system",
                "content": INSTRUCTIONS + "\nSelected task: " + task
                           + "\n" + TASKS[task]
            }]

            if isinstance(history, list):
                for item in history[-10:]:
                    if (
                        isinstance(item, dict)
                        and item.get("role") in ("user", "assistant")
                        and isinstance(item.get("content"), str)
                    ):
                        messages.append({
                            "role": item["role"],
                            "content": item["content"][:12000]
                        })

            messages.append({"role": "user", "content": message})

            client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1",
            )

            response = client.chat.completions.create(
                model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                messages=messages,
            )

            answer = response.choices[0].message.content
            return self.send_json(200, {
                "answer": answer or "The AI returned an empty response."
            })

        except json.JSONDecodeError:
            return self.send_json(400, {"error": "Invalid JSON request."})
        except Exception:
            return self.send_json(500, {
                "error": "The AI request failed. Check the server configuration and Groq usage limits."
            })

    def do_GET(self):
        self.send_json(200, {"status": "AI assistant API is running."})

    def send_json(self, status, data):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)
