# Idle Math and Big Numbers

Read when implementing a number type for values past 9e15 or 1.8e308, formatting large values for display, doing cost math in log-space, or tuning the prestige/reset loop.

## 1. Choosing a representation

| Representation | Range | Precision | Cost | Use when |
| --- | --- | --- | --- | --- |
| int64 | ±9.22e18 | exact | cheapest | Hard currency, counts, ticks; never for exponential soft currency |
| double | 1.797e308 | 15-17 digits; exact integers only to 2^53 ≈ 9.007e15 | cheap | Content plan stays below ~1e300 with margin |
| Mantissa (double) + exponent (int64) | 10^(9.2e18) | 15-17 digits | ~3-10× double | Default for incremental games that pass 1e300 |
| Log-space (store log10 x as double) | 10^(1.8e308) | relative precision ~1e-16 of the exponent, so absolute precision degrades as values grow | cheap mul/div, costlier add | Only multiply/compare, rarely add (prestige values, multipliers) |
| Layered ("tetration") types | beyond 10^(9e15) | coarse | expensive | Only when the design deliberately goes hyper-exponential |

Libraries in the break_infinity / break_eternity family use the mantissa-exponent and layered layouts respectively; verify the current version and license before adopting, and wrap them behind your own type so the representation can change.

**Precision consequence.** With ~16 significant digits, adding 1 to 1e20 does nothing. Late-game faucets must be proportional (percent of current rate, multipliers) rather than flat, or they silently stop working.

## 2. Mantissa-exponent struct (C#, non-negative values)

```csharp
public readonly struct BigNum : IComparable<BigNum>
{
    public readonly double M;   // 0, or 1 <= M < 10
    public readonly long E;     // base-10 exponent

    public static readonly BigNum Zero = new BigNum(0, 0);

    public BigNum(double m, long e)
    {
        if (m <= 0 || double.IsNaN(m)) { M = 0; E = 0; return; }
        int shift = (int)Math.Floor(Math.Log10(m));
        double nm = m / Math.Pow(10, shift);
        long ne = e + shift;
        if (nm >= 10) { nm /= 10; ne++; }          // floating-point edge after division
        else if (nm < 1) { nm *= 10; ne--; }
        M = nm; E = ne;
    }

    public static BigNum FromDouble(double x) => new BigNum(x, 0);

    public static BigNum operator *(BigNum a, BigNum b) => new BigNum(a.M * b.M, a.E + b.E);
    public static BigNum operator /(BigNum a, BigNum b) => new BigNum(a.M / b.M, a.E - b.E);

    public static BigNum operator +(BigNum a, BigNum b)
    {
        if (a.M == 0) return b;
        if (b.M == 0) return a;
        if (a.E < b.E) (a, b) = (b, a);
        long d = a.E - b.E;
        if (d > 17) return a;                      // b is below a's precision
        return new BigNum(a.M + b.M / Math.Pow(10, d), a.E);
    }

    // Caller guarantees a >= b; returns Zero instead of a negative value.
    public static BigNum operator -(BigNum a, BigNum b)
    {
        if (b.M == 0) return a;
        if (a.CompareTo(b) <= 0) return Zero;
        long d = a.E - b.E;
        if (d > 17) return a;
        return new BigNum(a.M - b.M / Math.Pow(10, d), a.E);
    }

    public double Log10() => M == 0 ? double.NegativeInfinity : Math.Log10(M) + E;

    public static BigNum Pow10(double log10)
    {
        double fl = Math.Floor(log10);
        return new BigNum(Math.Pow(10, log10 - fl), (long)fl);
    }

    public int CompareTo(BigNum o)
    {
        if (M == 0 || o.M == 0) return M.CompareTo(o.M);
        return E != o.E ? E.CompareTo(o.E) : M.CompareTo(o.M);
    }
}
```

Serialize as two fields (`m`, `e`) or a string `"1.2345e1234"`. Never as a JSON number: a JSON parser that reads doubles turns 1e400 into Infinity or an error. Send `Log10()` to analytics; percentile math on log values is meaningful, on raw values it is not.

## 3. Log-space formulas

Let `la = log10(a)`, `lb = log10(b)`, `la ≥ lb`.

```
log10(a·b)   = la + lb
log10(a/b)   = la − lb
log10(a^k)   = k·la
log10(a + b) = la + log10(1 + 10^(lb − la))      (skip b if la − lb > 17)
log10(a − b) = la + log10(1 − 10^(lb − la))      (requires la > lb)
```

**Cost of the k-th unit:** `log10 c(k) = log10 b + k·log10 r`. At r = 1.15 and k = 5,000 this is 1 + 5,000 × 0.0607 = 304.5, i.e. 3.2e304 — one level below double overflow. A game with 6,000 buyable levels at r = 1.15 cannot use doubles.

**Bulk cost in log-space:**

