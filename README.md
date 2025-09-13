# 🎓 Troni – Sistema de Recuperação Aumentada por Geração (RAG) para Apoio Acadêmico

Este projeto implementa um sistema baseado em **Recuperação Aumentada por Geração (RAG)** para fornecer informações institucionais do curso de **Engenharia Mecatrônica da UFSJ**.  
O sistema combina **modelos de linguagem (LLMs)** com uma base documental curada (arquivos `.pdf` e `.txt`) para garantir respostas mais **precisas, contextualizadas e confiáveis**, evitando alucinações comuns em LLMs puros.

---

## 🚀 Funcionalidades

- 📚 Ingestão automática de documentos acadêmicos (PPC, regulamentos, horários, colegiado etc.).
- 🔎 Indexação vetorial com **Qdrant** para recuperação eficiente.
- 🤖 Respostas baseadas em **RAG** ou **LLM puro** (para comparação).
- 🛡️ Módulo de segurança com filtros contra *prompt injection*.
- 📊 Testes com avaliação do sistema com métricas quantitativas:
  - Similaridade Semântica
  - ROUGE-L
  - Alucinação
- 📂 API em **Django**, com endpoints para perguntas e avaliação.

---
🛠️ Instalação
Clonar o Repositório
<pre>git clone https://github.com/seu-usuario/troni-rag.git
cd troni-rag</pre>

Criar ambiente virtual
<pre> python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows </pre>

Instalar dependência
<pre>pip install -r requirements.txt</pre>

Configurar variáveis de ambiente
<pre>
OPENAI_API_KEY = "sua_api_key"
COHERE_API_KEY = "sua_api_key"
QDRANT_API_KEY = "sua_api_key"
QDRANT_URL = "sua_qdrant_url"
</pre>

Na pasta data, você pode configurar os seus arquivos da forma como preferir, os arquivos utilizados nesse desenvolvimento estão disponíveis.

Caso queira modificar, será necessária a reindexação, que você pode fazer utilizando.
<pre>python manage.py ingest_data</pre>

Caso queira alterar as perguntas de teste, basta realizar no arquivo rag/management/commands/tests_pipeline. Para rodar os testes:
<pre>python manage.py tests_pipeline</pre>

Para ter acesso a um front-end básico, basta rodar o servidor:
<pre>python manage.py runserver</pre>

Caso queria utilizar integrando a outro tipo de desenvolvimento, apenas consumido a API, fazer a requisição para "SUA_URL_LOCAL:SUA_PORTA_LOCAL/api/chat/rag", após iniciar o servidor.

