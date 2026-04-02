## ADDED Requirements

### Requirement: Trend analysis via Google Trends

The system SHALL fetch 12-month Google Trends data for a given product keyword using pytrends and compute a trend direction (rising, stable, declining) and a 3-month average interest score (0–100).

#### Scenario: Rising trend detected

- **WHEN** the 3-month average interest score is ≥ 50 AND the last 4-week average exceeds the 3-month average by ≥ 10 points
- **THEN** the system SHALL return trend_direction = "rising"

#### Scenario: Trends API unavailable

- **WHEN** pytrends raises a connection error or TooManyRequestsError
- **THEN** the system SHALL return trend_direction = null and SHALL NOT block content generation

---

### Requirement: Social signal measurement via IG hashtag count

The system SHALL retrieve the approximate post count for the primary product hashtag on Instagram by parsing the hashtag explore page.

#### Scenario: High competition hashtag

- **WHEN** the retrieved hashtag post count is ≥ 100,000
- **THEN** the system SHALL set social_competition = "high"

#### Scenario: Low competition hashtag

- **WHEN** the retrieved hashtag post count is < 10,000
- **THEN** the system SHALL set social_competition = "low"

#### Scenario: IG fetch fails

- **WHEN** the IG hashtag page is unreachable or returns no count
- **THEN** the system SHALL set social_competition = null and SHALL NOT block content generation

---

### Requirement: Marketing mode recommendation

The system SHALL produce a marketing_recommendation object containing: recommended_formats (list), primary_platform, and strategy_type, derived from trend and social signal data.

#### Scenario: SEO long-form recommended

- **WHEN** trend_direction = "rising" AND social_competition = "low"
- **THEN** recommended_formats SHALL include "blog" and primary_platform SHALL be "blog"

#### Scenario: Social short-form recommended

- **WHEN** trend_direction = "rising" AND social_competition = "high"
- **THEN** recommended_formats SHALL include "social" and strategy_type SHALL be "short-hit"

#### Scenario: All formats recommended

- **WHEN** trend_direction = "rising" AND social_competition = "low"
- **THEN** recommended_formats SHALL include all three: "blog", "social", "reels"

#### Scenario: Data unavailable fallback

- **WHEN** both trend_direction and social_competition are null
- **THEN** recommended_formats SHALL default to all three formats and strategy_type SHALL be "default"

---

### Requirement: Strategy type classification

The system SHALL classify the content strategy into one of three types: montessori-knowledge (educational product tied to AMI concepts), price-value (competitive pricing angle), lifestyle-experience (casual life sharing).

#### Scenario: Montessori strategy selected

- **WHEN** the product category matches early childhood education, toys, or books
- **THEN** strategy_type SHALL be "montessori-knowledge"

#### Scenario: Price-value strategy selected

- **WHEN** competitor price data is available AND the user's price is lower
- **THEN** strategy_type SHALL be "price-value"
