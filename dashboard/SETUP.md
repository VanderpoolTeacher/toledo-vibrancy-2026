# Dashboard Setup (Subfolder of toledo-vibrancy-2026)

The dashboard lives at `dashboard/` inside your existing `toledo-vibrancy-2026` repo. Because that repo already exists and is connected to GitHub, most of the setup is already done. You just need to:

1. Commit the new `dashboard/` folder once
2. Verify Pages serves it
3. Make sure git credentials are cached so the daily 5 AM task can push silently

## 1. First commit (one time)

Open Terminal and run:

```bash
cd "/Users/michaelvanderpool/Documents/GitHub/Toledo"

git add dashboard/
git commit -m "Add daily Toledo development dashboard"
git push
```

If `git push` succeeds without prompting for credentials, you're good — your existing credentials work and the daily task will be able to push too.

## 2. Verify Pages serves the dashboard

Your repo's Pages is already enabled (the Vibrancy map is live at https://vanderpoolteacher.github.io/toledo-vibrancy-2026/). Subfolders are automatically served, so the dashboard will appear at:

**https://vanderpoolteacher.github.io/toledo-vibrancy-2026/dashboard/**

Wait 1-2 minutes after pushing, then open that URL. You should see the dashboard with a "Live site" badge in the header.

## 3. If `git push` *did* prompt for credentials

You need a Personal Access Token cached in macOS Keychain.

1. Go to https://github.com/settings/tokens?type=beta (Fine-grained tokens)
2. Click **Generate new token**
   - Name: `Toledo Dashboard Deploy`
   - Expiration: 1 year (or No expiration)
   - Repository access: **Only select repositories** → `toledo-vibrancy-2026`
   - Permissions → Repository permissions → **Contents: Read and write**
3. Generate and **copy the token immediately**
4. Configure git and trigger one push:

```bash
git config --global credential.helper osxkeychain
cd "/Users/michaelvanderpool/Documents/GitHub/Toledo"
git push
# Username: VanderpoolTeacher
# Password: <paste PAT>
```

The token is now in Keychain. Future pushes (including from the daily 5 AM task) will use it automatically.

## 4. Pre-approve the scheduled task

In Cowork, open the **Scheduled** sidebar, find **toledo-daily-development-brief**, and click **Run now** once. This pre-approves any tool permissions so future 5 AM runs don't pause for approval prompts.

Confirm the live site updates after the run completes.

## Troubleshooting

**`git push` fails with 403:** PAT expired or missing Contents write permission. Regenerate at https://github.com/settings/tokens?type=beta.

**Pages 404 at `/dashboard/`:** Make sure `dashboard/index.html` is committed and pushed. Check at https://github.com/VanderpoolTeacher/toledo-vibrancy-2026/tree/main/dashboard

**Daily task says "Permission denied":** Token isn't cached. Re-run the `git push` step manually to re-prompt and re-cache.

## What lives where

- `dashboard/index.html` — the dashboard page
- `dashboard/followed_stories.json` — author's followed stories/people (read by the page; updated by the 5 AM task)
- `dashboard/archive/` — dated markdown briefs, one per day
- `dashboard/deploy.sh` — push helper run by the 5 AM task

The Vibrancy map at the repo root (`index.html`) is untouched and continues to live at the root URL.
