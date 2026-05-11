FROM nginx:alpine

COPY app/templates/ /usr/share/nginx/html/
COPY static/ /usr/share/nginx/static/
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
