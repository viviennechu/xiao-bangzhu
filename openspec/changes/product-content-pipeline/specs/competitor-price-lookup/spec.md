## ADDED Requirements

### Requirement: Google search for competitor group buy price

The system SHALL search Google for `{product_keyword} site:facebook.com/chienchien99`, retrieve the top 5 result snippets, apply regex to extract price amounts (NTD), and return the lowest found price as competitor_price.

#### Scenario: Competitor price found

- **WHEN** at least one Google result snippet contains a numeric price pattern (e.g.,「$XXX」or「XXX元」or「NT$XXX」)
- **THEN** competitor_price SHALL be set to the lowest extracted numeric value as an integer

#### Scenario: No price found in snippets

- **WHEN** no snippet contains a recognizable price pattern
- **THEN** competitor_price SHALL be null and the system SHALL return a message: "查無 chienchien99 歷史團購紀錄"

#### Scenario: Google search fails

- **WHEN** the Google search raises a network error or returns no results
- **THEN** competitor_price SHALL be null and the system SHALL NOT raise an exception to the caller

---

### Requirement: SQLite caching of competitor price results

The system SHALL persist each successful competitor price lookup result to a local SQLite database (`data/competitor_prices.db`) with columns: product_keyword, competitor_price, source_snippet, searched_at.

#### Scenario: Result cached after successful lookup

- **WHEN** a competitor price is found
- **THEN** the result SHALL be inserted into the SQLite database within the same request lifecycle

#### Scenario: Cache hit on repeated query

- **WHEN** the same product_keyword is queried within 7 days of a previous successful lookup
- **THEN** the system SHALL return the cached result without making a new Google search

#### Scenario: Cache miss triggers fresh search

- **WHEN** the product_keyword has no cache entry OR the cached entry is older than 7 days
- **THEN** the system SHALL perform a fresh Google search

---

### Requirement: Price comparison output

The system SHALL compare competitor_price against the user's group_buy_price and return a comparison result with fields: is_competitive (bool), difference_amount (int), recommendation (string).

#### Scenario: User price is lower

- **WHEN** user group_buy_price < competitor_price
- **THEN** is_competitive SHALL be true and recommendation SHALL be "可在文案中強調比市面團購更優惠"

#### Scenario: User price is higher

- **WHEN** user group_buy_price > competitor_price
- **THEN** is_competitive SHALL be false and recommendation SHALL be "建議向廠商爭取更低的團購價格"
