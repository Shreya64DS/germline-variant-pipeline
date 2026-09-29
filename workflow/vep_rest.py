#!/usr/bin/env python3
"""Annotate a VCF using the Ensembl VEP REST API (no local cache needed)."""
import gzip, json, sys, time, urllib.request

IN_VCF  = "results/calls/HG001.pass.vcf.gz"
OUT_TSV = "results/annotation/HG001.annotated.tsv"
SERVER  = "https://rest.ensembl.org"
OPTS    = ("?canonical=1&mane=1&symbol=1&numbers=1&sift=b&polyphen=b"
           "&af=1&af_gnomade=1&af_gnomadg=1&check_existing=1&hgvs=1")
BATCH   = 200

IMPACT = {"HIGH": 3, "MODERATE": 2, "LOW": 1, "MODIFIER": 0}

def read_vcf(path):
    rows = []
    with gzip.open(path, "rt") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            f = line.rstrip("\n").split("\t")
            chrom, pos, _, ref, alt = f[0], f[1], f[2], f[3], f[4]
            fmt, smp = f[8].split(":"), f[9].split(":")
            d = dict(zip(fmt, smp))
            key = f"{chrom.replace('chr','')} {pos} . {ref} {alt} . . ."
            rows.append({"key": key, "chrom": chrom, "pos": pos, "ref": ref,
                         "alt": alt, "gt": d.get("GT", ""), "dp": d.get("DP", ""),
                         "gq": d.get("GQ", "")})
    return rows

def post(variants, attempt=1):
    req = urllib.request.Request(
        SERVER + "/vep/homo_sapiens/region" + OPTS,
        data=json.dumps({"variants": variants}).encode(),
        headers={"Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except Exception as e:
        if attempt > 5:
            raise
        wait = 5 * attempt
        print(f"  retry {attempt} after {wait}s ({e})", file=sys.stderr)
        time.sleep(wait)
        return post(variants, attempt + 1)

def pick(consequences):
    if not consequences:
        return {}
    return max(consequences, key=lambda c: (
        bool(c.get("mane_select")),
        c.get("canonical") == 1,
        IMPACT.get(c.get("impact", ""), -1)))

def freqs(item):
    best, ids, clin = "", [], []
    for cv in item.get("colocated_variants", []):
        if cv.get("id"):
            ids.append(cv["id"])
        clin += cv.get("clin_sig", []) or []
        for allele, fr in (cv.get("frequencies") or {}).items():
            vals = [v for k, v in fr.items()
                    if k in ("gnomade", "gnomadg", "af") and isinstance(v, (int, float))]
            if vals:
                m = max(vals)
                if best == "" or m > best:
                    best = m
    return best, ";".join(sorted(set(ids))), ";".join(sorted(set(clin)))

rows = read_vcf(IN_VCF)
print(f"{len(rows)} variants to annotate", file=sys.stderr)
ann = {}
for i in range(0, len(rows), BATCH):
    chunk = rows[i:i + BATCH]
    for item in post([r["key"] for r in chunk]):
        ann[item.get("input", "")] = item
    print(f"  {min(i+BATCH, len(rows))}/{len(rows)}", file=sys.stderr)
    time.sleep(0.5)

cols = ["chrom", "pos", "ref", "alt", "gt", "dp", "gq", "symbol", "gene",
        "transcript", "mane", "consequence", "impact", "sift", "polyphen",
        "max_pop_af", "existing", "clin_sig", "hgvsc", "hgvsp"]
with open(OUT_TSV, "w") as out:
    out.write("\t".join(cols) + "\n")
    for r in rows:
        it = ann.get(r["key"], {})
        tc = pick(it.get("transcript_consequences", []))
        af, ids, clin = freqs(it)
        out.write("\t".join(str(x) for x in [
            r["chrom"], r["pos"], r["ref"], r["alt"], r["gt"], r["dp"], r["gq"],
            tc.get("gene_symbol", ""), tc.get("gene_id", ""),
            tc.get("transcript_id", ""), tc.get("mane_select", ""),
            ",".join(tc.get("consequence_terms", []) or
                     [it.get("most_severe_consequence", "")]),
            tc.get("impact", ""), tc.get("sift_prediction", ""),
            tc.get("polyphen_prediction", ""), af, ids, clin,
            tc.get("hgvsc", ""), tc.get("hgvsp", "")]) + "\n")
print(f"wrote {OUT_TSV}", file=sys.stderr)
