import openai
import tiktoken
import os
import requests
import shutil
import subprocess
from dotenv import load_dotenv
from pydub import AudioSegment
from PIL import Image
from instabot import Bot
from time import sleep

def ferramenta_ler_arquivo(nome_arquivo):
    try:
        with open(file=nome_arquivo, mode="r", encoding="utf-8") as arquivo:
            return arquivo.read()
    except IOError as e:
        print(f"Erro no carregamento de arquivo: {e}")

def ferramenta_download_imagem(nome_arquivo, imagem_gerada, qtd_imagens = 1):
  lista_nome_imagens = []
  try:
    for contador_imagens in range(0,qtd_imagens):
        caminho = imagem_gerada[contador_imagens].url
        imagem = requests.get(caminho)

        with open(f"{nome_arquivo}-{contador_imagens}.png", "wb") as arquivo_imagem:
            arquivo_imagem.write(imagem.content)

        lista_nome_imagens.append(f"{nome_arquivo}-{contador_imagens}.png")
    return lista_nome_imagens
  except:
    print("Ocorreu um erro!")
    return  None

def ferramenta_divide_audio_em_partes(caminho_audio_podcast, nome_arquivo, minutos_pedaco):
    print("O arquivo do conteúdo de audio é muito grande para o whisper e será divido em partes para transcrição. Iniciando corte .. ")
    audio = AudioSegment.from_mp3(caminho_audio_podcast)

    minutos = minutos_pedaco * 60 * 1000
    
    contador_pedaco = 1
    arquivos_exportados = []

    while len(audio) > 0:
        pedaco = audio[:minutos]
        nome_pedaco_audio = f"{nome_arquivo}_parte_{contador_pedaco}.mp3"
        pedaco.export(nome_pedaco_audio, format="mp3")
        arquivos_exportados.append(nome_pedaco_audio)
        audio = audio[minutos:]
        print(f"Corte do pedaço {contador_pedaco} concluido.")
        contador_pedaco += 1
    
    print(f"Divisão total do áudio em partes concluída.")
        
    return arquivos_exportados

def selecionar_imagem (lista_nome_imagens):
    return lista_nome_imagens[int(input("Qual imagem você deseja selecionar? Informe o sufixo da imagem selecionada."))]

def ferramenta_png2jpg(caminho_imagem_escolhida, nome_arquivo):
    img_png = Image.open(caminho_imagem_escolhida)
    img_png.save(caminho_imagem_escolhida.split(".")[0]+".jpg") 

    return caminho_imagem_escolhida.split(".")[0] + ".jpg"

def confirmacao_postagem(caminho_imagem_convertida, legenda_post):
    subprocess.run(["powershell", "-Command", f"Start-Process '{caminho_imagem_convertida}' -Verb open"])
    print(f"\Legenda: {legenda_post}")

    print("\n\nDeseja postar os dados acima no seu instagram? Digite 's' para sim e 'n' para não.")
    return input()

def ferramenta_conversao_binario_para_string(texto):
    if isinstance(texto, bytes):
        return str(texto.decode())
    return texto

def openai_whisper_transcrever(caminho_audio, nome_arquivo, modelo_whisper, client):
    print(f"Transcrevendo conteúdo de aúdio com o {modelo_whisper}...")

    conteudo_audio = open(caminho_audio, "rb")

    resposta = client.audio.transcriptions.create(file=conteudo_audio, model=modelo_whisper)
    print("Transcrição do conteúdo de aúdio realizada com sucesso") if resposta else None

    transcricao = resposta.text

    with open(f"texto_completo_{nome_arquivo}.txt", "w",encoding='utf-8') as arquivo_texto:
        arquivo_texto.write(transcricao)
    print(f"Arquivo 'texto_completo_{nome_arquivo}.txt' salvo com sucesso") if os.path.exists(f"texto_completo_{nome_arquivo}.txt") else None

    return transcricao

