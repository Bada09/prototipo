#!/usr/bin/env python3
"""
Gera os áudios do protótipo Rhapsody com as vozes da OpenAI (as mesmas do openai.fm).

Uso (no seu computador, na pasta do projeto):
    pip install openai
    export OPENAI_API_KEY="sua-chave"        # Windows PowerShell: $env:OPENAI_API_KEY="sua-chave"
    python generate_audio.py

Cria dois conjuntos de arquivos:
    audio/ia/        -> falas de Ricardo (a IA)
    audio/corretor/  -> falas do colaborador (o corretor)

Depois suba index.html e a pasta audio/ para o GitHub. A chave NÃO vai para o GitHub.
Para refazer um arquivo existente, use:  python generate_audio.py --force
Se mudar algum texto no index.html, copie o novo texto para FALAS abaixo e rode com --force.
"""
import argparse, os, sys
from pathlib import Path
from openai import OpenAI

MODEL = "gpt-4o-mini-tts"
VOZ_IA = "onyx"        # Ricardo. Outras masculinas: ash, echo, fable, verse
VOZ_CORRETOR = "coral" # Colaborador. Outras: nova, shimmer, sage, alloy

BASE = "Fale em português do Brasil, com sotaque paulistano natural e ritmo de conversa real, sem soar como locutor. "
RICARDO = BASE + "Você é Ricardo Mendes, empresário de 42 anos, conversando com um corretor de seguros. "
CORRETOR = BASE + "Você é um corretor de seguros experiente falando com um cliente. "

ESTILO = {
    "ia/abertura":     RICARDO + "Tom: desconfiado e direto, voz grave e firme, ritmo calmo, como quem testa o corretor.",
    "ia/1_boa":        RICARDO + "Tom: hesitante, mais lento e pensativo, com pequenas pausas.",
    "ia/1_fraca":      RICARDO + "Tom: irritado e impaciente, mais rápido e seco, voz grave.",
    "ia/2_boa":        RICARDO + "Tom: hesitante, mas começando a se abrir, pensativo, pausas curtas.",
    "ia/2_fraca":      RICARDO + "Tom: irritado e impaciente, mais rápido e seco, voz grave.",
    "ia/3_boa":        RICARDO + "Tom: aberto e receptivo, caloroso, ritmo natural.",
    "ia/3_fraca":      RICARDO + "Tom: frio e irritado, dispensando a conversa, mais rápido e grave.",
    "corretor/1_boa":  CORRETOR + "Tom: profissional, caloroso e confiante, com curiosidade genuína na pergunta.",
    "corretor/2_boa":  CORRETOR + "Tom: empático e calmo, fazendo a pergunta com cuidado.",
    "corretor/3_boa":  CORRETOR + "Tom: seguro e consultivo, propondo as opções com clareza.",
    "corretor/1_fraca": CORRETOR + "Tom: um pouco defensivo, tom de vendedor.",
    "corretor/2_fraca": CORRETOR + "Tom: apressado, tentando encerrar com a tabela.",
    "corretor/3_fraca": CORRETOR + "Tom: ansioso, oferecendo desconto para fechar logo.",
}

FALAS = {
    "ia/abertura": "Olha, vou ser direto com você: recebi uma proposta de outra seguradora com a parcela bem mais baixa. Por que eu pagaria mais para fechar com você?",
    "ia/1_boa": "Para ser sincero, eu olhei mais o valor da parcela. Acho que cobre morte e pouca coisa além disso. Mas seguro de vida é tudo igual, não é?",
    "ia/1_fraca": "Isso todo corretor fala. No fim do mês, o que pesa é a parcela. E seguro de vida é tudo igual, não é?",
    "corretor/1_boa": "Faz sentido comparar, Ricardo. Antes de falar de preço, posso te fazer uma pergunta? O que essa outra proposta cobre, exatamente, e por quanto tempo?",
    "corretor/1_fraca": "Nosso preço é justo, Ricardo. Somos uma das maiores seguradoras do mundo, e qualidade tem um custo.",
    "ia/2_boa": "Minha esposa e meus dois filhos. E a empresa depende de mim. Nunca tinha pensado em afastamento, só em morte. Mesmo assim, não queria aumentar meu custo fixo agora.",
    "ia/2_fraca": "Tabela eu já recebi de três corretores. E, olha, eu não quero aumentar meu custo fixo agora.",
    "corretor/2_boa": "Entendo essa impressão. Me conta uma coisa: hoje, quem depende da sua renda? Se você precisasse ficar seis meses afastado da empresa, como ficariam as contas de casa e do negócio?",
    "corretor/2_fraca": "Não é igual, não. O nosso tem muito mais coberturas. Posso te mandar a tabela completa por e-mail.",
    "ia/3_boa": "Assim fica mais fácil de comparar. Pode me mandar as duas simulações. Se fizer sentido, a gente fecha ainda esta semana.",
    "ia/3_fraca": "Se dá para baixar agora, é porque o preço estava alto antes. Vou pensar e te retorno.",
    "corretor/3_boa": "É justo. Que tal a gente simular duas opções agora? Uma com a mesma parcela da outra proposta, para você comparar o que cada uma cobre, e outra com proteção de renda em caso de afastamento. Você decide com os números na frente.",
    "corretor/3_fraca": "Se eu conseguir dez por cento de desconto com o meu gerente, a gente fecha hoje?"
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="refaz arquivos que já existem")
    args = ap.parse_args()
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Defina a variável OPENAI_API_KEY antes de rodar (veja o topo deste arquivo).")
    client = OpenAI()
    saida = Path(__file__).parent / "audio"
    feitos = 0
    for chave, texto in FALAS.items():
        destino = saida / (chave + ".mp3")
        if destino.exists() and not args.force:
            print("já existe, pulando:", destino.relative_to(saida.parent))
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        voz = VOZ_IA if chave.startswith("ia/") else VOZ_CORRETOR
        print("gerando:", destino.relative_to(saida.parent), "(voz %s)" % voz)
        with client.audio.speech.with_streaming_response.create(
            model=MODEL, voice=voz, input=texto,
            instructions=ESTILO[chave], response_format="mp3",
        ) as resp:
            resp.stream_to_file(destino)
        feitos += 1
    print("Pronto: %d arquivo(s) novo(s) em %s" % (feitos, saida))

if __name__ == "__main__":
    main()
