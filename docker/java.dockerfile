FROM eclipse-temurin:21
RUN mkdir /libs
ADD https://repo1.maven.org/maven2/com/google/code/gson/gson/2.11.0/gson-2.11.0.jar /libs/gson.jar

# Set a permanent, global classpath inside the image
ENV CLASSPATH=".:/libs/gson.jar"