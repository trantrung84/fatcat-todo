"""App Store Connect API helper (runs in GitHub Actions with the ASC_* secrets).

  python tools/asc_meta.py meta   VERSION   -> push store/aso/asc.json (all locales) to the version + app info
  python tools/asc_meta.py submit VERSION   -> attach the newest VALID build of VERSION and submit for review
  python tools/asc_meta.py status VERSION   -> print what is set
"""
import json, os, sys, time, pathlib
import jwt, requests

APP_ID = "6838151094"
API = "https://api.appstoreconnect.apple.com"
ROOT = pathlib.Path(__file__).resolve().parent.parent


def token():
    key = os.environ["ASC_KEY_P8"]
    if "BEGIN PRIVATE KEY" not in key:
        import base64
        key = base64.b64decode(key).decode()
    now = int(time.time())
    return jwt.encode({"iss": os.environ["ASC_ISSUER_ID"], "iat": now, "exp": now + 1100, "aud": "appstoreconnect-v1"},
                      key, algorithm="ES256", headers={"kid": os.environ["ASC_KEY_ID"], "typ": "JWT"})


S = requests.Session()
S.headers["Authorization"] = "Bearer " + token()


def call(method, path, body=None, ok=(200, 201, 204)):
    r = S.request(method, API + path, json=body)
    if r.status_code not in ok:
        print("ERROR", method, path, r.status_code, r.text[:1500])
        r.raise_for_status()
    return r.json() if r.text else {}


def version(vs):
    d = call("GET", f"/v1/apps/{APP_ID}/appStoreVersions?filter[versionString]={vs}&filter[platform]=IOS")["data"]
    if not d:
        sys.exit(f"version {vs} not found")
    return d[0]


def editable_appinfo():
    infos = call("GET", f"/v1/apps/{APP_ID}/appInfos")["data"]
    for i in infos:
        if i["attributes"].get("appStoreState") in ("PREPARE_FOR_SUBMISSION", "DEVELOPER_REJECTED", "REJECTED",
                                                     "METADATA_REJECTED", "WAITING_FOR_REVIEW") or \
           i["attributes"].get("state") in ("PREPARE_FOR_SUBMISSION", "REJECTED", "WAITING_FOR_REVIEW"):
            return i
    print("appInfos:", [(i["id"], i["attributes"].get("appStoreState"), i["attributes"].get("state")) for i in infos])
    return infos[0]


def meta(vs):
    data = json.load(open(ROOT / "store/aso/asc.json"))
    v = version(vs)
    have = {l["attributes"]["locale"]: l for l in
            call("GET", f"/v1/appStoreVersions/{v['id']}/appStoreVersionLocalizations?limit=50")["data"]}
    for loc, m in data.items():
        attrs = {"description": m["description"], "keywords": m["keywords"], "whatsNew": m["whatsnew"],
                 "promotionalText": m["promo"], "supportUrl": "https://toonred.com", "marketingUrl": "https://toonred.com"}
        if loc in have:
            call("PATCH", f"/v1/appStoreVersionLocalizations/{have[loc]['id']}",
                 {"data": {"type": "appStoreVersionLocalizations", "id": have[loc]["id"], "attributes": attrs}})
            print("version loc updated", loc)
        else:
            attrs["locale"] = loc
            call("POST", "/v1/appStoreVersionLocalizations",
                 {"data": {"type": "appStoreVersionLocalizations", "attributes": attrs,
                           "relationships": {"appStoreVersion": {"data": {"type": "appStoreVersions", "id": v["id"]}}}}})
            print("version loc created", loc)
    info = editable_appinfo()
    have = {l["attributes"]["locale"]: l for l in
            call("GET", f"/v1/appInfos/{info['id']}/appInfoLocalizations?limit=50")["data"]}
    for loc, m in data.items():
        attrs = {"name": m["name"], "subtitle": m["subtitle"],
                 "privacyPolicyUrl": "https://toonred.com/fatcat-todo/privacy"}
        if loc in have:
            call("PATCH", f"/v1/appInfoLocalizations/{have[loc]['id']}",
                 {"data": {"type": "appInfoLocalizations", "id": have[loc]["id"], "attributes": attrs}})
            print("app info loc updated", loc)
        else:
            attrs["locale"] = loc
            call("POST", "/v1/appInfoLocalizations",
                 {"data": {"type": "appInfoLocalizations", "attributes": attrs,
                           "relationships": {"appInfo": {"data": {"type": "appInfos", "id": info["id"]}}}}})
            print("app info loc created", loc)


