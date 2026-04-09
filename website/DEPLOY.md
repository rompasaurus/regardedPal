# Deployment Guide — GitHub Pages + Squarespace Domain

Step-by-step process to push the Dilder site live on GitHub Pages and point your Squarespace-registered domain at it.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Push the Repo to GitHub](#2-push-the-repo-to-github)
3. [Enable GitHub Pages](#3-enable-github-pages)
4. [Trigger the First Deployment](#4-trigger-the-first-deployment)
5. [Verify the Site is Live on github.io](#5-verify-the-site-is-live-on-githubio)
6. [Add the CNAME File](#6-add-the-cname-file)
7. [Configure DNS in Squarespace](#7-configure-dns-in-squarespace)
8. [Link the Domain in GitHub Pages](#8-link-the-domain-in-github-pages)
9. [Enable HTTPS](#9-enable-https)
10. [Update mkdocs.yml](#10-update-mkdocsyml)
11. [Verify Everything End-to-End](#11-verify-everything-end-to-end)
12. [How Redeployment Works Going Forward](#12-how-redeployment-works-going-forward)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Overview

What we are connecting:

```
Your machine
  └── git push → github.com/rompasaurus/dilder (main branch)
                    └── GitHub Actions runs mkdocs gh-deploy
                          └── Built HTML pushed to gh-pages branch
                                └── GitHub Pages serves gh-pages
                                      └── Squarespace DNS points your domain here
                                            └── https://yourdomain.com ✓
```

The workflow file `.github/workflows/deploy-site.yml` is already committed and handles the build automatically on every push to `main` that touches `website/`.

---

## 2. Push the Repo to GitHub

If you haven't pushed yet:

```bash
git push -u origin main
```

Confirm it landed at `github.com/rompasaurus/dilder`.

---

## 3. Enable GitHub Pages

1. Go to `github.com/rompasaurus/dilder`
2. Click **Settings** (top nav, not the gear on your profile)
3. In the left sidebar click **Pages**
4. Under **Build and deployment**:
   - Source: **GitHub Actions**
5. Click **Save**

> **Important:** Choose "GitHub Actions" not "Deploy from a branch". The workflow handles the branch push itself — if you pick "Deploy from a branch" GitHub will try to serve the wrong branch or conflict with the workflow.

---

## 4. Trigger the First Deployment

The workflow triggers on any push to `main` that touches `website/`. Make a trivial change to kick it off:

```bash
# From the dilder/ repo root
git commit --allow-empty -m "Trigger first GitHub Pages deployment"
git push
```

Or just push any pending change you already have.

**Watch the build:**

1. Go to `github.com/rompasaurus/dilder/actions`
2. Click the running workflow — **Deploy Site to GitHub Pages**
3. Watch the steps: Checkout → Setup Python → Install dependencies → Deploy
4. Green checkmark = success. Takes about 60–90 seconds.

---

## 5. Verify the Site is Live on github.io

Once the workflow completes, your site is live at:

```
https://rompasaurus.github.io/dilder/
```

Open it and check that pages load, the blog renders, and images appear. Do this before touching DNS — if something is broken, fix it at this stage before pointing your domain at it.

---

## 6. Add the CNAME File

This tells GitHub Pages which custom domain to expect. Without it, the domain gets wiped every time the workflow redeploys.

Create the file `website/docs/CNAME` containing only your domain name, no protocol, no trailing slash:

```
yourdomain.com
```

Replace `yourdomain.com` with your actual registered domain (e.g. `dilder.dev`).

Then commit and push:

```bash
git add website/docs/CNAME
git commit -m "Add CNAME for custom domain"
git push
```

Wait for the Actions build to finish — then the `CNAME` file will be present in the built `gh-pages` branch.

---

## 7. Configure DNS in Squarespace

This is the step that points your domain at GitHub's servers.

### Get to the DNS panel

1. Log into `account.squarespace.com`
2. Click **Domains** in the left sidebar
3. Click your domain name
4. Click **DNS** → **DNS Settings**

You will see a table of existing DNS records. You need to add the following.

---

### A Records — apex domain (e.g. `yourdomain.com`)

Add **four A records**, all pointing to GitHub's IP addresses:

| Type | Host | Data / Value | TTL |
|------|------|-------------|-----|
| A | `@` | `185.199.108.153` | 3600 |
| A | `@` | `185.199.109.153` | 3600 |
| A | `@` | `185.199.110.153` | 3600 |
| A | `@` | `185.199.111.153` | 3600 |

- **Host `@`** means the apex/root domain itself (e.g. `yourdomain.com`)
- All four IPs are GitHub's global CDN nodes — add all four for redundancy
- TTL 3600 = 1 hour, which is fine

---

### CNAME Record — www subdomain

Add one CNAME so `www.yourdomain.com` also works:

| Type | Host | Data / Value | TTL |
|------|------|-------------|-----|
| CNAME | `www` | `rompasaurus.github.io` | 3600 |

> **Note on Squarespace's default records:**
> Squarespace adds its own A records and CNAME for `@` and `www` when you register a domain through them. You need to **delete or replace** those existing records before adding the GitHub ones — having two conflicting A records for `@` will cause unpredictable routing.
>
> Look for any existing records with Host `@` or `www` pointing to Squarespace IP addresses (typically `198.185.159.x` or `198.49.23.x`) and delete them first.

---

### What it should look like after

| Type | Host | Value |
|------|------|-------|
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| CNAME | `www` | `rompasaurus.github.io` |

Everything else (MX records for email, TXT records for verification) can stay — don't touch those.

---

### Wait for propagation

DNS changes take anywhere from **5 minutes to 48 hours** to propagate globally. Usually under an hour in practice.

You can check current propagation status at:

```
https://dnschecker.org
```

Enter your domain and check the A record — when you see `185.199.108.153` appearing in most locations, it's ready.

---

## 8. Link the Domain in GitHub Pages

Once DNS is propagating (doesn't need to be 100% done):

1. Go to `github.com/rompasaurus/dilder/settings/pages`
2. Under **Custom domain**, type your domain: `yourdomain.com`
3. Click **Save**

GitHub will run a DNS check. It may show a warning like "DNS check in progress" — this is normal during propagation. Come back after 10–30 minutes and it should clear.

---

## 9. Enable HTTPS

GitHub provisions a free Let's Encrypt SSL certificate automatically once the DNS check passes.

1. Go back to **Settings → Pages**
2. Once the DNS check shows green, you will see **Enforce HTTPS** checkbox appear
3. Tick it
4. Wait ~5 minutes for the certificate to be issued

After this, `http://yourdomain.com` will automatically redirect to `https://yourdomain.com`.

---

## 10. Update mkdocs.yml

Now that you have a real domain, update the `site_url` so MkDocs generates correct canonical URLs and the sitemap:

Open `website/mkdocs.yml` and change line 2:

```yaml
site_url: https://yourdomain.com
```

Commit and push:

```bash
git add website/mkdocs.yml
git commit -m "Update site_url to production domain"
git push
```

---

## 11. Verify Everything End-to-End

Work through this checklist:

- [ ] `https://yourdomain.com` loads — no certificate warning
- [ ] `https://www.yourdomain.com` loads (www redirect works)
- [ ] `http://yourdomain.com` redirects to `https://` automatically
- [ ] Landing page renders correctly
- [ ] Blog index shows both posts
- [ ] Docs pages load with correct nav
- [ ] SVG concept renders display on the Enclosure Design page
- [ ] Dark/light mode toggle works
- [ ] No broken links (check the browser console for 404s)

---

## 12. How Redeployment Works Going Forward

You never need to manually deploy again. The process is:

```bash
# Make your changes (new blog post, doc update, etc.)
git add .
git commit -m "Add Phase 2 blog post"
git push
```

GitHub Actions automatically:
1. Detects the push to `main` touching `website/`
2. Spins up a fresh Ubuntu runner
3. Installs MkDocs Material from `requirements.txt`
4. Runs `mkdocs gh-deploy --force --clean`
5. Pushes the built HTML to `gh-pages`
6. GitHub Pages serves the new version

The site updates in about 60–90 seconds after you push. Check `github.com/rompasaurus/dilder/actions` to watch builds or diagnose failures.

---

## 13. Troubleshooting

### DNS check failing in GitHub Pages

- Check that old Squarespace A records for `@` are deleted
- Verify the four GitHub IPs are present using `dig yourdomain.com A`
- Wait longer — DNS can take up to 48h in edge cases

### "HTTPS not available yet"

- The certificate is provisioned automatically but takes up to 30 minutes after DNS validates
- The Enforce HTTPS checkbox won't appear until GitHub's check passes

### Site shows the old github.io URL after adding custom domain

- Make sure the `CNAME` file exists in `website/docs/CNAME` and was included in the last build
- Check the `gh-pages` branch directly on GitHub — look for a `CNAME` file at the root

### Build fails in Actions

- Go to `github.com/rompasaurus/dilder/actions`, click the failed run
- Expand the failing step to see the full error
- Common cause: `requirements.txt` out of sync — run `pip freeze > requirements.txt` locally and push

### www doesn't redirect to apex (or vice versa)

- GitHub Pages handles this automatically once both the A records and CNAME for `www` are set
- If it's not working, confirm the CNAME record in Squarespace points to `rompasaurus.github.io` (with the dot at the end, or without — either works)

### Domain shows Squarespace's default page

- Old Squarespace A records are still active — delete them and add only the four GitHub IPs

---

## Quick Reference — GitHub's IP Addresses

These are GitHub's current Pages IP addresses. They rarely change but you can always verify at `docs.github.com/pages`:

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```
