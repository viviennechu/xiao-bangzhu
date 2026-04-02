## ADDED Requirements

### Requirement: SEO blog post generation

The system SHALL generate a blog post of 1,500–2,500 Chinese characters with an SEO-optimized H1 title containing the primary keyword, at least 3 H2 sections, and a meta description of 120–160 characters.

#### Scenario: Full blog post generated

- **WHEN** product highlights, style examples, and market analysis are available
- **THEN** the output SHALL contain: one H1 title, ≥ 3 H2 sections, body text ≥ 1,500 characters, and a meta_description field

#### Scenario: Blog post respects keyword placement

- **WHEN** the primary keyword is provided
- **THEN** the primary keyword SHALL appear in the H1 title and at least once in the first paragraph

---

### Requirement: Blog post structure

The blog post SHALL follow the structure: personal anecdote opening → product introduction → highlight breakdown (one H2 per major highlight) → 「大V老實說」pros/cons section → conclusion with hashtags.

#### Scenario: 大V老實說 section present

- **WHEN** any blog post is generated
- **THEN** the output SHALL contain a section with the heading 「大V老實說」listing at least one pro and one con

#### Scenario: Hashtags at end

- **WHEN** any blog post is generated
- **THEN** the output SHALL end with 4–6 hashtags in the format `#keyword`

---

### Requirement: AMI knowledge integration in blog

The system SHALL inject AMI knowledge snippets into the blog when product category is educational or books.

#### Scenario: AMI theory cited in blog

- **WHEN** ami_snippet is not null AND product category is "educational"
- **THEN** the blog SHALL reference the AMI concept with a citation attribution to 蒙特梭利理論

---

### Requirement: Blog generation via SSE stream

The system SHALL stream blog generation progress to the frontend via a dedicated SSE endpoint, emitting progress events during generation and a done event with the final text.

#### Scenario: SSE stream completes

- **WHEN** the blog generation API endpoint is called
- **THEN** the system SHALL emit at least one progress event followed by a done event containing the full blog text
