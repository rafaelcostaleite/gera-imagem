import os
import io
import zipfile
from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

# Criar pastas se não existirem
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Formatos de redes sociais (nome: (largura, altura))
SOCIAL_MEDIA_FORMATS = {
    'Instagram': {
        'Instagram Post (Quadrado)': (1080, 1080),
        'Instagram Story': (1080, 1920),
        'Instagram Reels': (1080, 1920),
        'Instagram Landscape': (1080, 566),
    },
    'Facebook': {
        'Facebook Post': (1200, 630),
        'Facebook Cover': (820, 312),
        'Facebook Story': (1080, 1920),
        'Facebook Event Cover': (1920, 1005),
    },
    'Google Ads': {
        'Medium Rectangle': (300, 250),
        'Leaderboard': (728, 90),
        'Wide Skyscraper': (160, 600),
        'Large Rectangle': (336, 280),
        'Half Page': (300, 600),
        'Large Leaderboard': (970, 90),
    },
    'LinkedIn': {
        'LinkedIn Post': (1200, 627),
        'LinkedIn Cover': (1584, 396),
        'LinkedIn Story': (1080, 1920),
    },
    'Twitter/X': {
        'Twitter Post': (1200, 675),
        'Twitter Header': (1500, 500),
    },
    'YouTube': {
        'YouTube Thumbnail': (1280, 720),
        'YouTube Banner': (2560, 1440),
    },
    'TikTok': {
        'TikTok Video': (1080, 1920),
    },
}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(image, target_size, maintain_aspect=True):
    """
    Redimensiona a imagem para o tamanho alvo.
    Se maintain_aspect=True, mantém a proporção e centraliza com fundo branco.
    """
    target_width, target_height = target_size

    if maintain_aspect:
        # Calcular proporção
        img_ratio = image.width / image.height
        target_ratio = target_width / target_height

        if img_ratio > target_ratio:
            # Imagem mais larga - ajustar pela largura
            new_width = target_width
            new_height = int(target_width / img_ratio)
        else:
            # Imagem mais alta - ajustar pela altura
            new_height = target_height
            new_width = int(target_height * img_ratio)

        # Redimensionar imagem
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Criar canvas com fundo branco
        canvas = Image.new('RGB', target_size, (255, 255, 255))

        # Centralizar imagem no canvas
        offset_x = (target_width - new_width) // 2
        offset_y = (target_height - new_height) // 2
        canvas.paste(resized, (offset_x, offset_y))

        return canvas
    else:
        # Redimensionar sem manter proporção (esticar)
        return image.resize(target_size, Image.Resampling.LANCZOS)

@app.route('/')
def index():
    return render_template('index.html', formats=SOCIAL_MEDIA_FORMATS)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de arquivo não permitido. Use PNG, JPG, JPEG ou WEBP'}), 400

    # Obter formatos selecionados
    selected_formats = request.form.getlist('formats[]')
    maintain_aspect = request.form.get('maintain_aspect', 'true') == 'true'

    if not selected_formats:
        return jsonify({'error': 'Selecione pelo menos um formato'}), 400

    try:
        # Abrir imagem
        image = Image.open(file.stream)

        # Converter para RGB se necessário
        if image.mode in ('RGBA', 'P'):
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'RGBA':
                rgb_image.paste(image, mask=image.split()[3])
            else:
                rgb_image.paste(image)
            image = rgb_image

        # Criar arquivo ZIP em memória
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for format_key in selected_formats:
                # Encontrar o tamanho correspondente
                platform, format_name = None, None
                for plat, formats in SOCIAL_MEDIA_FORMATS.items():
                    if format_key in formats:
                        platform = plat
                        format_name = format_key
                        size = formats[format_key]
                        break

                if size:
                    # Redimensionar imagem
                    resized = resize_image(image, size, maintain_aspect)

                    # Salvar em buffer
                    img_buffer = io.BytesIO()
                    resized.save(img_buffer, format='JPEG', quality=95)
                    img_buffer.seek(0)

                    # Adicionar ao ZIP
                    safe_name = format_name.replace(' ', '_').replace('/', '-')
                    zip_file.writestr(f'{safe_name}_{size[0]}x{size[1]}.jpg', img_buffer.getvalue())

        zip_buffer.seek(0)

        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name='redimensionadas.zip'
        )

    except Exception as e:
        return jsonify({'error': f'Erro ao processar imagem: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
