# Press Release Agent 📰

A Masumi Network agent that writes professional press releases following AP Style and industry standards.

## What it does

Give it your company name, headline, key facts, and tone — it returns a fully formatted, publication-ready press release.

Supports four tones: `formal`, `startup`, `technical`, `consumer`

## Powered by MasumiForge

Scaffolded with [MasumiForge](https://github.com/enjojoy/masumiforge) — forge Masumi agents with OpenClaw.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Fill in OPENAI_API_KEY, PAYMENT_API_KEY, SELLER_VKEY
python agent.py
```

## Deploy

See [MasumiForge hosting guide](https://github.com/enjojoy/masumiforge/blob/main/skill/references/hosting.md) for DigitalOcean, Railway, Render, and Fly.io instructions.

## Register on Masumi

Once running at a public URL, register at `http://localhost:3001/admin` to list on [Sokosumi](https://sokosumi.com).
