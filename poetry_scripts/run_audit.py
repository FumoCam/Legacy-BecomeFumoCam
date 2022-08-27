from typing import Dict

from ossaudit import audit, packages

# {"Vuln ID": "Reason"}
cve_ignores: Dict[str, str] = {
    "CVE-2022-33124": "aiohttp 3.8.1 IPV6 exception, not applicable",
    "sonatype-2022-0719": "dparse 0.5.2, non-threat, used only on dev",
}


def do_audit():
    with open("requirements-dev.txt") as dependencies:
        pkgs = packages.get_from_files([dependencies])

    audit_results = audit.components(pkgs)
    high_severity_found = False
    for vulnerability in audit_results:
        if vulnerability.id in cve_ignores:
            print(f"Skipping {vulnerability.id} ({cve_ignores[vulnerability.id]})")
            continue

        if vulnerability.cvss_score > 7.0 and not high_severity_found:
            high_severity_found = True

        for key, value in vulnerability._asdict().items():
            print(f"{key}: {value}")

        print("\n\n")

    if high_severity_found:
        exit(1)  # Failure

    exit(0)  # Success


if __name__ == "__main__":
    do_audit()
