# Devcontainer image for Atari 2600 development
FROM --platform=linux/amd64 ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
# Base tools + dasm + python3 + virtual X server for Stella
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    dasm \
    python3 \
    python3-pip \
    unzip \
    nano \
    sudo \
    xvfb \
    libgl1-mesa-dri libglx-mesa0 \
  && rm -rf /var/lib/apt/lists/*

# Install Stella emulator from deb release
RUN curl -fsSL \
    https://github.com/stella-emu/stella/releases/download/7.0/stella_7.0_amd64.deb \
    -o /tmp/stella.deb \
  && apt-get update \
  && apt-get install -y --no-install-recommends /tmp/stella.deb \
  && rm /tmp/stella.deb \
  && rm -rf /var/lib/apt/lists/*

# Headless Stella disable audio
ENV SDL_AUDIODRIVER=dummy

# Create non-root dev user
RUN useradd -m -s /bin/bash dev \
  && usermod -aG sudo dev \
  && echo "dev ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER dev
WORKDIR /home/dev

# Create Stella config directory (required for sqlite database)
RUN mkdir -p /home/dev/.config/stella