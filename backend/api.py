from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from tinydb import TinyDB, Query
from crewai import Agent, Task, Crew
import os

# Correção do caminho de importação a partir da raiz
from backend.sim_engine import inicializar_mundo, simular_ciclo_vida

# Configuração do Ollama
os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
os.environ["OPENAI_API_KEY"] = "ollama"
os.environ["OPENAI_MODEL_NAME"] = "llama3"

app = FastAPI(title="Crunch Time - Social Sim API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db = TinyDB('backend/database/world_state.json')
Membro = Query()
inicializar_mundo()

class InteracaoCEO(BaseModel):
    nome_npc: str
    tipo_acao: str  # "pressionar", "apoiar", "conversar_vida"
    mudanca_stress: int
    mudanca_motivacao: int

@app.get("/")
def status():
    return {"status": "Online", "tema": "Persistence in World Building & OCEAN Five"}

@app.get("/equipa")
def obter_equipa():
    """Devolve o estado completo de todos os NPCs (Stats, OCEAN, Vida Pessoal e Relações)."""
    return db.all()

@app.post("/interagir")
def interagir_com_npc(interacao: InteracaoCEO):
    """Processa a decisão do CEO, calcula o impacto baseado no OCEAN e gera a resposta."""
    resultado_busca = db.search(Membro.nome == interacao.nome_npc)
    if not resultado_busca:
        return {"erro": "NPC não encontrado."}
    
    npc = resultado_busca[0]
    ocean = npc['ocean']

    # 1. Cálculo Psicológico (OCEAN modula o impacto das decisões)
    mudanca_stress = interacao.mudanca_stress
    mudanca_mot = interacao.mudanca_motivacao

    if mudanca_stress > 0 and ocean['neuroticismo'] >= 70:
        mudanca_stress = int(mudanca_stress * 1.3)
    
    if mudanca_mot > 0 and ocean['amabilidade'] >= 75:
        mudanca_mot = int(mudanca_mot * 1.2)

    novo_stress = max(0, min(100, npc['stress'] + mudanca_stress))
    nova_motivacao = max(0, min(100, npc['motivacao'] + mudanca_mot))

    db.update({
        'stress': novo_stress,
        'motivacao': nova_motivacao
    }, Membro.nome == interacao.nome_npc)

    # 2. Preparar o Contexto para a IA (CrewAI)
    if interacao.tipo_acao == "pressionar":
        contexto_acao = "O CEO acabou de te pressionar por resultados e exigiu mais ritmo de trabalho."
    elif interacao.tipo_acao == "apoiar":
        contexto_acao = "O CEO elogiou o teu esforço e deu-te espaço para respirar e fazer uma pausa."
    else:
        contexto_acao = "O CEO veio meter conversa contigo para saber como estás e como vão as coisas fora do trabalho."

    # 3. Tentar chamar o Ollama; se estiver desligado/desinstalado, usa resposta simulada
    try:
        backstory_rica = (
            f"És o(a) {npc['nome']} ({npc['funcao']}) numa startup. "
            f"Os teus traços de personalidade OCEAN (0-100) são: Abertura={ocean['abertura']}, "
            f"Conscienciosidade={ocean['conscienciosidade']}, Extroversão={ocean['extroversao']}, "
            f"Amabilidade={ocean['amabilidade']}, Neuroticismo={ocean['neuroticismo']}. "
            f"A tua vida pessoal: {npc['vida_pessoal']} "
            f"O que te aconteceu recentemente fora/dentro do trabalho: '{npc['ultimo_evento']}'. "
            f"Estado atual: Stress a {novo_stress}%, Motivação a {nova_motivacao}%, Energia a {npc['energia']}%."
        )

        agente = Agent(
            role=f"{npc['nome']} da Startup",
            goal="Responder ao CEO de forma autêntica, refletindo a personalidade OCEAN, o nível de stress e a vida pessoal.",
            backstory=backstory_rica,
            allow_delegation=False,
            verbose=False
        )

        tarefa = Task(
            description=(
                f"{contexto_acao} Responde diretamente ao CEO em 1 ou 2 frases curtas. "
                f"Deixa transparecer o teu humor atual e menciona o que te aconteceu recentemente ('{npc['ultimo_evento']}'). "
                f"Não uses aspas nem descrições de ações. RESPONDE OBRIGATORIAMENTE EM PORTUGUÊS DE PORTUGAL."
            ),
            expected_output="Apenas a fala direta do personagem em Português de Portugal.",
            agent=agente
        )

        equipa_ia = Crew(agents=[agente], tasks=[tarefa], verbose=False)
        resposta_final = str(equipa_ia.kickoff())

    except Exception:
        # Modo de reserva (Fallback) para quando o Ollama não está instalado no PC
        if interacao.tipo_acao == "conversar_vida":
            resposta_final = f"[Modo Offline] Para ser sincero Chefe, ando um pouco afetado porque: {npc['ultimo_evento']}"
        elif novo_stress >= 70:
            resposta_final = f"[Modo Offline] Estou com o stress a {novo_stress}%! Além do trabalho, {npc['ultimo_evento'].lower()}"
        else:
            resposta_final = f"[Modo Offline] Obrigado pela compreensão, Chefe. Isto ajuda a equilibrar as coisas."

    return {
        "npc": npc['nome'],
        "novo_stress": novo_stress,
        "nova_motivacao": nova_motivacao,
        "resposta": resposta_final
    }

@app.post("/avancar-dia")
def avancar_dia():
    """Termina o dia de trabalho e simula a vida pessoal dos NPCs durante a noite."""
    acontecimentos = simular_ciclo_vida()
    return {
        "mensagem": "Um novo dia começou na startup! A vida pessoal dos NPCs avançou.",
        "resumo_noite": acontecimentos
    }