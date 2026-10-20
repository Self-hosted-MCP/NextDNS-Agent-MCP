# Setup on your own server

For people used to servers: any Linux machine with Docker, at home or rented. About 15 minutes. You get `https://your-domain` with a free certificate.

## With Docker Compose and Caddy

The repository has a [`docker-compose.yml`](../docker-compose.yml) that runs the server plus [Caddy](https://caddyserver.com), which gets and renews the HTTPS certificate by itself.

1. Point a domain (for example `dns.example.com`) at your server's IP address, and open ports 80 and 443.
2. Get the files:

   ```bash
   git clone https://github.com/Self-hosted-MCP/NextDNS-Agent-MCP.git
   ```

   ```bash
   cd NextDNS-Agent-MCP
   ```

3. Make a `.env` file next to `docker-compose.yml`:

   ```
   NEXTDNS_DOMAIN=dns.example.com
   LOGIN_PASSPHRASE=your passphrase, 6+ characters
   NEXTDNS_SECRET_KEY=some long random text, never change it
   ```

   A random secret key: `openssl rand -hex 32`.

4. Start it:

   ```bash
   docker compose up -d
   ```

5. Open `https://dns.example.com/settings`, sign in, paste your API key, choose the profile modes.
6. Connect your AI apps to `https://dns.example.com/mcp`: [connect-your-ai.md](connect-your-ai.md).

`docker-compose.yml` builds the image from the repository. To use the ready-made one instead, replace `build: .` with `image: ghcr.io/self-hosted-mcp/nextdns-agent-mcp:latest`.

## Behind your own reverse proxy

Already run nginx, Traefik or Caddy? Run only the server and point the proxy at port 8766:

```bash
docker run -d --name nextdns-agent-mcp --restart unless-stopped \
  -p 127.0.0.1:8766:8766 -v nextdns-data:/data \
  -e LOGIN_PASSPHRASE='your passphrase' -e NEXTDNS_SECRET_KEY='long random text' \
  -e PUBLIC_URL=https://dns.example.com \
  ghcr.io/self-hosted-mcp/nextdns-agent-mcp:latest
```

The proxy must pass the `Host` header through: the `/mcp` address only accepts requests for the host in `PUBLIC_URL` (and localhost).

## Without a domain: a tunnel

No domain or no open ports? Cloudflare Tunnel or Tailscale Funnel give the server a public HTTPS address. Set `PUBLIC_URL` to that address. See [setup-computer.md](setup-computer.md#on-your-phone-through-a-tunnel).

## Without Docker

Install it like on a computer ([setup-computer.md](setup-computer.md)) and run `nextdns-agent-mcp serve` as a service (systemd, for example), with `HOST=0.0.0.0` if a proxy on another machine reaches it.

## Backups of the server itself

Everything the server keeps is in the `/data` volume (`nextdns-data`): the saved API key (encrypted), logins, the change log and profile backups. Back up that volume and keep `NEXTDNS_SECRET_KEY` with it.

## Updates

With the ready-made image:

```bash
docker compose pull && docker compose up -d
```

With `build: .` (the default):

```bash
git pull && docker compose up -d --build
```

See [updates.md](updates.md).
