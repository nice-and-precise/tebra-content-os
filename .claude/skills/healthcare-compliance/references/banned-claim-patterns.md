# Banned Claim Patterns

These patterns trigger the PreToolUse compliance hook (`scripts/compliance_check.py`). Avoid generating content matching these patterns unless you have a registered source citation.

## Mortality and Morbidity Claims

```
reduces? (mortality|death|deaths|morbidity)
(lower|fewer|reduced?) (deaths|fatalities|mortality rate)
(improves?|extends?) (survival|life expectancy|prognosis)
prevents? (complications|adverse events|readmissions?)
```

## Percentage + Clinical Metric

```
\d+\.?\d*\s*%\s*(reduction|decrease|improvement|increase)\s+in\s+(a1c|hemoglobin|readmission|mortality|complication|infection)
reduces? (a1c|hba1c|blood pressure|readmission rate|complication rate) by \d+
```

## Diagnostic Accuracy Claims

```
detects? \d+\.?\d*\s*% of (cases|diagnoses|conditions)
(misses?|catches?) fewer (diagnoses|cases|errors?)
(more|less) accurate (than|compared to)
diagnostic accuracy of \d+
```

## Regulatory Endorsement Claims

```
(fda[-\s]?approved|fda[-\s]?cleared|fda[-\s]?certified)
(cms[-\s]?certified|cms[-\s]?approved|cms[-\s]?endorsed)
(hipaa[-\s]?certified|hipaa[-\s]?guaranteed|fully hipaa)
(ama[-\s]?approved|ama[-\s]?recommended|ama[-\s]?endorsed)
```

Note: "HIPAA-compliant" is not banned if sourced to an official BAA or audit report. "HIPAA-certified" is always banned — HIPAA has no certification program.

## Bare Mortality Keyword (without context)

The compliance hook also flags bare occurrences of:

```
mortality
morbidity
```

in any sentence that also contains a percentage or a comparative claim (e.g., "reduces," "lower," "fewer").

## Safe Alternatives

| Banned pattern | Safe reframe |
|---------------|-------------|
| "Reduces claim denials by 59%" | Requires a Tier 2 source; use exact source data |
| "Prevents readmissions" | "Supports readmission reduction programs" (cite the program, not the outcome) |
| "FDA-approved" | "Cleared by FDA for [specific indication]" (cite the 510(k) or clearance letter) |
| "Reduces A1C" | Remove, or cite a peer-reviewed study that Tebra's workflow is tied to |
| "HIPAA-certified" | "HIPAA-compliant under [specific safeguard]" (cite the BAA or policy) |
