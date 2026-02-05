# Devcontainer image for Atari 2600 development
FROM ubuntu:24.04

# Base tools + Atari tools
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      git \
      dasm \
      stella \
      python3 \
      python3-pip \
      unzip \
      nano \
      sudo \
  && rm -rf /var/lib/apt/lists/*

# Create non-root dev user
RUN useradd -m -s /bin/bash dev \
  && usermod -aG sudo dev \
  && echo "dev ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER dev
WORKDIR /home/dev
