// Container-Healthcheck (vom Dockerfile per HEALTHCHECK aufgerufen).
// Prüft, ob der Server auf seinem Port antwortet. /api/version ist ohne Anmeldung erreichbar.
// Mit SSL_CERT_FILE spricht der Server HTTPS; ein selbst signiertes Zertifikat ist dann möglich,
// deshalb wird dort ohne Zertifikatsprüfung abgefragt (der Check dient nur der Erreichbarkeit).
'use strict'
const http = require('http')
const https = require('https')

const port = Number(process.env.PORT) || 3000
const lib = process.env.SSL_CERT_FILE ? https : http

const req = lib.get(
  { host: '127.0.0.1', port, path: '/api/version', rejectUnauthorized: false, timeout: 4000 },
  res => process.exit(res.statusCode === 200 ? 0 : 1)
)
req.on('timeout', () => req.destroy(new Error('timeout')))
req.on('error', () => process.exit(1))
