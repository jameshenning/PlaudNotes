# How to Register the Railway Template (Repo Owner Only)

This is a one-time setup so the "Deploy on Railway" button works for everyone.

## Steps

1. Go to **[railway.com/button](https://railway.com/button)**
2. Paste your GitHub repo URL: `https://github.com/jameshenning/PlaudNotes`
3. Railway will detect the Dockerfile and create a template draft
4. Configure the required environment variables:

   | Variable | Required | Default Value | Description |
   |----------|----------|---------------|-------------|
   | `PLAUD_TOKEN` | Yes | *(empty)* | User's Plaud bearer token |
   | `PLAUD_MCP_API_KEY` | Yes | *(empty)* | User picks a secret password |
   | `PLAUD_TRANSPORT` | Yes | `http` | Leave as http |
   | `PLAUD_MCP_HOST` | Yes | `0.0.0.0` | Leave as 0.0.0.0 |
   | `PLAUD_REGION` | No | `us` | us or eu |

5. Set `PLAUD_TRANSPORT` and `PLAUD_MCP_HOST` as pre-filled defaults (users shouldn't need to change these)
6. Mark `PLAUD_TOKEN` and `PLAUD_MCP_API_KEY` as required with no default (users must fill these in)
7. Publish the template
8. Railway will give you a template URL like: `https://railway.com/template/XXXXXX`
9. Open `README.md` and replace the deploy button line:

   **Find this:**
   ```markdown
   [![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/new)
   ```

   **Replace with:**
   ```markdown
   [![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/template/XXXXXX)
   ```
   (Use your actual template URL)

10. Commit and push the change

## After This

The "Deploy on Railway" button will work for anyone — they click it, fill in their Plaud token and a password, and Railway handles everything else.
