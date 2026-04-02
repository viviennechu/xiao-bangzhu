## ADDED Requirements

### Requirement: Multi-platform social post generation

The system SHALL generate three distinct social posts in a single call: one for IG (≤ 300 characters + 5–8 hashtags), one for FB (≤ 300 characters, conversational tone), and one for LINE group (≤ 200 characters, direct CTA).

#### Scenario: All three platform posts returned

- **WHEN** social_writer is invoked with product data
- **THEN** the response SHALL contain three fields: ig_post, fb_post, line_post, each as a string

#### Scenario: IG post hashtag count

- **WHEN** the IG post is generated
- **THEN** the ig_post SHALL end with 5–8 hashtags in `#keyword` format

---

### Requirement: Casual conversational tone

Social posts SHALL use first-person narrative, conversational sentence endings (口語化), and SHALL NOT use formal sales language such as「精選」「嚴選」「頂級」「奢華」.

#### Scenario: Forbidden sales language absent

- **WHEN** any social post is generated
- **THEN** the text SHALL NOT contain any of: 精選, 嚴選, 頂級, 奢華, 限時搶購, 超殺價

---

### Requirement: Price value mention in social post

When competitor price data shows the user's price is lower, the social posts SHALL include a price comparison statement.

#### Scenario: Price advantage highlighted

- **WHEN** competitor_price is available AND user_price < competitor_price
- **THEN** at least one social post SHALL mention the price difference in plain language (e.g.,「比市面便宜 XX 元」)

---

### Requirement: Social post generation via SSE stream

The system SHALL stream social post generation via a dedicated SSE endpoint.

#### Scenario: SSE stream completes

- **WHEN** the social writer API endpoint is called
- **THEN** the system SHALL emit at least one progress event followed by a done event containing ig_post, fb_post, and line_post fields
