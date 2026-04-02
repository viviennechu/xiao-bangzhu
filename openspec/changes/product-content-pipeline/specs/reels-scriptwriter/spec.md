## ADDED Requirements

### Requirement: Three-section Reels script structure

The system SHALL generate a Reels script with exactly three sections: Hook (≤ 15 words, question or counter-intuitive statement), Content Segments (3–5 segments, each with voiceover text and a screen action hint), and CTA (≤ 10 words).

#### Scenario: Hook uses question or counter-intuitive opening

- **WHEN** a Reels script is generated
- **THEN** the Hook field SHALL be a question ending in「？」OR begin with a statement that contradicts common assumption

#### Scenario: Content segment count within range

- **WHEN** a Reels script is generated
- **THEN** the segments array SHALL contain between 3 and 5 items

#### Scenario: Each segment has voiceover and screen hint

- **WHEN** any content segment is generated
- **THEN** each segment SHALL have a voiceover field (spoken text) and a screen_hint field (what to show on camera)

---

### Requirement: Non-preachy casual tone for Reels

Reels scripts SHALL use casual, imperfect, relatable language. The script SHALL NOT use academic or lecture-style phrasing. The script SHALL include at least one personal imperfection acknowledgment (e.g., acknowledging that even the author doesn't follow the ideal 100% of the time).

#### Scenario: Imperfection acknowledgment present

- **WHEN** the product category is "educational" or "parenting"
- **THEN** the script SHALL contain at least one sentence acknowledging real-world imperfection in implementation

---

### Requirement: AMI knowledge in Reels script

For educational or book products, the system SHALL reference one AMI concept naturally within the Content Segments.

#### Scenario: AMI concept woven into segment

- **WHEN** ami_snippet is not null AND product category is "educational"
- **THEN** at least one segment voiceover SHALL reference an AMI concept in plain conversational language (no jargon without explanation)

---

### Requirement: Reels script generation via SSE stream

The system SHALL stream Reels script generation via a dedicated SSE endpoint.

#### Scenario: SSE stream completes

- **WHEN** the reels scriptwriter API endpoint is called
- **THEN** the system SHALL emit at least one progress event followed by a done event containing the structured script object
