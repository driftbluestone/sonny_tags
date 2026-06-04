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
if [ -z "$1" ] || [ -z "$2" ]; then\n\
    echo "Error: Missing source file or JSON arguments." >&2\n\
    exit 1\n\
fi\n\
\n\
# Compile the user code using C++20 and O2 optimizations\n\
# Outputting straight to /tmp ensures a non-root user (1000) can write the binary safely\n\
g++ -O2 -std=c++20 "$1" -o /tmp/compiled_tag\n\
COMPILE_STATUS=$?\n\
\n\
if [ $COMPILE_STATUS -eq 0 ]; then\n\
    # Execute the compiled binary and pass the JSON string as argv[1]\n\
    /tmp/compiled_tag "$2"\n\
    RUN_STATUS=$?\n\
    rm -f /tmp/compiled_tag\n\
    exit $RUN_STATUS\n\
else\n\
    # Compilation failed; g++ has already outputted the syntax errors to stderr\n\
    exit $COMPILE_STATUS\n\
fi\n' > /usr/local/bin/run-cpp && \
chmod +x /usr/local/bin/run-cpp

# Configure the container to execute our compilation/runtime wrapper by default
ENTRYPOINT ["/usr/local/bin/run-cpp"]