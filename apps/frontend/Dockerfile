FROM node:22.16.0-alpine3.22 AS dependencies
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:22.16.0-alpine3.22 AS build
WORKDIR /app
COPY package*.json ./
COPY --from=dependencies /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:22.16.0-alpine3.22 AS production-deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev && npm cache clean --force

FROM node:22.16.0-alpine3.22
WORKDIR /app
COPY package*.json ./
COPY --from=production-deps /app/node_modules ./node_modules
COPY --from=build /app/build ./build
CMD ["npm", "run", "start"]