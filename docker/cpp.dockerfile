# Use the official Docker Hub GCC image as the default C++ base environment
FROM gcc:latest

# Create the include directory for third-party headers
RUN mkdir -p /usr/local/include/nlohmann

# Download the single-header version of nlohmann/json
# Placing it in /usr/local/include ensures it is automatically in g++'s default search path
RUN curl -L -s "https://github.com/nlohmann/json/releases/download/v3.11.3/json.hpp" \
    -o /usr/local/include/nlohmann/json.hpp

# Setup a clean working directory
WORKDIR /app

# Create a robust execution wrapper script.
# This script takes:
#   $1 = The absolute path to the user's mounted C++ file (e.g., /data/script.cpp)
#   $2 = The raw JSON context string
RUN printf '#!/bin/sh\n\
set -e\n\
g++ -O2 -std=c++20 -x c++ - -o /tmp/compiled_bin\n\
exec /tmp/compiled_bin "$@"\n' > /usr/local/bin/run-cpp && \
    chmod +x /usr/local/bin/run-cpp

# Configure the container to execute our compilation/runtime wrapper by default
ENTRYPOINT ["/usr/local/bin/run-cpp"]