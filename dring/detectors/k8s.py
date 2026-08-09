"""Kubernetes pod name — splits deployment / pod-template-hash / pod suffix."""

import re

NAME = "k8s"
# k8s random suffixes use alphanumerics minus vowels and 0/1/o/i/l
_SUF = "[bcdfghjklmnpqrstvwxz2456789]"
_RE = re.compile(rf"^([a-z0-9][a-z0-9-]*?)-({_SUF}{{8,10}})-({_SUF}{{5}})$")


def detect(s):
    m = _RE.match(s.strip())
    if not m:
        return None
    name, tmpl_hash, suffix = m.groups()
    return {
        "type": NAME,
        "confidence": 0.75,
        "summary": f"Kubernetes pod: Deployment '{name}' -> ReplicaSet '{name}-{tmpl_hash}' -> pod '{suffix}'",
        "details": {
            "deployment": name,
            "pod_template_hash": tmpl_hash,
            "pod_suffix": suffix,
        },
    }
