## ADDED Requirements

### Requirement: AMI document indexing at startup

The system SHALL read all `.docx` files under the AMI knowledge directory (`/Users/a_bab/Desktop/all_claude/ami蒙特梭利/ami/`) at application startup, extract plain text using python-docx, and store the result as an in-memory dict keyed by filename.

#### Scenario: Successful index load

- **WHEN** the application starts and the AMI directory exists with at least one `.docx` file
- **THEN** the in-memory index SHALL contain at least one entry and the system SHALL log the count of loaded documents

#### Scenario: AMI directory missing

- **WHEN** the AMI directory does not exist at startup
- **THEN** the system SHALL log a warning and continue with an empty index; content generation SHALL still function without AMI injection

#### Scenario: Corrupt or unreadable docx

- **WHEN** a `.docx` file raises an exception during parsing
- **THEN** the system SHALL skip that file, log the filename and error, and continue loading remaining files

---

### Requirement: Relevant AMI content retrieval

The system SHALL retrieve the most relevant AMI text snippet for a given topic query by computing keyword overlap scores across all indexed documents, returning the top-scoring document's content truncated to 600 characters.

#### Scenario: Matching AMI content found

- **WHEN** the topic query contains keywords present in at least one indexed AMI document
- **THEN** the system SHALL return the highest-scoring document's text snippet (≤ 600 chars)

#### Scenario: No matching AMI content

- **WHEN** no indexed document has any keyword overlap with the query
- **THEN** the system SHALL return null and the caller SHALL omit AMI injection from the prompt

---

### Requirement: AMI content injection into prompts

The system SHALL inject retrieved AMI text into the AI generation system prompt for blog and reels outputs when the product is categorized as educational, early childhood, or books.

#### Scenario: AMI snippet injected for educational product

- **WHEN** the product category is "educational" or "books" AND ami_snippet is not null
- **THEN** the system prompt SHALL include the AMI snippet under a labeled section "蒙特梭利理論依據"

#### Scenario: AMI injection skipped for non-educational product

- **WHEN** the product category is "general" (e.g., household goods, food)
- **THEN** the system SHALL NOT inject AMI content into the prompt
