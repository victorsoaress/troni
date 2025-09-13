from django.core.management.base import BaseCommand
import requests
import json
import requests
import json
from embeddings_utils import create_embedding
import numpy as np
from rouge_score import rouge_scorer

class Command(BaseCommand):
    help = "Roda os testes do pipeline"

    def handle(self, *args, **options):
        PERGUNTAS_TESTE = [
            # ========================
            # 5 perguntas de tópicos variados (IDs 101-105)
            # ========================
            {
                "id": 101,
                "categoria": "premios",
                "pergunta": "Quais são os critérios para receber o Prêmio de Mérito Acadêmico?",
                "resposta_esperada": """Para ser elegível ao Prêmio de Mérito Acadêmico, o discente deve atender aos seguintes critérios:
                    1. **Coeficiente de Rendimento (CR) igual ou superior a 8,0**, conforme o extrato escolar fornecido pela UFSJ/Dicon;
                    2. **Integralização de, no mínimo, 80% da carga horária total** do curso na UFSJ;
                    3. **Cumprimento de todos os requisitos para colação de grau**."""
            },
            {
                "id": 102,
                "categoria": "empresa_junior",
                "pergunta": "Quais são as principais áreas de atuação da Tristate Consultoria?",
                "resposta_esperada": "As principais áreas de atuação da Tristate incluem software/android/web, automação industrial, automação residencial (Domótica), modelagem computacional e manufatura 3D."
            },
            {
                "id": 103,
                "categoria": "inscricao_periodica",
                "pergunta": "Quais são as três etapas da inscrição periódica e quando ocorre a solicitação de quebra de pré‑requisito/extrapolação de carga?",
                "resposta_esperada":  "As três etapas da inscrição periódica são a Matrícula, realizada de 30 de julho a 1º de agosto de 2025 com resultado divulgado em 6 de agosto de 2025; a Rematrícula, que ocorre de 8 a 12 de agosto de 2025 com resultado em 18 de agosto de 2025; e a Matrícula Extraordinária, que será de 19 a 27 de agosto de 2025 e é destinada à ocupação de vagas remanescentes. A solicitação de quebra de pré-requisito ou extrapolação de carga horária deve ser feita por meio de formulário online, acessível apenas com o e-mail institucional, sendo obrigatória a tentativa prévia de matrícula no SIGAA com comprovação anexada. Esses pedidos só são analisados se o aluno tiver, no mínimo, 3000 horas integralizadas ou necessitar cursar duas disciplinas dependentes para concluir o curso, e a prioridade é dada, primeiro, ao discente com maior carga horária integralizada e, em seguida, ao que possui maior índice de rendimento no SIGAA."
            },
            {
                "id": 104,
                "categoria": "requerimento_eletronico",
                "pergunta": "Quais modalidades podem ser abertas no Requerimento Eletrônico do curso?",
                "resposta_esperada": "As modalidades que podem ser abertas no Requerimento Eletrônico são: Abono de Faltas, Apólice de Seguro - somente para estágio curricular obrigatório, Atestado de Frequência, Atividades Complementares, Carta de Apresentação para Estágio, Certificado de Monitoria, Dispensa de Disciplina (a solicitação de Equivalência/Aproveitamento de Estudos é realizada em outro item), Equivalência Interna entre Unidades Curriculares e/ou Aproveitamento de Estudo, Inscrição em Estágio Curricular Obrigatório, Inscrição em Trabalho de Conclusão de Curso (TCC I e/ou TCC II), Inscrição em TCIC I e/ou TCIC II - Trabalho de Contextualização e Integração Curricular (apenas alunos ingressantes em 2017.1), Prorrogação do Prazo de Integralização do Curso, Segunda Chamada de Avaliação, Tratamento Especial de Estudos, Recurso contra Decisão do Colegiado de Curso, Revisão de Avaliação e de Nota Final, OUTROS - caso não esteja elencado nos itens relacionados acima."
            },
            {
                "id": 105,
                "categoria": "atividade_complementar",
                "pergunta": "Quais são os passos principais para solicitar a contagem de horas de Atividades Complementares?",
                "resposta_esperada": "Os passos para solicitar a contagem de horas complementares são: Preencher o formulário online disponível na aba Requerimento Eletrônico; Preencher e assinar o formulário de Atividades Complementares: AC-01. Anexar o formulário AC-01 e comprovantes das atividades por meio do envio de arquivo único em PDF** | Crie um arquivo único em PDF que contenha o formulário AC-01 e os comprovantes das atividades, na sequência em que foram listados no formulário. Envie esse arquivo único para que as atividades sejam validadas no sistema. **AS ATIVIDADES SERÃO VALIDADAS NO SISTEMA SOMENTE APÓS REALIZAÇÃO DOS PROCEDIMENTOS DESCRITOS"
            },

            # ========================
            # 5 perguntas exclusivas dos PDFs (IDs 201-205)
            # ========================
            {
                "id": 201,
                "categoria": "colegiado",
                "pergunta": "Segundo a Resolução UFSJ/Consu nº 009/2019, como é composta a estrutura do Colegiado do Curso de Engenharia Mecatrônica?",
                "resposta_esperada": """O Colegiado do Curso é composto:
                    I – pelo(a) coordenador(a) do Curso, que o preside;
                    II – pelo(a) vice-coordenador(a) do Curso;
                    III – por 3 (três) membros conselheiros docentes do Curso;
                    IV – por 1 (um) discente do curso, indicado pelo órgão representativo e, na
                    falta desse órgão, eleito pelos respectivos pares."""
            },
            {
                "id": 202,
                "categoria": "colegiado",
                "pergunta": "Quais são os membros do colegiado?",
                "resposta_esperada": "Atualmente, o Colegiado é composto pelos seguintes membros: Diego Raimondi Corradi, que ocupa o cargo de Coordenador, com vigência de mandato de 17/11/2023 a 16/11/2025;  Filipe Augusto Santos Rocha, que é o Vice-Coordenador, com mandato de 05/05/2025 a 05/05/2027; Wesley Josias de Paula, que é o 1º Membro Docente, com mandato de 04/06/2025 a 03/06/2027; Leonardo Guimarães Fonseca, que ocupa o cargo de 2º Membro Docente, com mandato de 25/07/2024 a 24/07/2026; Rone Ilídio da Silva, que é o 3º Membro Docente, com mandato de 22/03/2025 a 21/03/2027; e Victor de Almeida Andrade, que é o Membro Discente, com mandato de 04/12/2024 a 03/12/2025."
            },
            {
                "id": 203,
                "categoria": "ppc",
                "pergunta": "De acordo com o PPC do curso, qual é o objetivo geral da Engenharia Mecatrônica na UFSJ?",
                "resposta_esperada": "O curso de graduação em Engenharia Mecatrônica da Universidade Federal  de São João del-Rei, Campus Alto Paraopeba, tem como objetivo geral formar engenheiros com sólido preparo científico e tecnológico na área de Elétrica, Mecânica, Computação,Controle e Automação. Os egressos devem ter capacidade de absorver e desenvolver novas tecnologias"
            },
            {
                "id": 204,
                "categoria": "ppc",
                "pergunta": "Segundo o PPC, quais são os princípios curriculares básicos da formação no curso?",
                "resposta_esperada": "Formação sólida em fundamentos científicos (física, matemática, informática); formação tecnológica em mecânica, controle e automação; formação complementar em sistemas e processos; formação metodológica em engenharia."
            },
            {
                "id": 205,
                "categoria": "ppc",
                "pergunta": "No PPC, quais são as informações básicas de oferta e integralização (modalidade, turnos, vagas e duração)?",
                "resposta_esperada": "Modalidade: curso noturno e integral. Turnos: o primeiro semestre é destinado ao curso noturno e o segundo semestre ao curso integral.Vagas: 50 vagas semestrais.Duração: o curso tem duração de cinco anos, modulado em semestres de dezoito semanas letivas."
            },
            {
                "id": 206,
                "categoria": "ppc",
                "pergunta": "Quais são as matérias obrigatórias do primeiro período?",
                "resposta_esperada":"""1. Cálculo Diferencial e Integral I 
                                        2. Sistemas Digitais
                                        3. Algoritmos e Estrutura de Dados I 
                                        4. Química Geral
                                        5. Química Geral Experimental
                                        6. Introdução a Engenharia Mecatrônica 
                                        7. Metodologia Científica
                        """
            }         
        ]

        API_URL = "http://127.0.0.1:8000/api/chat/rag"

        # ========================
        # Funções de Métricas
        # ========================

        def cosine_similarity(v1, v2):
            """Cálculo da similaridade coseno"""
            v1, v2 = np.array(v1), np.array(v2)
            return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    

        def avaliar_resposta(resposta_modelo, resposta_esperada, fontes=None):
            """
            Calcula métricas inspiradas em artigos de QA/RAG:
            - exact_match (bool)
            - semantic_similarity (0-1)
            - rougeL (0-1)
            - length (int)
            - fontes_ok (bool) se fontes existem (para RAG)
            - hallucination (bool) se similarity < 0.3
            """
            if not resposta_modelo:
                return {
                    "semantic_similarity": 0.0,
                    "rougeL": 0.0,
                    "length": 0,
                    "fontes_ok": bool(fontes),
                    "hallucination": True
                }


            # Similaridade semântica
            emb_modelo = create_embedding(resposta_modelo)
            emb_esperada = create_embedding(resposta_esperada)
            similarity = cosine_similarity(emb_modelo, emb_esperada)

            # ROUGE-L
            scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
            rougeL = scorer.score(resposta_esperada, resposta_modelo)["rougeL"].fmeasure

            return {
                "semantic_similarity": similarity,
                "rougeL": rougeL,
                "length": len(resposta_modelo.split()),
                "fontes_ok": bool(fontes),
                "hallucination": similarity < 0.3
            }

        # ========================
        # Avaliação
        # ========================

        def avaliar():
            resultados = []
            stats = {"puro": [], "rag": []}

            for q in PERGUNTAS_TESTE:
                pergunta = q["pergunta"]
                esperado = q["resposta_esperada"]

                # --- 1. LLM puro ---
                r_puro = requests.post(API_URL, json={"user_query": pergunta, "modo": True})
                resposta_pura = r_puro.json().get("answer", "")

                # --- 2. LLM com RAG ---
                r_rag = requests.post(API_URL, json={"user_query": pergunta, "modo": False})
                resposta_rag = r_rag.json().get("answer", "")
                fontes = r_rag.json().get("sources", [])

                # --- Métricas ---
                metrics_pura = avaliar_resposta(resposta_pura, esperado)
                metrics_rag = avaliar_resposta(resposta_rag, esperado, fontes)

                stats["puro"].append(metrics_pura)
                stats["rag"].append(metrics_rag)

                resultados.append({
                    "id": q["id"],
                    "pergunta": pergunta,
                    "resposta_esperada": esperado,
                    "resposta_pura": resposta_pura,
                    "resposta_rag": resposta_rag,
                    "fontes": fontes,
                    "metrics_pura": metrics_pura,
                    "metrics_rag": metrics_rag
                })

            # ========================
            # Agregação das métricas
            # ========================
            def aggregate(metrics_list):
                return {
                    "avg_similarity": np.mean([m["semantic_similarity"] for m in metrics_list]),
                    "avg_rougeL": np.mean([m["rougeL"] for m in metrics_list]),
                    "exact_match_rate": np.mean([m["exact_match"] for m in metrics_list]),
                    "hallucination_rate": np.mean([m["hallucination"] for m in metrics_list]),
                    "avg_length": np.mean([m["length"] for m in metrics_list]),
                    "source_coverage": np.mean([m["fontes_ok"] for m in metrics_list]),
                }

            resumo = {
                "LLM puro": aggregate(stats["puro"]),
                "LLM+RAG": aggregate(stats["rag"])
            }

            # Salvar tudo em um único JSON
            output = {
                "resultados_detalhados": resultados,
                "resumo_metricas": resumo
            }

            with open("avaliacao_completa.json", "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=2)

            print("✅ Avaliação concluída! Resultados em avaliacao_completa.json")
            print(json.dumps(resumo, indent=2, ensure_ascii=False))

        avaliar()


        self.stdout.write(self.style.SUCCESS("Testes do pipeline concluídos!"))