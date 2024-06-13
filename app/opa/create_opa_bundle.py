import tarfile
from pathlib import Path


def create_opa_bundle():
    bundle_path = Path("app/opa/bundle.tar.gz")
    if bundle_path.is_file():
        bundle_path.unlink()

    rules_path = Path("app/opa/rules")
    with tarfile.open(bundle_path, 'w:gz') as tar:
        for f in rules_path.glob('*[!.gen].rego'):
            tar.add(name=f, arcname=f.relative_to(rules_path.parent))