def submit(vs):
    v = version(vs)
    builds = []
    for _ in range(40):  # wait up to ~40 min for processing
        builds = call("GET", f"/v1/builds?filter[app]={APP_ID}&filter[preReleaseVersion.version]={vs}"
                             f"&filter[processingState]=VALID&sort=-uploadedDate&limit=1")["data"]
        if builds:
            break
        print("waiting for a processed build of", vs)
        time.sleep(60)
    if not builds:
        sys.exit("no processed build")
    b = builds[0]
    print("build", b["attributes"]["version"])
    if b["attributes"].get("usesNonExemptEncryption") is None:
        call("PATCH", f"/v1/builds/{b['id']}",
             {"data": {"type": "builds", "id": b["id"], "attributes": {"usesNonExemptEncryption": False}}})
    call("PATCH", f"/v1/appStoreVersions/{v['id']}/relationships/build", {"data": {"type": "builds", "id": b["id"]}})
    sub = call("POST", "/v1/reviewSubmissions",
               {"data": {"type": "reviewSubmissions", "attributes": {"platform": "IOS"},
                         "relationships": {"app": {"data": {"type": "apps", "id": APP_ID}}}}})["data"]
    call("POST", "/v1/reviewSubmissionItems",
         {"data": {"type": "reviewSubmissionItems",
                   "relationships": {"reviewSubmission": {"data": {"type": "reviewSubmissions", "id": sub["id"]}},
                                     "appStoreVersion": {"data": {"type": "appStoreVersions", "id": v["id"]}}}}})
    call("PATCH", f"/v1/reviewSubmissions/{sub['id']}",
         {"data": {"type": "reviewSubmissions", "id": sub["id"], "attributes": {"submitted": True}}})
    print("SUBMITTED for review:", vs, "build", b["attributes"]["version"])


def certs(_):
    for c in call("GET", "/v1/certificates?limit=200")["data"]:
        a = c["attributes"]
        print(c["id"], "|", a.get("certificateType"), "|", a.get("name"), "|", a.get("displayName"), "|", a.get("expirationDate"))


def revoke_ci_dev_certs(_):
    """Revoke Apple Development certs that CI runners created (keeps distribution certs and certs from real Macs)."""
    for c in call("GET", "/v1/certificates?limit=200")["data"]:
        a = c["attributes"]
        if a.get("certificateType") in ("DEVELOPMENT", "IOS_DEVELOPMENT") and "Created via API" in (a.get("displayName") or a.get("name") or ""):
            call("DELETE", f"/v1/certificates/{c['id']}")
            print("revoked", c["id"], a.get("displayName"))


def status(vs):
    v = version(vs)
    print("version", vs, v["attributes"].get("appStoreState"))
    for l in call("GET", f"/v1/appStoreVersions/{v['id']}/appStoreVersionLocalizations?limit=50")["data"]:
        a = l["attributes"]
        print(" ", a["locale"], "| kw", len(a.get("keywords") or ""), "| desc", len(a.get("description") or ""),
              "| new", len(a.get("whatsNew") or ""))
    info = editable_appinfo()
    for l in call("GET", f"/v1/appInfos/{info['id']}/appInfoLocalizations?limit=50")["data"]:
        a = l["attributes"]
        print(" ", a["locale"], "|", a.get("name"), "|", a.get("subtitle"))


if __name__ == "__main__":
    {"meta": meta, "submit": submit, "status": status, "certs": certs, "revoke": revoke_ci_dev_certs}[sys.argv[1]](sys.argv[2])
    if sys.argv[1] == "meta":
        status(sys.argv[2])
