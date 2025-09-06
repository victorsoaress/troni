# chat/views.py
import json
import os
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI

def _get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY não configurada")
    return OpenAI(api_key=api_key)

@csrf_exempt 
def chat_view(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Use POST")
    try:
        data = json.loads(request.body.decode("utf-8"))
        user_msg = data.get("msg", "").strip()
        if not user_msg:
            return HttpResponseBadRequest("Campo 'msg' é obrigatório")
        client = _get_openai_client()

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Responda em PT-BR de forma objetiva."},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.2,
        )
        text = resp.choices.message.content or ""
        return JsonResponse({"answer": text})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# chatbot/views.py
from django.shortcuts import render

def home(request):
    # Renderiza seu template principal do chat
    return render(request, "templates/index.html")