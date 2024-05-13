FROM debian:buster

RUN apt-get update && apt-get install -y curl

RUN apt-get update && \
 apt-get install -y \
    nodejs npm

RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs


RUN npm install -g ganache@7.9.2

WORKDIR /.

COPY start_ganache.sh .
RUN chmod +x start_ganache.sh

CMD ["./start_ganache.sh"]

# CMD ["ganache", "-h","0.0.0.0", "--db", "/ganache_db", "-m", "dizzy actress recipe trick gain desk future deliver bulk garage shaft arrow"]

