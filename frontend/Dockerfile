FROM node:21.7.1-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . ./
RUN npm run build

CMD sh -c "cp -r build/. /var/www/static/ && chmod -R 644 /var/www/static/ && find /var/www/static/ -type d -exec chmod 755 {} \; && echo 'Frontend static copied correctly'"