def openai_whisper_transcrever_em_partes(caminho_audio, nome_arquivo, minutos_pedaco, modelo_whisper, client):
    print(f"Transcrevendo conteúdo de aúdio com o {modelo_whisper}...")

    lista_arquivos_audio = ferramenta_divide_audio_em_partes(caminho_audio, nome_arquivo, minutos_pedaco)
    lista_pedacos_audio = []

    for pedaco_audio in lista_arquivos_audio:
        conteudo_audio = open(pedaco_audio, "rb")

        resposta = client.audio.transcriptions.create(file=conteudo_audio, model=modelo_whisper)
        print(f"Transcrição da parte {lista_arquivos_audio.index(pedaco_audio)+1} de {len(lista_arquivos_audio)} do conteúdo de aúdio realizada com sucesso") if resposta else None

        transcricao = resposta.text
        lista_pedacos_audio.append(transcricao)

    transcricao = "".join(lista_pedacos_audio)
    print("Transcrição total do conteúdo de aúdio em texto único realizada com sucesso") if resposta else None

    with open(f"texto_completo_{nome_arquivo}.txt", "w",encoding='utf-8') as arquivo_texto:
        arquivo_texto.write(transcricao)
    print(f"Arquivo 'texto_completo_{nome_arquivo}.txt' salvo com sucesso") if os.path.exists(f"texto_completo_{nome_arquivo}.txt") else None

    return transcricao

def openai_gpt_resumir_texto(transcricao_completa, nome_arquivo, quantidade_maxima_esperada_palavras_resumo, client):
    prompt_sistema = """
        Assuma que você é um digital influencer e que está divulgando conteúdos de um conteúdo de áudio (podcast) que você gostou muito e quer compartilhar com seus seguidores.

        Os textos produzidos devem levar em consideração uma peresona que consumirá os conteúdos gerados. Leve em consideração:

        - Seus seguidores são pessoas progressistas, interessadas em questões sociais relacionadas ao tema aborado no conteúdo de aúdio e que amam consumir conteúdos relacionados aos principais temas dessas áreas.
        - Você deve utilizar o gênero neutro na construção do seu texto
        - Os textos serão utilizados para convidar pessoas do instagram para consumirem o conteúdo de áudio
        - O texto deve ser escrito em português do Brasil.
    """
    prompt_usuario = f"\nReescreva a transcrição acima para que possa ser postado como uma legenda do Instagram. Ela deve resumir o texto para chamada na rede social com o limite máximo de {str(quantidade_maxima_esperada_palavras_resumo)} palavras. Inclua hashtags"

    codificador = tiktoken.encoding_for_model("gpt-3.5-turbo")
    qtde_tokens = (len(codificador.encode(transcricao_completa + prompt_sistema + prompt_usuario))) + (quantidade_maxima_esperada_palavras_resumo * 2)
    modelo_gpt_resumo = "gpt-3.5-turbo" if qtde_tokens < 4096 else "gpt-3.5-turbo-16k"
    print(f"Resumindo para um post no Instagram com o {modelo_gpt_resumo}...")

    resposta = client.chat.completions.create(
        model= modelo_gpt_resumo,
        messages=[
            {
                "role": "system",
                "content": prompt_sistema
            },
            {
                "role": "user",
                "content": transcricao_completa + prompt_usuario
            }
        ],
        temperature= 0.6
    )
    print("Resumo da transcriçao do conteúdo de aúdio realizado com sucesso") if resposta else None

    resumo_instagram = resposta.choices[0].message.content
    with open(f"resumo_instagram_{nome_arquivo}.txt", "w",encoding='utf-8') as arquivo_texto:
        arquivo_texto.write(resumo_instagram)
    print(f"Arquivo 'resumo_instagram_{nome_arquivo}.txt' salvo com sucesso") if os.path.exists(f"resumo_instagram_{nome_arquivo}.txt") else None

    return resumo_instagram

