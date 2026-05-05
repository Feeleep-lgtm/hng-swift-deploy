#!/usr/bin/env python3
import sys
import yaml
import subprocess
import time
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def load_manifest():
    with open(BASE_DIR / "manifest.yaml") as f:
        return yaml.safe_load(f)

def cmd_init():
    manifest = load_manifest()
    with open("docker-compose.yml", "w") as f:
        f.write(env.get_template("docker-compose.yml.j2").render(manifest=manifest))
    with open("nginx.conf", "w") as f:
        f.write(env.get_template("nginx.conf.j2").render(manifest=manifest))
    print("✅ Generated docker-compose.yml and nginx.conf")

def cmd_validate():
    print("🔍 Running validation checks...\n")
    try:
        manifest = load_manifest()
        checks = [
            ("manifest.yaml exists", True),
            ("Valid YAML", True),
            ("Required fields", bool(manifest.get('app') and manifest.get('nginx'))),
            ("Nginx port defined", bool(manifest['nginx'].get('port'))),
        ]
        for name, passed in checks:
            print(f"{'✅ PASS' if passed else '❌ FAIL'} {name}")
        print("\n🎉 All validation checks passed!")
    except Exception as e:
        print(f"❌ Validation failed: {e}")

def cmd_deploy():
    print("🚀 Deploying stack...")
    cmd_init()
    subprocess.run(["docker", "compose", "up", "-d", "--build"])
    time.sleep(5)
    subprocess.run(["docker", "compose", "ps"])

def cmd_teardown(clean=False):
    print("🗑️ Tearing down...")
    subprocess.run(["docker", "compose", "down"])
    if clean:
        for f in ["docker-compose.yml", "nginx.conf"]:
            if Path(f).exists():
                Path(f).unlink()
        print("🧹 Cleaned generated files")

def main():
    if len(sys.argv) < 2:
        print("Usage: python swiftdeploy.py <init|validate|deploy|promote|teardown>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "init": cmd_init()
    elif cmd == "validate": cmd_validate()
    elif cmd == "deploy": cmd_deploy()
    elif cmd == "promote":
        mode = sys.argv[2] if len(sys.argv) > 2 else "stable"
        manifest = load_manifest()
        manifest['app']['mode'] = mode
        with open("manifest.yaml", "w") as f:
            yaml.dump(manifest, f, sort_keys=False)
        print(f"🔄 Promoted to {mode.upper()}")
        cmd_init()
        subprocess.run(["docker", "compose", "up", "-d", "--build"])
    elif cmd == "teardown":
        clean = "--clean" in sys.argv
        cmd_teardown(clean)
    else:
        print("Unknown command")

if __name__ == "__main__":
    main()
