import streamlit as st
import qrcode
from io import BytesIO
import streamlit as st
import pandas as pd
import json
from io import BytesIO
import base64


# URL do sistema no Streamlit Cloud
link_sistema = "https://kmmorto-enec8ynngvbpnpmp8yk6pt.streamlit.app/"

# Função para gerar QR Code
def gerar_qr_code(link):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

# Gerar o QR Code
qr_image = gerar_qr_code(link_sistema)

# Converter o QR Code em bytes
buffer = BytesIO()
qr_image.save(buffer, format="PNG")
buffer.seek(0)  # Voltar ao início do buffer

# Exibir o QR Code no Streamlit
st.subheader("Acesse o sistema pelo QR Code")
st.image(buffer, caption="Escaneie para acessar o sistema", use_container_width=True)

# Salvar o QR Code como arquivo para impressão
qr_image.save("qr_code_sistema.png")
st.success("QR Code salvo como 'qr_code_sistema.png'")
