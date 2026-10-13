# Apple Health mobility parser

Extracts daily iPhone mobility measures from an Apple Health export (`export.xml`).

## Usage

```
python parse_apple_health.py export.xml output.csv
```

Requires Python 3. No other packages are needed.

## Output

One row per calendar day:

| Column | Value |
|---|---|
| date | YYYY-MM-DD |
| walking_speed | daily mean, m/s |
| step_length | daily mean, cm |
| asymmetry | daily mean, % |
| double_support | daily mean, % |
| step_count | daily sum |

Only records whose device metadata identifies an iPhone are included. Values are otherwise used as provided by Apple. A blank cell means there was no record of that measure on that day.
