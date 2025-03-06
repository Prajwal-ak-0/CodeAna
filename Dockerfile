FROM ubuntu:22.04

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install essential dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    python3 \
    python3-pip \
    sudo \
    golang \
    docker.io \
    docker-compose \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add ~/.local/bin to PATH before installing Aider
ENV PATH="/root/.local/bin:${PATH}"

# Install Aider according to the user's instructions
RUN pip3 install aider aider-install && \
    # Run aider-install with retry mechanism
    (aider-install || (sleep 5 && aider-install) || (sleep 10 && aider-install))

# Find aider executable path and make it available in PATH
RUN which aider || echo "Aider not found in PATH, creating symlink if needed" && \
    if [ ! -f /usr/local/bin/aider ] && [ -d /root/.local/bin ] && [ -f /root/.local/bin/aider ]; then \
        ln -sf /root/.local/bin/aider /usr/local/bin/aider && \
        chmod +x /usr/local/bin/aider; \
    fi

# Install Bearer according to the instructions
RUN curl -sfL https://raw.githubusercontent.com/Bearer/bearer/main/contrib/install.sh | sh
ENV PATH="/root/.bearer/bin:${PATH}"

# Install Privado according to the exact steps provided
WORKDIR /root

# 1. Clone the Privado CLI repository with depth 1
RUN git clone --depth 1 https://github.com/SuchitG04/privado-cli.git

# 2. Create the Dockerfile.patched for the patched Privado image (will be built at runtime in entrypoint.sh)
RUN echo 'FROM public.ecr.aws/privado/privado:latest\n\
\n\
# Install necessary tools\n\
RUN apt-get update && apt-get install -y \\\n\
    curl \\\n\
    procps \\\n\
    && rm -rf /var/lib/apt/lists/*\n\
\n\
# Create a wrapper script for Java that disables container detection\n\
RUN echo '"'"'#!/bin/bash'"'"' > /usr/local/java/jdk-18.0.2/bin/java.wrapper && \\\n\
    echo '"'"'exec /usr/local/java/jdk-18.0.2/bin/java.real \\\n\
    -XX:-UseContainerSupport \\\n\
    -Djdk.internal.platform.useContainerSupport=false \\\n\
    "$@"'"'"' >> /usr/local/java/jdk-18.0.2/bin/java.wrapper && \\\n\
    chmod +x /usr/local/java/jdk-18.0.2/bin/java.wrapper\n\
\n\
# Rename the original Java binary and replace it with our wrapper\n\
RUN mv /usr/local/java/jdk-18.0.2/bin/java /usr/local/java/jdk-18.0.2/bin/java.real && \\\n\
    mv /usr/local/java/jdk-18.0.2/bin/java.wrapper /usr/local/java/jdk-18.0.2/bin/java\n\
\n\
# Set environment variables to disable container support\n\
ENV JAVA_TOOL_OPTIONS="-XX:-UseContainerSupport -Djdk.internal.platform.useContainerSupport=false"\n\
ENV _JAVA_OPTIONS="-XX:-UseContainerSupport -Djdk.internal.platform.useContainerSupport=false"\n\
' > /root/Dockerfile.patched

# 3. Build the privado binary from source
WORKDIR /root/privado-cli
RUN go build -o privado

# 4. Make the privado binary executable and add to PATH
RUN chmod +x /root/privado-cli/privado
ENV PATH="/root/privado-cli:${PATH}"

# Create a verification script
RUN echo '#!/bin/bash\n\
echo "==== Verifying Aider Installation ===="\n\
which aider\n\
if [ $? -ne 0 ]; then\n\
    echo "Aider not found in PATH. Checking if it exists in common locations:"\n\
    find /root -name aider -type f 2>/dev/null || echo "No aider executable found"\n\
    find /root -name aider-chat.py -type f 2>/dev/null || echo "No aider-chat.py found"\n\
else\n\
    aider --version || echo "Aider installed but version command failed"\n\
fi\n\
\n\
echo "==== Verifying Bearer Installation ===="\n\
which bearer\n\
bearer --version\n\
\n\
echo "==== Verifying Privado Installation ===="\n\
echo "1. Checking if privado binary is in PATH:"\n\
which privado || echo "privado not found in PATH"\n\
\n\
echo "2. Checking if privado-cli repository exists:"\n\
ls -la /root/privado-cli\n\
\n\
echo "3. Checking for privado-patched Docker image:"\n\
docker images | grep privado-patched || echo "privado-patched image not found"\n\
\n\
echo "4. Testing privado command:"\n\
cd /root/privado-cli && ./privado --help | head -n 5\n\
\n\
echo "==== Verifying Docker Installation ===="\n\
docker --version\n\
docker-compose --version\n\
\n\
echo "==== Verifying Go Installation ===="\n\
go version\n\
\n\
echo "==== All tools verified ===="\n\
' > /root/verify.sh && chmod +x /root/verify.sh

# Create a workspace directory
WORKDIR /workspace

# Set the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"] 