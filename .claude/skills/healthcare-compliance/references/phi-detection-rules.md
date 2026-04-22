# PHI Detection Rules

HIPAA Safe Harbor requires removal of 18 identifiers. This file maps each to its detection pattern and the action to take in content drafts.

## The 18 Safe Harbor Identifiers

| # | Identifier | Detection pattern | Action |
|---|-----------|------------------|--------|
| 1 | Names | Full name, first + last in same sentence | Delete or replace with `[PATIENT]` |
| 2 | Geographic subdivision smaller than state | City, county, ZIP, street address | Generalize to state-level or region |
| 3 | Dates (except year) | MM/DD, month + day, "admitted on March 3" | Replace with year or timeframe ("Q1 2025") |
| 4 | Phone numbers | `\d{3}[-.\s]?\d{3}[-.\s]?\d{4}` | Delete |
| 5 | Fax numbers | Same pattern as phone | Delete |
| 6 | Email addresses | `[\w.+-]+@[\w-]+\.[a-z]{2,}` | Delete |
| 7 | Social Security numbers | `\d{3}-\d{2}-\d{4}` | Delete |
| 8 | Medical record numbers | Any numeric ID following "MRN", "record #", "encounter ID" | Delete |
| 9 | Health plan beneficiary numbers | Insurance ID, member ID patterns | Delete |
| 10 | Account numbers | Bank or billing account numbers | Delete |
| 11 | Certificate/license numbers | DEA number, medical license number | Delete |
| 12 | VIN and serial numbers | Vehicle or device serial numbers | Delete |
| 13 | Device identifiers | FDA UDI patterns | Delete |
| 14 | URLs that reveal patient identity | Any URL containing patient name or record ID | Delete |
| 15 | IP addresses | `\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}` (in patient context) | Delete |
| 16 | Biometric identifiers | Fingerprint, retina scan references | Delete |
| 17 | Full-face photographs | Any photo reference in a patient context | Remove reference |
| 18 | Any other unique identifier | Age > 89, rare condition + region combination | Generalize or delete |

## Age Threshold

Any patient described as older than 89 must have their age generalized to "90 or older" or "older adult patient." Specific age + condition + geographic detail is identifying even when all three are below the threshold individually.

## Aggregate vs. Individual Data

Practice-level aggregate statistics are not PHI:
- "This practice processed 2,400 claims in Q1 2025" ✓
- "Patient Jane Smith had 3 claims denied in Q1 2025" ✗

When in doubt: if the data could identify a specific individual, remove it.

## Synthetic Data for Case Studies

When a real customer interview cannot be attributed or their data is not available, synthetic data may be used if:

1. It is clearly labeled "representative example" or "illustrative scenario" in the draft
2. The synthetic data is based on real industry benchmarks (cite the source)
3. It is not presented as data from a specific named practice
