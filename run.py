from app.app import create_app
import os

app = create_app()

# Verifica se estamos no ambiente de desenvolvimento local
if __name__ == "__main__":
    # Utiliza as variáveis de ambiente fornecidas pelo Vercel
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))

    # Inicia o aplicativo no servidor de desenvolvimento
    app.run(host=host, port=port)
s