```
log10 C(k, n) = log10 b + k·log10 r + log10(r^n − 1) − log10(r − 1)
log10(r^n − 1) ≈ n·log10 r            when n·log10 r > 17
```

**Max affordable in log-space** (D = log10 M − log10 c(k)):

```
if D < 0                    → 0
if D < 300                  → n = floor( log_r( 10^D·(r − 1) + 1 ) )        (ordinary double math)
else                        → n = floor( (D + log10(r − 1)) / log10 r )
then decrement once if C(k, n) > M
```

## 4. Notation

| Exponent | Short scale | Letters (after T) | Scientific | Engineering |
| --- | --- | --- | --- | --- |
| 3 | K | K | 1.00e3 | 1.00e3 |
| 6 | M | M | 1.00e6 | 1.00e6 |
| 9 | B | B | 1.00e9 | 1.00e9 |
| 12 | T | T | 1.00e12 | 1.00e12 |
| 15 | Qa | aa | 1.00e15 | 1.00e15 |
| 18 | Qi | ab | 1.00e18 | 1.00e18 |
| 21 | Sx | ac | 1.00e21 | 1.00e21 |
| 90 | — | az | 1.00e90 | 1.00e90 |
| 93 | — | ba | 1.00e93 | 1.00e93 |
| 2,040 | — | zz | 1.00e2040 | 1.00e2040 |

Rules (heuristics drawn from common genre practice):
- Always show 3 significant digits: `1.23aa`, `12.3aa`, `123aa`. Width stays constant, which matters more than the suffix scheme.
- Letters after T are learnable (aa, ab, ... az, ba, ...) and cover 676 groups up to 1e2040; named short-scale words (Quadrillion, Quintillion, ...) stop being readable after about Dc (1e33).
- Offer a scientific/engineering toggle; long-tenure players switch to it.
- Comparisons in UI ("need 4.2ab, have 980aa") must use the same scheme on both sides.

```ts
const SHORT = ["", "K", "M", "B", "T"];

export function formatBig(m: number, e: number): string {   // m in [1,10), e integer
  if (m === 0) return "0";
  let group = Math.floor(e / 3);
  let lead = m * Math.pow(10, e - group * 3);                // in [1, 1000)
  const digits = lead < 10 ? 2 : lead < 100 ? 1 : 0;
  if (Number(lead.toFixed(digits)) >= 1000) { lead /= 1000; group++; }
  const d = lead < 10 ? 2 : lead < 100 ? 1 : 0;
  if (group < SHORT.length) return lead.toFixed(d) + SHORT[group];
  const idx = group - SHORT.length;                          // 0 => "aa" at 1e15
  if (idx >= 26 * 26) return `${m.toFixed(2)}e${e}`;         // past "zz": scientific
  const a = String.fromCharCode(97 + Math.floor(idx / 26));
  const b = String.fromCharCode(97 + (idx % 26));
  return lead.toFixed(d) + a + b;
}
```

Display values under 1,000 as integers when the currency is integral; never show "1.00K" for 1,000 coins in the first session.

## 5. Prestige loop math

**Gain families** (L = lifetime earnings this run, L₀ = threshold):

| Family | Formula | To double gain you need | Feel |
| --- | --- | --- | --- |
| Square root | `P = k·sqrt(L/L₀)` | 4× L | Generous; fast early resets |
| Cube root | `P = k·(L/L₀)^(1/3)` | 8× L | Standard mid-pace |
| Logarithmic | `P = k·log10(L/L₀)` | L squared | Very slow; resets become rare events |
| Layered | prestige-of-prestige currencies | — | Only for long-tenure designs |

**Effect of prestige** is usually linear in points: `mult = 1 + β·P` (β = 1-10% per point, heuristic). Combined with a square-root gain, total multiplier grows as about `sqrt(L)`, so each run reaches a higher L faster — that compounding is the meta loop.

**When to reset (player-optimal).** Run gain rate is `P(t)/t` including the time to climb back. It peaks where the marginal rate equals the average rate: `dP/dt = P(t)/t`. Show a "prestige now gives ×X" readout; players use it instead of the formula. Design targets (heuristic):
- First reset available at 1-3 h of play and worth ≥ 2× production.
- Run length roughly flat or shrinking across resets; if each run takes longer than the last, the multiplier family is too steep.
- New mechanics unlock at reset milestones so the reset is a content event, not only a number.

**Milestone multipliers** (heuristic): ×2 to a building's output at owned counts 25, 50, 100, 200, 300, 400... These create visible goals between purchases and convert a smooth exponential cost into a stepped feel without changing r.

## 6. Pacing check in log-time

Plot `log10(currency)` and `log10(next goal cost)` against real hours from the harness. Healthy idle pacing (heuristic): the gap between them stays roughly constant within a run, then collapses after each reset. A widening gap is a wall; a shrinking one means the run should already have ended.
