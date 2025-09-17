# Configuración de Producción - Servicio Web
## Customer Feedback Analyzer - LISTO PARA DEPLOY
### Fecha: 2025-09-17

---

## ✅ ESTADO: LISTO PARA PRODUCCIÓN

### Cambios Realizados:
1. ✅ Carpeta `web/src` duplicada ELIMINADA
2. ✅ Variables de entorno actualizadas para producción
3. ✅ API_PROXY_TARGET configurado con puerto 10000
4. ✅ Scripts de build verificados
5. ✅ NODE_ENV=production configurado

---

## 🚀 CONFIGURACIÓN PARA RENDER

### Servicio: `customer-feedback-app`

| Configuración | Valor |
|---------------|-------|
| **Service Type** | Web Service |
| **Environment** | Node |
| **Region** | Oregon |
| **Plan** | Starter |
| **Root Directory** | `.` (raíz del repositorio) |
| **Build Command** | `cd web && npm install && npm run build:render` |
| **Start Command** | `cd web && npm run start:prod` |
| **Port** | 3000 |
| **Health Check Path** | `/health` |
| **Node Version** | 20.11.0 |

---

## 🔧 VARIABLES DE ENTORNO PARA RENDER

### Variables Automáticas (desde render.yaml):
```yaml
NODE_ENV: production
NODE_VERSION: 20.11.0
PORT: 3000
```

### Variable CRÍTICA a configurar manualmente:
```bash
API_PROXY_TARGET=http://customer-feedback-api-bmjp:10000
```

**IMPORTANTE**: Usar puerto `10000` no `8000` para la comunicación interna.

---

## 📁 ESTRUCTURA DE ARCHIVOS FINAL

```
web/
├── server/
│   └── server.ts          # BFF con proxy configurado
├── client/
│   ├── src/              # Aplicación React (única carpeta src)
│   ├── dist/             # Build del cliente
│   └── package.json      # Dependencias del cliente
├── dist/                 # Build de producción
│   ├── server.js         # BFF compilado
│   └── client-build/     # React app compilado
├── .env                  # Configuración (gitignored)
├── .env.production       # Referencia producción
└── package.json          # Scripts y dependencias BFF
```

---

## 🔄 PROCESO DE BUILD

El comando `npm run build:render` ejecuta:

1. `npm ci --production=false` - Instala deps del BFF
2. `cd client && npm ci --production=false` - Instala deps del cliente
3. `npm run build` - Build de Vite (React optimizado)
4. `npx tsc server/server.ts --outDir dist` - Compila BFF
5. `cp -r client/dist dist/client-build` - Copia cliente al dist

**Resultado**: Carpeta `dist/` con todo listo para servir

---

## 🌐 FLUJO DE PRODUCCIÓN

```
Usuario
  ↓
https://customer-feedback-app.onrender.com
  ↓
[Web Service - Puerto 3000]
  ├─ Static Files → dist/client-build/
  │   ├─ index.html
  │   └─ assets/ (JS, CSS optimizados)
  └─ /api/* → Proxy
      ↓
  http://customer-feedback-api-bmjp:10000
      ↓
  [API Service Interno]
```

---

## ✨ CARACTERÍSTICAS EN PRODUCCIÓN

### Frontend:
- ✅ React SPA con routing
- ✅ Glassmorphism UI
- ✅ Tailwind CSS optimizado
- ✅ Code splitting automático
- ✅ Assets con cache headers

### BFF Server:
- ✅ Express con Helmet (seguridad)
- ✅ Compression activada
- ✅ Proxy API sin CORS
- ✅ Sirve React build
- ✅ Health endpoint

---

## 📋 CHECKLIST PRE-DEPLOY

### Archivos de configuración:
- [x] `web/.env` con NODE_ENV=production
- [x] `web/.env.production` actualizado
- [x] Puerto API correcto (10000)
- [x] Scripts build:render y start:prod

### Estructura:
- [x] Carpeta `web/src` eliminada
- [x] Solo existe `web/client/src`
- [x] Package.json con todas las deps

### En Render Dashboard:
- [ ] Verificar API_PROXY_TARGET
- [ ] Confirmar NODE_VERSION=20.11.0
- [ ] Health check en /health
- [ ] Auto-deploy activado

---

## 🔐 VARIABLES DE ENTORNO FINALES

```bash
# En web/.env y web/.env.production
NODE_ENV=production
PORT=3000
API_PROXY_TARGET=http://customer-feedback-api-bmjp:10000
NODE_VERSION=20.11.0
```

---

## 🎯 COMANDOS PARA VERIFICAR

### Build local de prueba:
```bash
cd web
npm run build:render
# Verificar que dist/ se crea correctamente
```

### Start local de producción:
```bash
cd web
NODE_ENV=production npm run start:prod
# Debe servir en puerto 3000
```

---

## ⚠️ NOTAS IMPORTANTES

1. **NO usar puerto 8000** para API_PROXY_TARGET
2. **USAR puerto 10000** que es donde escucha uvicorn
3. **NO commitear** archivos .env
4. **VERIFICAR** que solo existe `web/client/src`

---

## 🚀 ESTADO FINAL

El servicio web está **100% CONFIGURADO PARA PRODUCCIÓN** con:
- ✅ Estructura limpia sin duplicados
- ✅ Variables de entorno correctas
- ✅ Scripts de build optimizados
- ✅ Proxy API configurado correctamente
- ✅ UI hermosa y funcional

**LISTO PARA DEPLOY EN RENDER** 🎉

---

**Generado**: 2025-09-17
**Versión**: 3.1.0
**Estado**: PRODUCTION READY