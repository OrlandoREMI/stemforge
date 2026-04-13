# syntax=docker/dockerfile:1.7

# --- deps ------------------------------------------------------------------
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json ./
# TODO: añadir package-lock.json y usar `npm ci` tras el primer install
RUN npm install --no-audit --no-fund

# --- builder ---------------------------------------------------------------
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# --- runner ----------------------------------------------------------------
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
USER nextjs

# next.config.mjs has `output: "standalone"` — copy the standalone bundle.
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

EXPOSE 3000
CMD ["node", "server.js"]
