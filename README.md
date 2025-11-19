# Redimensionador de Artes para Redes Sociais

Aplicativo web que transforma artes de marketing em diversos tamanhos para que sejam utilizados em diferentes plataformas e redes sociais.

## Funcionalidades

- Upload de imagens (PNG, JPG, JPEG, WEBP)
- Redimensionamento automático para múltiplos formatos
- Suporte para as principais redes sociais:
  - Instagram (Post, Story, Reels, Landscape)
  - Facebook (Post, Cover, Story, Event Cover)
  - Google Ads (diversos tamanhos de banners)
  - LinkedIn (Post, Cover, Story)
  - Twitter/X (Post, Header)
  - YouTube (Thumbnail, Banner)
  - TikTok (Video)
- Opção de manter proporção da imagem original
- Download de todas as imagens redimensionadas em um arquivo ZIP
- Interface intuitiva com drag & drop

## Formatos Suportados

### Instagram
- Post (Quadrado): 1080×1080px
- Story: 1080×1920px
- Reels: 1080×1920px
- Landscape: 1080×566px

### Facebook
- Post: 1200×630px
- Cover: 820×312px
- Story: 1080×1920px
- Event Cover: 1920×1005px

### Google Ads
- Medium Rectangle: 300×250px
- Leaderboard: 728×90px
- Wide Skyscraper: 160×600px
- Large Rectangle: 336×280px
- Half Page: 300×600px
- Large Leaderboard: 970×90px

### LinkedIn
- Post: 1200×627px
- Cover: 1584×396px
- Story: 1080×1920px

### Twitter/X
- Post: 1200×675px
- Header: 1500×500px

### YouTube
- Thumbnail: 1280×720px
- Banner: 2560×1440px

### TikTok
- Video: 1080×1920px

## Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passos

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd gera-imagem
```

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Como Usar

1. Inicie o servidor:
```bash
python app.py
```

2. Acesse no navegador:
```
http://localhost:5000
```

3. Siga os passos na interface:
   - Faça upload da sua arte de marketing
   - Selecione os formatos desejados
   - Escolha se deseja manter a proporção da imagem
   - Clique em "Gerar Imagens Redimensionadas"
   - Baixe o arquivo ZIP com todas as imagens

## Opções de Redimensionamento

### Manter Proporção (padrão)
Quando ativada, a imagem original é redimensionada mantendo sua proporção. Se necessário, bordas brancas são adicionadas para preencher o tamanho final.

### Esticar Imagem
Quando desativada, a imagem é esticada para preencher completamente o tamanho alvo, podendo distorcer a imagem original.

## Estrutura do Projeto

```
gera-imagem/
├── app.py              # Aplicação Flask principal
├── requirements.txt    # Dependências Python
├── templates/
│   └── index.html     # Interface web
├── static/
│   └── style.css      # Estilos CSS
├── uploads/           # Pasta temporária para uploads (criada automaticamente)
└── output/            # Pasta temporária para saída (criada automaticamente)
```

## Tecnologias Utilizadas

- **Backend**: Flask (Python)
- **Processamento de Imagens**: Pillow (PIL)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

## Limitações

- Tamanho máximo de arquivo: 16MB
- Formatos aceitos: PNG, JPG, JPEG, WEBP

## Próximas Melhorias

- [ ] Adicionar mais formatos de redes sociais
- [ ] Permitir personalização de tamanhos
- [ ] Opção de adicionar marca d'água
- [ ] Visualização prévia dos redimensionamentos
- [ ] Suporte para processamento em lote
- [ ] Opção de escolher cor de fundo (além de branco)
- [ ] Suporte para imagens PNG com transparência

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## Licença

Este projeto está disponível para uso livre.
