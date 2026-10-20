# code/ — the canonical grocery domain

The handbook's examples are written against one domain: a grocery-marketplace
order and inventory engine. Chapters show **excerpts** of it; this module is the
full, compiling model — 52 types in `com.handbook.grocery`.

| Path | Contents |
|---|---|
| `src/main/java` | The domain: `Money`, `Sku`, `Order`, `OrderLine`, `Cart`, `CartLine`, `InventoryItem`, `OrderStatus`, collaborators, exceptions |
| `examples/` | 80 runnable single-file programs used by the Examples pages, each with its captured `.out` |
| `src/test/java` | `SnippetContext` — the variables handbook snippets assume exist. Used only by the checker |

## Decisions this module fixes

- **`Money`** — `BigDecimal` at scale 2, so `equals` and `compareTo` agree (Ch 23). `rupees(long)` for whole rupees, `rupees(String)` for decimals. INR via `Currency.getInstance("INR")`.
- **`OrderStatus`** is the lifecycle **enum**. The sealed hierarchy carrying per-state data in Ch 12–13 is **`OrderState`**.
- **`Catalogue.priceFor`** returns `Optional<Money>` — a price may be absent (Ch 09). `PricingEngine.evaluate` returns `Money`.
- **`InventoryItem.reserve`** returns `ReservationResult`, not `boolean` (Ch 27, 41, 44).
- **`OrderId`** and **`DeliverySlot`** are `Comparable`, so they work as tie-breakers and sort keys (Ch 06, 23).

## Checking the handbook against it

```bash
python3 tools/check-code-blocks.py          # compile every ```java block with the local JDK
python3 tools/check-code-blocks.py --all    # on JDK 25+: include post-21 feature blocks

# Also type-check the testing chapters (41–44) against real JUnit, Mockito and AssertJ:
mvn -q -f code/pom.xml dependency:build-classpath -Dmdep.outputFile=/tmp/cp.txt
python3 tools/check-code-blocks.py --cp "$(cat /tmp/cp.txt)"
```

Reviewed exceptions — blocks that reference types from an adjacent block, or a
deliberately different variable type — are fingerprinted in
`tools/code-check-baseline.json`. Editing such a block changes its fingerprint,
so it is checked again rather than silently excused.
