FROM rust:latest

WORKDIR /app

# 1. Create a dummy skeleton Cargo project
RUN cargo new --bin sandbox
WORKDIR /app/sandbox

# 2. Append the JSON dependencies to Cargo.toml
RUN echo 'serde = { version = "1.0", features = ["derive"] }' >> Cargo.toml && \
    echo 'serde_json = "1.0"' >> Cargo.toml

# 3. Pre-build the project once to permanently cache the JSON libraries inside the image
RUN cargo build --release

# 4. Give user 1000 ownership so your sandbox can compile scripts at runtime
RUN chown -R 1000:1000 /app/sandbox

# 5. Create the entrypoint wrapper script using portable printf
RUN printf '#!/bin/sh\n\
cp "$1" /app/sandbox/src/main.rs\n\
cd /app/sandbox\n\
cargo run --release --offline --quiet -- "$2"\n' > /usr/local/bin/run-rust && \
chmod +x /usr/local/bin/run-rust

ENTRYPOINT ["/usr/local/bin/run-rust"]