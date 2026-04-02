## ADDED Requirements

### Requirement: Keyword-scored article selection

The system SHALL load `posts.json` and score each article by counting keyword matches between the topic query and the article's `title + excerpt + tags` fields, then return the top N highest-scoring articles as style examples.

#### Scenario: Relevant articles found

- **WHEN** at least 3 articles have a keyword overlap score > 0
- **THEN** the system SHALL return the top 3 articles by score, each truncated to 800 characters of plain text (HTML stripped)

#### Scenario: Fewer than 3 relevant articles

- **WHEN** fewer than 3 articles have a score > 0
- **THEN** the system SHALL fill remaining slots from the 5 most recent articles in posts.json (by date descending)

#### Scenario: No relevant articles at all

- **WHEN** no article has any keyword overlap with the query
- **THEN** the system SHALL return 3 articles selected from the 5 most recent articles

---

### Requirement: HTML stripping before style example output

The system SHALL strip all HTML tags from article `content` before returning style examples for use in prompts.

#### Scenario: HTML content stripped

- **WHEN** an article's content field contains HTML markup
- **THEN** the returned text SHALL contain no HTML tags and SHALL preserve paragraph breaks as newlines

---

### Requirement: Style category filtering

The system SHALL support an optional `category_filter` parameter. When provided, the system SHALL restrict scoring to articles that have at least one matching category or tag before applying keyword scoring.

#### Scenario: Montessori category filter applied

- **WHEN** category_filter = "montessori" is specified
- **THEN** the system SHALL only score articles whose tags or categories contain "蒙特梭利" or "AMI"

#### Scenario: No articles match category filter

- **WHEN** category_filter is specified but no articles match the category
- **THEN** the system SHALL ignore the filter and fall back to scoring all articles
