FROM node:20-alpine AS builder

WORKDIR /app

# نسخ package files
COPY package*.json ./
RUN npm install

# نسخ المصادر وبناء التطبيق
COPY . .
RUN npm run build

# ===== مرحلة الإنتاج =====
FROM nginx:alpine

# نسخ ملفات البناء
COPY --from=builder /app/dist /usr/share/nginx/html

# نسخ إعدادات Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]