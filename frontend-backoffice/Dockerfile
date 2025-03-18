# Étape 1 : Construire l'application Angular
FROM node:18 AS build

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers package.json et package-lock.json
COPY package*.json ./

# Installer les dépendances
RUN npm install

# Copier tout le projet
COPY . .

# Construire l'application Angular
RUN npm run build --prod

# Étape 2 : Servir avec Nginx
FROM nginx:alpine

# Copier les fichiers de build Angular dans Nginx
COPY --from=build /app/dist/frontend-backoffice /usr/share/nginx/html

# Ajouter une configuration Nginx personnalisée
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exposer le port 80
EXPOSE 80

# Lancer Nginx
CMD ["nginx", "-g", "daemon off;"]
