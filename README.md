# A Place to Practise: public written review

This static site is a review draft. It preserves the goal-first walkthrough, skills library, and current written practice routes. The catalogue contains 83 cards; it is not a completed 83-skill treatment library. Some resources are planning placeholders or explicitly unavailable references.

Clinical, accessibility, browser and source-rights acceptance remain open. The methods have distinct source populations, prerequisites and limits, described within each resource. No blanket age or treatment-suitability claim is made.

Narration is not connected in this written build. Unreviewed recordings are separate. Disabled narration controls are not evidence of playable or approved audio. PDF downloads, selected artwork, comparison packages and internal review records are withheld with explicit notices.

Writing and temporary shortcuts follow each tool's stated behavior. Explicitly copied or downloaded notes remain outside the page after clearing. The site is not a monitored service and does not send answers to a therapist. Hosting services receive ordinary page and asset requests. A noindex instruction is not access control.

## Verify and deploy

This compact repository stores the exact sanitized site source in `site-runtime.zip`. Run `python3 build-site.py` from a clean checkout. It verifies the manifest and archive, safely extracts the static source into `site/`, then checks every file, local HTML dependency and static size. The script refuses to merge into an existing `site/` directory. The Pages workflow uploads only `site/`. GitHub Pages must be configured to use GitHub Actions. No custom domain or DNS change is included.

The site uses relative paths and a project-base helper, so the same files support both an origin root and a GitHub project path. No backend or package installation is required. Hosted browser verification is still required after any deployment.

For an intended update, edit the extracted source, regenerate the runtime archive and release manifest, and update the pinned manifest/archive hashes in the build script; changing it does not constitute clinical, listening or publication-rights approval. No licence grant covering third-party material is included. Public references and adaptation limits remain within the resources.
