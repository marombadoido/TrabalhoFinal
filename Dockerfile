# Imagem base completa do Debian
FROM debian:bullseye

# Variáveis de ambiente para evitar prompts de localização
ENV DEBIAN_FRONTEND=noninteractive

# Instalar pacotes básicos, ODBC e Python
RUN apt-get update && \
    apt-get install -y \
        curl \
        gnupg \
        apt-transport-https \
        ca-certificates \
        build-essential \
        unixodbc \
        unixodbc-dev \
        libgssapi-krb5-2 \
        libsasl2-modules-gssapi-mit \
        python3 \
        python3-pip \
        python3-dev \
        tzdata \
        locales

# Adicionar repositório e chave do Microsoft ODBC
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg && \
    echo "deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/microsoft.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list

# Instalar driver ODBC da Microsoft
RUN apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Definir local e fuso horário
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

# Copiar aplicação para o container
WORKDIR /app
COPY . /app

# Instalar dependências Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Expor a porta padrão do Flask
EXPOSE 5000

# Comando para rodar o Flask
CMD ["flask", "run", "--host=0.0.0.0"]