def openai_gpt_criar_hashtag(resumo_instagram, nome_arquivo, client):
    print(f"Gerando as hashtags com o gpt-3.5-turbo...")

    prompt_sistema = """
        Assuma que você é um digital influencer e que está divulgando conteúdos de um conteúdo de áudio (podcast) que você gostou muito e quer compartilhar com seus seguidores.

        Os textos produzidos devem levar em consideração uma peresona que consumirá os conteúdos gerados. Leve em consideração:

        - Seus seguidores são pessoas interessadas em questões sociais relacionadas ao tema aborado no conteúdo de aúdio e que amam consumir conteúdos relacionados aos principais temas dessas áreas.
        - Você deve utilizar o gênero neutro na construção do seu texto
        - Os textos serão utilizados para convidar pessoas do instagram para consumirem o conteúdo de áudio
        - O texto deve ser escrito em português do Brasil.
        - A saída deve conter 5 hashtags
    """

    prompt_usuario = f"""
    Aqui está um resumo de um texto:
    '{resumo_instagram}'.
    
    Gere 5 hashtags que sejam relevantes para este texto e que possam ser publicadas no Instagram. Faça em português do Brasil
    """

    resposta = client.chat.completions.create(
        model= "gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": prompt_sistema
            },
            {
                "role": "user",
                "content": prompt_usuario
            }
        ],
        temperature= 0.6
    )
    print("Geração de hashtags baseado no resumo da transcriçao do conteúdo de aúdio realizado com sucesso") if resposta else None

    hashtags = resposta.choices[0].message.content
    with open(f"hashtags_{nome_arquivo}.txt", "w",encoding='utf-8') as arquivo_texto:
        arquivo_texto.write(hashtags)
    print(f"Arquivo 'hashtags_{nome_arquivo}.txt' salvo com sucesso") if os.path.exists(f"hashtags_{nome_arquivo}.txt") else None

    return hashtags

def openai_gpt_gerar_texto_criar_imagem_instagram(resumo_instagram, nome_arquivo, client):
    print(f"Gerando texto para criação de imagens com o gpt-3.5-turbo...")

    prompt_sistema = """
        - Crie um prompt para o DALL-E com base no resumo de um podcast. O objetivo é gerar uma imagem representativa para um post de recomendação no Instagram. Certifique-se de incluir elementos visualmente atraentes que capturem a essência do conteúdo. Ao criar o prompt tenha atenção com palavras que podem ferir o 'safety system' por conter texto potencialmente ofensivo no prompt. A imagem gerada deve conter somente uma representação visual, sem textos e sem símbolos.
        - A sáida deve ser somente um texto, sem hashtags.
    """

    prompt_usuario =  f"""
        Resumo do Podcast: [{resumo_instagram}]

        Exemplo de saída:
        Crie uma imagem que represente [CONTINUAÇÃO]
    """

    resposta = client.chat.completions.create(
        model= "gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": prompt_sistema
            },
            {
                "role": "user",
                "content": prompt_usuario
            }
        ],
        temperature= 1
    )
    print("Geração de hashtags baseado no resumo da transcriçao do conteúdo de aúdio realizado com sucesso") if resposta else None

    texto_para_criar_imagem = resposta.choices[0].message.content
    with open(f"texto_gera_imagem_{nome_arquivo}.txt", "w",encoding='utf-8') as arquivo_texto:
        arquivo_texto.write(texto_para_criar_imagem)
    print(f"Arquivo 'texto_gera_imagem_{nome_arquivo}.txt' salvo com sucesso") if os.path.exists(f"texto_gera_imagem_{nome_arquivo}.txt") else None

    return texto_para_criar_imagem

def openai_dalle_gerar_imagem(resolucao, texto_criar_imagem_instagram, nome_arquivo, modelo_dalle_gerar_imagem, client, qtd_imagens=1):
    print(f"Gerando imagem com {modelo_dalle_gerar_imagem}...")

    prompt_user = texto_criar_imagem_instagram

    resposta = client.images.generate(
        model= modelo_dalle_gerar_imagem,
        prompt= prompt_user,
        size= resolucao,
        quality="standard",
        n= qtd_imagens
    )
    print("Geração da imagem realizada com sucesso") if resposta else None

    for i in range(qtd_imagens):
        print(f"Link da imagem {i}:\n{resposta.data[i].url}\n")
    return resposta.data

