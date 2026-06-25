# Publishing Megaphone to the Claude Code Marketplace

## What to upload

| File / Directory | Purpose |
|---|---|
| `skills/` | Nine skill files |
| `commands/` | Six command files |
| `assets/` | Icon and banner images |
| `bin/` | Helper scripts |
| `.claude-plugin/plugin.json` | Plugin manifest |
| `.claude-plugin/marketplace.json` | Registry entry |
| `README.md` | User-facing documentation |
| `CHANGELOG.md` | Version history |
| `LICENSE` | MIT license |

Do NOT upload: `.megaphone/`, `screenshots/`, `.git/`, `.gitignore`, `UPLOAD.md`.

## Marketplace submission steps

1. Ensure the repo is public on GitHub at `github.com/fernandoleyra/megaphone`
2. Tag the release:
   ```bash
   git tag v1.0.0
   git push origin main --tags
   ```
3. Create a GitHub Release from the tag with the CHANGELOG entry as release notes
4. Submit to the Claude Code plugin registry:
   - Plugin name: `megaphone`
   - Owner: `fernandoleyra`
   - Source: `https://github.com/fernandoleyra/megaphone`

## Install command (for users)

```
/plugin marketplace add fernandoleyra/megaphone
/plugin install megaphone
```

## Version bump instructions

1. Update `version` in `.claude-plugin/plugin.json`
2. Update the version badge in `README.md`
3. Add a new entry to `CHANGELOG.md`
4. Commit: `git commit -m "chore: bump version to X.Y.Z"`
5. Tag: `git tag vX.Y.Z && git push --tags`

## Verify install works

After pushing, test:
```
/plugin marketplace add fernandoleyra/megaphone
/plugin install megaphone
```
