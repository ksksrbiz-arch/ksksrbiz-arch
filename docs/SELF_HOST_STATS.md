# Self-Hosting the GitHub Stats Cards

The "GitHub Stats" and "Top Languages" cards in the README are rendered by
[`github-readme-stats`](https://github.com/anuraghazra/github-readme-stats).
This README already points at a **self-hosted** instance
(`github-stats-pi-tawny.vercel.app`) so it isn't subject to the rate limits of
the shared public instance (`github-readme-stats.vercel.app`), which is used by
millions and frequently returns `429 Too Many Requests` / `503` errors.

No cache-busting parameter is appended to these URLs. A scheduled workflow used
to add one daily, but it was removed in v6.2 along with the other Actions-based
workflows, so the cards are now cached by the stat host and by GitHub's image
proxy and refresh on their own schedule. To force a refresh by hand, append any
changing query parameter (for example `&cache_bust=2`) to the URLs in README.md.

If you ever move the cards to a different host, deploying your own free instance
on Vercel is a one-time, ~5 minute setup — the steps below walk through it.

## Steps

1. **Create a GitHub Personal Access Token (classic)**
   - Go to <https://github.com/settings/tokens> → *Generate new token (classic)*.
   - No scopes are required for public stats. (Tick `repo` only if you want
     private-contribution counts included.)
   - Copy the token — you'll paste it into Vercel as `PAT_1`.

2. **Deploy to Vercel** (one click)
   - Open: <https://vercel.com/new/clone?repository-url=https://github.com/anuraghazra/github-readme-stats>
   - When prompted for **Environment Variables**, add:
     - **Name:** `PAT_1`
     - **Value:** the token from step 1
   - Click **Deploy**. Vercel gives you a domain like
     `https://your-project-name.vercel.app`.

3. **Point the README at your instance**
   - In `README.md`, find the block marked `STATS HOST` and replace
     `github-readme-stats.vercel.app` in **both** image URLs with your new
     Vercel domain, e.g.:

     ```
     https://YOUR-PROJECT.vercel.app/api?username=ksksrbiz-arch&show_icons=true&hide_border=true&include_all_commits=true
     https://YOUR-PROJECT.vercel.app/api/top-langs/?username=ksksrbiz-arch&layout=compact&langs_count=8&hide_border=true
     ```

   - Commit and push. Done — your cards now render from your own rate-limit-free
     instance.

## Notes

- Keep `PAT_1` secret; if it leaks, revoke it in GitHub token settings.
- A `cache_bust` query param is harmless and works against a self-hosted
  instance too, if you ever want to add one manually.
- Vercel's free tier is more than enough for a personal profile README.
- Full docs: <https://github.com/anuraghazra/github-readme-stats#deploy-on-your-own>
