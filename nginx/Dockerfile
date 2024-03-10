FROM	debian:buster

RUN		apt-get update
RUN		apt-get install -y nginx openssl

RUN mkdir -p /etc/nginx/ssl

RUN openssl req -newkey rsa:4096 -x509 -sha256 -days 365 -nodes \
  -out /etc/nginx/ssl/minh-ngu.crt \
  -keyout /etc/nginx/ssl/minh-ngu.key \
  -subj "/C=FR/ST=Paris/L=Paris/O=42 School/OU=minh-ngu/CN=127.0.0.1/" \
  -addext "subjectAltName = IP:127.0.0.1"

RUN mkdir -p /app/config
RUN cp /etc/nginx/ssl/* /app/config

COPY ./conf/nginx.conf /etc/nginx/conf.d

RUN mkdir -p /run/nginx

EXPOSE 80
EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]