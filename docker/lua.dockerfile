# Use Debian 12 (Bookworm) slim as the standard base
FROM debian:12-slim

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Lua 5.4, LuaRocks, and the build tools needed for libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    lua5.4 \
    liblua5.4-dev \
    luarocks \
    gcc \
    libc6-dev \
    make \
    # Install dkjson and bind it specifically to Lua 5.4
    && luarocks --lua-version=5.4 install dkjson \
    # Clean up package manager cache to save space
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Set up the execution entrypoint.
# We explicitly call 'lua5.4' since Debian version-tags the executable.
#   $1 = Path to the user's mounted Lua script
#   $2 = The raw JSON context string
ENTRYPOINT ["lua5.4"]