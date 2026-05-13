# frontend/Dockerfile
# ----------------------------------------------------------------------
# Development Dockerfile for the Next.js dashboard.
# A production multi-stage build comes in Phase 8 — this version
# prioritizes fast rebuilds and hot module reloading.
# ----------------------------------------------------------------------

FROM node:20-alpine

WORKDIR /app

# Copy ONLY the package manifests first so `npm install` is cached
# unless dependencies actually change. Without this trick, every code
# change re-runs the entire dependency install — adds minutes per rebuild.
COPY package.json ./
RUN npm install

# Now copy the rest of the source
COPY . .

EXPOSE 3000

# `next dev` enables hot module reloading — edits show up in the browser
# instantly without restarting anything.
CMD ["npm", "run", "dev"]