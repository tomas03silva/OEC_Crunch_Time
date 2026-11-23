import random
from tinydb import TinyDB, Query

# Caminho para a nova base de dados
db = TinyDB('backend/database/world_state.json')
Membro = Query()

# Eventos que podem acontecer fora da empresa (Vida Pessoal)
EVENTOS_VIDA_PESSOAL = [
    {"evento": "Teve uma noite de insónias por causa do barulho dos vizinhos.", "impacto_stress": 15, "impacto_energia": -20},
    {"evento": "Discutiu com o(a) parceiro(a) ontem à noite.", "impacto_stress": 25, "impacto_energia": -10},
    {"evento": "O carro avariou a caminho do escritório e apanhou chuva.", "impacto_stress": 20, "impacto_energia": -15},
    {"evento": "Fez uma sessão de ginásio incrível e dormiu 8 horas seguidas.", "impacto_stress": -15, "impacto_energia": 20},
    {"evento": "Recebeu uma boa notícia de um amigo de infância.", "impacto_stress": -10, "impacto_energia": 10},
    {"evento": "Ficou a jogar videojogos até às 4 da manhã.", "impacto_stress": -5, "impacto_energia": -25},
    {"evento": "Teve um jantar de família muito tranquilo.", "impacto_stress": -10, "impacto_energia": 10}
]

def inicializar_mundo():
    """Cria os 4 NPCs com perfis OCEAN e vidas próprias se a base de dados estiver vazia."""
    if len(db.all()) > 0:
        return  # O mundo já existe, não sobrescreve

    equipa_inicial = [
        {
            "nome": "Programador",
            "funcao": "Backend",
            "asset": "prog",
            "stress": 30,
            "motivacao": 65,
            "energia": 80,
            "ocean": {
                "abertura": 45,          # Prefere rotinas e código estruturado
                "conscienciosidade": 85, # Muito focado e perfeccionista
                "extroversao": 25,       # Introvertido, prefere estar no seu canto
                "amabilidade": 60,       # Cooperativo, mas direto
                "neuroticismo": 75       # Ansioso, absorve muito stress
            },
            "vida_pessoal": "Vive sozinho com dois gatos. Tem tendência para procrastinar a dormir.",
            "ultimo_evento": "Começou a semana focado na arquitetura do servidor.",
            "relacoes": {"Designer": 75, "Marketeer": 45, "Estagiario": 60}
        },
        {
            "nome": "Designer",
            "funcao": "UI/UX",
            "asset": "des",
            "stress": 20,
            "motivacao": 80,
            "energia": 85,
            "ocean": {
                "abertura": 90,          # Extremamente criativa e aberta a novas ideias
                "conscienciosidade": 60, # Organizada, mas por vezes caótica no processo
                "extroversao": 75,       # Sociável, gosta de conversar no escritório
                "amabilidade": 80,       # Muito empática com os colegas
                "neuroticismo": 50       # Equilibrada emocionalmente
            },
            "vida_pessoal": "Partilha apartamento com amigos artistas. Adora visitar exposições.",
            "ultimo_evento": "Encontrou inspiração num novo estilo de Pixel Art.",
            "relacoes": {"Programador": 75, "Marketeer": 70, "Estagiario": 85}
        },
        {
            "nome": "Marketeer",
            "funcao": "Produto",
            "asset": "mark",
            "stress": 35,
            "motivacao": 75,
            "energia": 90,
            "ocean": {
                "abertura": 70,          # Gosta de tendências e novidades
                "conscienciosidade": 70, # Ambicioso e orientado a metas
                "extroversao": 95,       # Extremamente extrovertido e comunicativo
                "amabilidade": 40,       # Competitivo, por vezes egoísta
                "neuroticismo": 30       # Muito resistente ao stress e à pressão
            },
            "vida_pessoal": "Frequenta eventos de networking e ginásio todos os dias.",
            "ultimo_evento": "Fechou uma parceria promissora durante um jantar.",
            "relacoes": {"Programador": 45, "Designer": 70, "Estagiario": 50}
        },
        {
            "nome": "Estagiario",
            "funcao": "QA Testing",
            "asset": "qa",
            "stress": 40,
            "motivacao": 85,
            "energia": 75,
            "ocean": {
                "abertura": 80,          # Curioso e ansioso por aprender
                "conscienciosidade": 50, # Ainda a aprender a gerir o tempo
                "extroversao": 60,       # Amigável e falador
                "amabilidade": 90,       # Quer agradar a toda a gente
                "neuroticismo": 80       # Muito inseguro e facilmente intimidado
            },
            "vida_pessoal": "Está a acabar a tese de mestrado à noite enquanto estagia.",
            "ultimo_evento": "Passou a noite a tentar corrigir um bug na tese.",
            "relacoes": {"Programador": 60, "Designer": 85, "Marketeer": 50}
        }
    ]

    db.insert_multiple(equipa_inicial)
    print("Mundo inicializado com perfis OCEAN e vidas pessoais!")

def simular_ciclo_vida():
    """Simula o que acontece fora do trabalho e as interações sociais entre a equipa."""
    equipa = db.all()
    resumo_noite = []

    for npc in equipa:
        # 1. Evento Aleatório de Vida Pessoal
        evento = random.choice(EVENTOS_VIDA_PESSOAL)
        
        # O traço NEUROTICISMO amplifica o stress negativo e reduz o alívio positivo!
        fator_neuroticismo = npc['ocean']['neuroticismo'] / 50.0  # Entre 0.0 e 2.0
        
        mudanca_stress = evento['impacto_stress']
        if mudanca_stress > 0:
            mudanca_stress = int(mudanca_stress * fator_neuroticismo)
        
        novo_stress = max(0, min(100, npc['stress'] + mudanca_stress))
        nova_energia = max(10, min(100, npc['energia'] + evento['impacto_energia']))
        
        # 2. Dinâmica Social (Contágio Emocional)
        # Se um colega extrovertido estiver muito stressado, passa stress aos amigos próximos
        nota_social = ""
        for outro in equipa:
            if outro['nome'] != npc['nome']:
                afinidade = npc['relacoes'].get(outro['nome'], 50)
                if outro['stress'] >= 75 and afinidade >= 70:
                    novo_stress = min(100, novo_stress + 5)
                    nota_social = f" Ficou preocupado(a) ao ver o(a) {outro['nome']} tão exausto(a)."

        historico_atualizado = f"{evento['evento']}{nota_social}"

        db.update({
            'stress': novo_stress,
            'energia': nova_energia,
            'ultimo_evento': historico_atualizado
        }, Membro.nome == npc['nome'])

        resumo_noite.append({
            "npc": npc['nome'],
            "acontecimento": historico_atualizado,
            "novo_stress": novo_stress,
            "nova_energia": nova_energia
        })

    return resumo_noite

if __name__ == "__main__":
    inicializar_mundo()