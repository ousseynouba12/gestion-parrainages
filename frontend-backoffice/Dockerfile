# Étape de construction
FROM node:20-alpine AS build
# Définir le répertoire de travail
WORKDIR /app
# Copier tout le contenu du répertoire courant
COPY . ./
# Installer les dépendances
RUN npm ci
# Construire l'application en mode production
RUN npm run build -- --configuration production
# Étape de production avec Nginx
FROM nginx:alpine
# Copier une configuration Nginx personnalisée pour les SPA Angular
RUN rm -rf /etc/nginx/conf.d/*
COPY <<EOF /etc/nginx/conf.d/default.conf
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;
    # Compression gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    # Angular routes handling
    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
EOF
# Copier les fichiers de build depuis l'étape précédente
COPY --from=build /app/dist/*/browser /usr/share/nginx/html
# Exposer le port 80
EXPOSE 80
# Démarrer Nginx
CMD ["nginx", "-g", "daemon off;"]
