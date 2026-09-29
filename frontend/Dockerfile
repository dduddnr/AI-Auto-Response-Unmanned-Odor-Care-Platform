FROM node:22-alpine

WORKDIR /app

COPY package*.json ./
# lock 파일 그대로, 패키지 해시(integrity) 검증하며 설치
RUN npm ci

COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
