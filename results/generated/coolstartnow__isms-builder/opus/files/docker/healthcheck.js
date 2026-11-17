// ISMS Builder – Docker HEALTHCHECK: the public login page must answer (HTTP or HTTPS, depending on SSL_* vars).
'use strict'
const useTls = !!(process.env.SSL_CERT_FILE && process.env.SSL_KEY_FILE)
const client = require(useTls ? 'https' : 'http')

const req = client.get({
  host: '127.0.0.1',
  port: Number(process.env.PORT) || 3000,
  path: '/ui/login.html',
  rejectUnauthorized: false,   // local loopback check; certificate is issued for the public host name
  timeout: 4000,
}, res => {
  res.resume()
  process.exit(res.statusCode >= 200 && res.statusCode < 400 ? 0 : 1)
})
req.on('timeout', () => { req.destroy(); process.exit(1) })
req.on('error', () => process.exit(1))
