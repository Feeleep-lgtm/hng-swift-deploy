# SwiftDeploy - Declarative Deployment Tool

A clean, production-ready declarative deployment CLI that treats `manifest.yaml` as the **single source of truth**.

Built for HNG DevOps Stage (SwiftDeploy Task).

---

## Features

- **Single Source of Truth**: Everything is driven from `manifest.yaml`
- **Stable & Canary Deployments** with one-command promotion
- **Automatic Configuration Generation** using Jinja2 templates
- **Secure by Default**: Non-root containers + dropped capabilities
- **Nginx Reverse Proxy** with proper headers and logging
- **Full CLI**: `init`, `validate`, `deploy`, `promote`, `teardown`

---

## Quick Start

```bash
# 1. Clone and enter project
git clone <your-repo-url>
cd swiftdeploy

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize project
python swiftdeploy.py init

# 4. Validate
python swiftdeploy.py validate

# 5. Deploy
python swiftdeploy.py deploy

# 6. Switch modes
python swiftdeploy.py promote canary
python swiftdeploy.py promote stable