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
- **Django + DRF** como backend.  
- **Qdrant** como vetor store para busca semântica.  
- **OpenAI Embeddings** para representação vetorial de textos.  
- **LLM (GPT)** para geração de respostas condicionadas ao contexto recuperado.  
- **Métricas automáticas** para avaliar desempenho (similaridade, ROUGE-L, alucinação etc).  
---

## 🗂 Estrutura dos Arquivos

### `security_prompt.py`
Define mecanismos de **segurança contra prompt injection** e **validação de saída**:
- `PromptInjectionFilter` → detecta padrões perigosos (ex: “ignore instruções anteriores”).  
- `OutputValidator` → valida respostas para evitar vazamento de segredos.  
- `SecureLLMPipeline` → combina filtros, contexto e validação antes de chamar a LLM.  

---

### `views.py`
Define a **API principal** para interação com o chatbot (`/api/chat/rag`):
- Recebe `user_query` e `modo` (puro ou RAG).  
- Se **RAG**: recupera categorias, busca chunks no Qdrant, monta contexto e passa para o pipeline seguro.  
- Se **puro**: envia direto para a LLM.  
- Retorna:
  ```json
  {
    "answer": "...",
    "sources": ["arquivo.txt", "documento.pdf"]
  }
### `embeddings_utils.py`
- Gera embeddings com OpenAI (text-embedding-3-large).
- Retorna vetores normalizados para busca semântica.
  
### `qdrant_singleton.py`
Gerencia a conexão com o Qdrant:
- Implementa Singleton.
- ensure_collection → cria coleções ufsj_<categoria>.
- search → busca vetorial.
- upsert_points → insere embeddings com payload (texto, fonte, página, categoria).

### `extract_chunks.py`
Responsável por dividir documentos em chunks:
- process_txt → divide .txt em blocos de até 500 palavras.
- process_pdf → usa pymupdf4llm.to_markdown para extrair PDFs em markdown.
- Cada chunk contém texto + número da página.

### `ingest_data.py`
Comando Django para ingestão de dados no Qdrant:
1- Lê data_config.json → mapeia categorias para arquivos.
2 - Extrai chunks (via extract_chunks).
3 - Gera embeddings (create_embedding).
4 - Insere no Qdrant (upsert_points).

### `tests_pipeline.py`
Script de avaliação do pipeline:
- Executa perguntas nos modos LLM puro e RAG.
- Calcula métricas:
-- Similaridade semântica
-- ROUGE-L
-- Taxa de alucinação
-- Fonte recuperada
-- Comprimento da resposta
-Gera avaliacao_completa.json com resultados detalhados.

---

---
📊 Fluxo Geral do Sistema

Ingestão de dados → (ingest_data.py) prepara coleções no Qdrant.

Usuário faz uma pergunta → (views.py).

Pipeline de segurança → (security_prompt.py) aplica filtros e validações.

Busca semântica → (qdrant_singleton.py + embeddings_utils.py).

LLM gera resposta → com base no contexto recuperado.

Métricas de avaliação → (tests_pipeline.py) validam a qualidade do sistema.
--
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

