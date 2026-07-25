# Deploy en OCI Compute

Esta guía despliega el agente en una instancia de **OCI Compute** (capa "Always Free"
es suficiente) usando Docker, para que quede accesible públicamente por HTTP.

## 0. Prerrequisitos

- Una cuenta de OCI (Oracle Cloud) — la capa gratuita alcanza para este proyecto.
- El repositorio ya subido a GitHub.
- (Opcional) Una API key del proveedor de LLM que vayas a usar (Anthropic, OpenAI, etc.).
  Si no configurás ninguna, el agente corre en modo `mock` (sirve para demostrar el
  deploy, aunque no redacte respuestas con un LLM real).

## 1. Crear la instancia de cómputo

1. En la consola de OCI: **Menú ☰ → Compute → Instances → Create Instance**.
2. Nombre: `agente-clinica-vitalis`.
3. Imagen: **Canonical Ubuntu 22.04** (o la que prefieras).
4. Forma (*Shape*): `VM.Standard.E2.1.Micro` (Always Free) o `VM.Standard.A1.Flex`
   (Ampere, también Always Free con hasta 4 OCPU / 24 GB).
5. En **Networking**, asegurate de que la instancia tenga una **IP pública asignada**.
6. Agregá tu clave pública SSH (o generá un par nuevo desde la consola).
7. Creá la instancia y anotá la **IP pública** una vez que esté en estado *Running*.

## 2. Abrir el puerto en la red (Security List / NSG)

1. Andá a la VCN asociada a la instancia: **Networking → Virtual Cloud Networks**.
2. Entrá a la **Security List** (o **Network Security Group**) de la subred pública.
3. Agregá una **Ingress Rule**:
   - Source CIDR: `0.0.0.0/0`
   - Protocolo: TCP
   - Puerto de destino: `8000` (o `80` si vas a poner Nginx delante, ver paso 6).

## 3. Conectarse por SSH e instalar Docker

```bash
ssh -i tu_clave.pem ubuntu@<IP_PUBLICA>

# En la instancia:
sudo apt update
sudo apt install -y docker.io git
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
# Cerrá sesión y volvé a entrar para que el grupo docker tome efecto
```

## 4. Clonar el repositorio y construir la imagen

```bash
git clone https://github.com/<tu-usuario>/agente-clinica-vitalis.git
cd agente-clinica-vitalis
docker build -t agente-clinica .
```

## 5. Correr el contenedor

Modo `mock` (sin API key, para verificar rápido que el deploy funciona):
```bash
docker run -d --name agente-clinica \
  -p 8000:8000 \
  --restart unless-stopped \
  agente-clinica
```

Con un LLM real (ejemplo con Anthropic/Claude):
```bash
docker run -d --name agente-clinica \
  -p 8000:8000 \
  -e LLM_BACKEND=anthropic \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  --restart unless-stopped \
  agente-clinica
```

## 6. Verificar que quedó accesible

Desde tu propia computadora (no desde la instancia):
```bash
curl http://<IP_PUBLICA>:8000/salud
```

Y desde el navegador, entrá a:
```
http://<IP_PUBLICA>:8000
```

Deberías ver la interfaz de chat de "Clínica Vitalis". **Esa URL (o una captura de
pantalla de esa página) es lo que va en el README como evidencia del deploy.**

## 7. (Opcional pero recomendado) Nginx + dominio + HTTPS

Si querés exponerlo en el puerto 80/443 con un dominio propio:
```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```
Configurá un `server block` que haga proxy_pass a `http://127.0.0.1:8000`, apuntá
tu dominio a la IP pública, y corré `certbot --nginx` para el certificado SSL.

## 8. Actualizar el deploy cuando cambia el código

```bash
git pull
docker build -t agente-clinica .
docker stop agente-clinica && docker rm agente-clinica
docker run -d --name agente-clinica -p 8000:8000 --restart unless-stopped agente-clinica
```

## Troubleshooting

| Problema | Causa probable | Solución |
|---|---|---|
| `curl` no responde desde afuera | Puerto no abierto en la Security List/NSG | Revisar paso 2 |
| `curl` no responde ni siquiera con `localhost` en la instancia | El contenedor no arrancó | `docker logs agente-clinica` |
| El agente responde en modo `mock` aunque configuraste una key | Variable de entorno mal escrita o no pasada al `docker run` | Revisar `docker inspect agente-clinica \| grep -A5 Env` |
| `Connection refused` en el puerto 8000 | Firewall interno de Ubuntu (`ufw`) bloqueando | `sudo ufw allow 8000` |
