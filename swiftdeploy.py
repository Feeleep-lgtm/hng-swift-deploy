#!/usr/bin/env python3
import sys
import yaml
import subprocess
import time
import requests
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
OPA_URL = "http://localhost:8181"

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def load_manifest():
    with open(BASE_DIR / "manifest.yaml") as f:
        return yaml.safe_load(f)

def query_opa(policy_path, input_data):
    try:
        resp = requests.post(
            f"{OPA_URL}/v1/data/{policy_path}",
            json={"input": input_data},
            timeout=5
        )
        if resp.status_code == 200:
            result = resp.json()
            return result.get("result", {})
        return {"allow": False, "reason": f"OPA error: {resp.status_code}"}
    except:
        return {"allow": False, "reason": "OPA unreachable"}

def cmd_init():
    manifest = load_manifest()
    with open("docker-compose.yml", "w") as f:
        f.write(env.get_template("docker-compose.yml.j2").render(manifest=manifest))
    with open("nginx.conf", "w") as f:
        f.write(env.get_template("nginx.conf.j2").render(manifest=manifest))
    print("✅ Generated configs from manifest")

def cmd_deploy():
    print("🔍 Pre-deploy OPA check...")
    # TODO: Get host stats and query OPA
    cmd_init()
    subprocess.run(["docker", "compose", "up", "-d", "--build"])

def main():
    if len(sys.argv) < 2:
        print("Usage: python swiftdeploy.py <init|validate|deploy|promote|status>")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "init":
        cmd_init()
    elif cmd == "deploy":
        cmd_deploy()
    else:
        print(f"Command '{cmd}' coming soon...")

if __name__ == "__main__":
    main()