def postar_instagram(caminho_imagem, texto, user, password):
    if os.path.exists("config"):
        shutil.rmtree("config")
    bot = Bot()
    
    bot.login(username=user, password=password)
    sleep(2)
    resposta = bot.upload_photo(caminho_imagem, caption=texto)


def main():
    load_dotenv()
    client = openai.OpenAI()
    resolucao = "1024x1024"
    minutos_pedaco = 20
    quantidade_maxima_esperada_palavras_resumo = 100

    caminho_audio = str(os.getenv("AUDIO_PATH"))
    nome_arquivo = str(os.getenv("FILE_NAME"))
    url_podcast = str(os.getenv("AUDIO_URL"))

    usuario_instagram = str(os.getenv("USER_INSTAGRAM"))
    senha_instagram = str(os.getenv("PASSWORD_INSTAGRAM"))

    modelo_whisper = "whisper-1"
    tamanho_arquivo_audio = os.path.getsize(caminho_audio) / (1024 * 1024)
    if tamanho_arquivo_audio < 25:
        transcricao_completa = openai_whisper_transcrever(caminho_audio, nome_arquivo, modelo_whisper, client)
    else:
        transcricao_completa = openai_whisper_transcrever_em_partes(caminho_audio, nome_arquivo, minutos_pedaco, modelo_whisper, client)
    # transcricao_completa = ferramenta_ler_arquivo(f"texto_completo_{nome_arquivo}.txt")
    
    resumo_instagram = openai_gpt_resumir_texto(str(transcricao_completa), nome_arquivo, quantidade_maxima_esperada_palavras_resumo, client)
    # resumo_instagram = ferramenta_ler_arquivo(f"resumo_instagram_{nome_arquivo}.txt")
    
    hashtags = openai_gpt_criar_hashtag(resumo_instagram, nome_arquivo, client)
    # hashtags = ferramenta_ler_arquivo(f"hashtags_{nome_arquivo}.txt")

    texto_criar_imagem_instagram = openai_gpt_gerar_texto_criar_imagem_instagram(resumo_instagram, nome_arquivo, client)
    # texto_criar_imagem_instagram = ferramenta_ler_arquivo(f"texto_gera_imagem_{nome_arquivo}.txt")

    modelo_dalle_gerar_imagem = "dall-e-3"
    qtd_imagens = 1
    if modelo_dalle_gerar_imagem == "dall-e-3":
        qtd_imagens = 1
    imagem_gerada = openai_dalle_gerar_imagem(resolucao, texto_criar_imagem_instagram, nome_arquivo, modelo_dalle_gerar_imagem, client, qtd_imagens)
    lista_imagens_geradas = ferramenta_download_imagem(nome_arquivo, imagem_gerada, qtd_imagens)

    if qtd_imagens > 1:
        caminho_imagem_escolhida = selecionar_imagem (lista_imagens_geradas)
    else:
        caminho_imagem_escolhida = f"{nome_arquivo}-0.png"
    caminho_imagem_convertida = ferramenta_png2jpg(caminho_imagem_escolhida, nome_arquivo)

    legenda_post = f"{ferramenta_conversao_binario_para_string(resumo_instagram)} {ferramenta_conversao_binario_para_string(hashtags)} \n\nLink do podcast: {ferramenta_conversao_binario_para_string(url_podcast)}"

    if confirmacao_postagem(caminho_imagem_convertida, legenda_post).lower() == "s":
        print("Confirmou")
        postar_instagram(caminho_imagem_convertida,
                         legenda_post,
                         usuario_instagram,
                         senha_instagram)

if __name__ == "__main__":
    main()
