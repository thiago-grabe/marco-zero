FROM node:22-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# API URL para build estático — proxy via nginx em runtime
ENV VITE_API_URL=/api
RUN npm run build

FROM nginx:alpine
# Copiar build estático
COPY --from=builder /app/dist /usr/share/nginx/html
# Copiar config do nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
