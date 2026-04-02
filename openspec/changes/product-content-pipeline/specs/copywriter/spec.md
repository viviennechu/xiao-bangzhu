## ADDED Requirements

### Requirement: Copywriter as three-format orchestration layer

The system SHALL act as an orchestration layer that invokes blog-writer, social-writer, and reels-scriptwriter in parallel using asyncio.gather, returning all three outputs in a single response object with fields: blog, social, reels.

#### Scenario: All three formats generated in parallel

- **WHEN** the copywriter is called with product data, highlights, price_result, market_analysis, ami_snippet, and style_examples
- **THEN** the system SHALL invoke all three writers concurrently and return a combined result containing blog (string), social (object with ig_post/fb_post/line_post), and reels (object with hook/segments/cta)

#### Scenario: One writer fails, others succeed

- **WHEN** one of the three parallel writers raises an exception
- **THEN** the system SHALL return partial results for the successful writers and set the failed writer's field to null with an error message; the overall request SHALL NOT fail

---

### Requirement: Context package assembly

Before invoking the three writers, the copywriter SHALL assemble a shared context package containing: product (dict), highlights (list), price_result (dict or null), market_analysis (dict or null), ami_snippet (string or null), style_examples (list of strings).

#### Scenario: Context package assembled with all fields

- **WHEN** all upstream data is available
- **THEN** the context package SHALL contain all six fields with non-null values

#### Scenario: Context package assembled with partial data

- **WHEN** market_analysis or ami_snippet is null due to upstream failure
- **THEN** the context package SHALL still be assembled with null values for missing fields; writers SHALL handle null fields gracefully
