FROM nginx:1.24-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/

RUN mkdir -p /var/www/static /var/www/media

RUN chown -R nginx:nginx /var/www/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]