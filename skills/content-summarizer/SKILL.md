---
name: content-summarizer
description: Summarize and interpret long-form content (podcasts, interviews, papers, blogs) using chunking-extraction-assembly methodology. Use this skill whenever the user wants to generate a structured summary of lengthy content, analyze interviews or articles, or extract key insights from documents with interpretation and context enrichment.
---

# Content Summarizer Skill

## Purpose

Transform long-form content (podcasts, interviews, academic papers, blog posts) into structured, MECE (Mutually Exclusive, Collectively Exhaustive) summaries with interpretation.

## Why This Approach

Direct LLM summarization of long content often results in:
- Missing important details
- Non-MECE coverage (some topics over-represented, others skipped)
- Surface-level analysis without depth

This skill uses a **three-phase pipeline** inspired by knowledge management systems:
1. **Chunking** - Split content into semantic units
2. **Extraction** - Pull key information from each chunk
3. **Assembly** - Combine into structured output with interpretation

## Workflow

### Phase 1: Chunking

**Goal**: Split input into manageable, semantically coherent segments.

**Methods** (choose based on content type):

**A. Header-Based Chunking** (for structured content)
- Split by markdown headers (H1, H2, H3)
- Keep hierarchical relationships intact

**B. Token-Based Chunking** (for unstructured content)
- Target: ~4,000-8,000 tokens per chunk
- Ensure chunks break at natural boundaries (paragraphs, topic shifts)
- Maintain ~200 token overlap between chunks for context continuity

**C. Semantic Chunking** (for conversational content like podcasts)
- Identify topic transitions
- Group by speaker turns or thematic segments
- Each chunk should cover ONE major theme or question-answer pair

### Phase 2: Extraction

**Goal**: Extract structured information from each chunk.

**Critical Extraction Categories** (based on common omissions):

#### A. Personal Journey & Background
- **Early life experiences** that shaped thinking (childhood, education, formative moments)
- **Key relationships**: mentors, collaborators, influences
- **Pivotal decisions** and their rationale
- **Personal anecdotes** that reveal character or philosophy

#### B. Intellectual Framework
- **Research methodology** (how they approach problems)
- **Core philosophical beliefs** (what they believe about the field)
- **Mental models** they use (books, thinkers, frameworks they reference)
- **Evolution of thinking** (how their views changed over time)

#### C. Specific Details (often overlooked)
- **Exact quotes** with speaker attribution
- **Specific stories** (rejections, failures, breakthroughs)
- **Concrete examples** (not just abstract concepts)
- **Vivid details** (what makes the story memorable)

#### D. Open Questions & Tensions
- **Unresolved problems** they acknowledge
- **Contradictions** or competing views they discuss
- **Future directions** they hint at
- **Skepticism** or doubts they express

**Extraction Template**:

```markdown
## Chunk X

### Key Points
- [ ] Main argument or insight 1
- [ ] Main argument or insight 2
- [ ] Supporting evidence or example

### Key Quotes (EXACT, with speaker)
- "Exact quote that captures a key idea" (Speaker)
- "Another memorable quote" (Speaker)

### Entities Mentioned
- People: [name, role/context if known]
- Organizations: [name]
- Concepts: [technical terms, theories, frameworks]
- Books/Resources: [specific titles mentioned]
- Events: [specific events referenced]

### Personal Journey Elements
- Background: [early life, education, formative experiences]
- Relationships: [key people and their influence]
- Turning points: [decisions that changed trajectory]
- Personal stories: [specific anecdotes revealed]

### Intellectual Framework
- Methodology: [how they work/think]
- Philosophy: [core beliefs about the field]
- Influences: [books, thinkers, frameworks]
- Evolution: [how views changed]

### Questions Raised
- What questions does this chunk raise?
- What remains unanswered?
- What tensions or contradictions exist?

### Connections
- Links to previous chunks
- Callbacks to earlier topics
- Foreshadowing of later topics
```

### Phase 3: Assembly

**Goal**: Synthesize all chunks into final structured output.

**Step 3.1: Deduplication & Clustering**

**Comprehensive Review Checklist**:

When reviewing extractions, verify these often-missed categories:

- [ ] **Personal journey**: Did we capture early life, education, formative moments?
- [ ] **Key relationships**: Did we track mentors, collaborators, influences?
- [ ] **Methodology**: Did we extract HOW they work, not just WHAT they found?
- [ ] **Philosophy**: Did we capture their core beliefs and frameworks?
- [ ] **Stories**: Did we include specific anecdotes, not just summaries?
- [ ] **Quotes**: Did we preserve vivid, exact quotes with context?
- [ ] **Evolution**: Did we track how their thinking changed?
- [ ] **Tensions**: Did we capture doubts, contradictions, open questions?

**Clustering Process**:
1. Merge duplicate or highly similar points
2. Cluster related points into themes
3. Identify the 3-5 major themes that cover the content
4. **Verify coverage**: Check if any major personal/professional arc is missing

**Step 3.2: Structured Summary Generation**

Create the final output with this structure:

```markdown
# [Content Title] - Summary & Interpretation

## Metadata
- **Source**: [original source/URL]
- **Type**: [podcast interview / academic paper / blog post]
- **Length**: [original word count/duration]
- **Key People**: [main speakers/authors mentioned]

## TL;DR (1-Minute Summary)
[2-3 sentences capturing the essence. Maximum 100 words.]

## Personal Journey (if applicable)
[For interviews/profiles: trace the subject's arc from background to current position]

### Early Life & Formation
- Background: [childhood, education, formative experiences]
- Key influences: [people, books, events that shaped thinking]
- Turning points: [decisions or moments that changed trajectory]

### Career Trajectory
- Major transitions: [key career moves and their rationale]
- Mentorship: [key relationships and their impact]
- Evolution: [how thinking/work changed over time]

## Core Arguments

### 1. [Theme Name]
[2-3 sentence synthesis of this theme across all relevant chunks]

**Key Evidence:**
- Point from chunk X
- Point from chunk Y
- Quote: "..." (Speaker)

### 2. [Theme Name]
...

### 3. [Theme Name]
...

## Methodology & Philosophy (if applicable)
[How they approach their work - often the most valuable insight]

### Research/Work Approach
- [Specific methodologies they use]
- [How they generate ideas]
- [Their decision-making frameworks]

### Intellectual Influences
- [Key thinkers, books, frameworks they reference]
- [How these shaped their thinking]
- [Quotes or concepts they frequently return to]

## Key Insights & Takeaways

### For [Relevant Audience 1, e.g., Researchers]
- Practical implication 1
- Practical implication 2

### For [Relevant Audience 2, e.g., Practitioners]
- Practical implication 1
- Practical implication 2

## Notable Quotes

> "[Most impactful quote - prioritize vivid, specific quotes over generic ones]"  
> — [Speaker], context if relevant

> "[Second most impactful quote]"  
> — [Speaker]

> "[Third quote - could be a specific detail or story that reveals character]"  
> — [Speaker]

## Gaps & Open Questions
- What wasn't covered?
- What contradictions exist?
- What would be good follow-up questions?
- What tensions or unresolved issues remain?

## Interpretation & Context

### Background Context
[2-3 paragraphs providing background on:
- Who are these people?
- Why does this conversation matter?
- What's the broader context of this discussion?]

### Critical Analysis
[Your interpretation:
- Strengths of the arguments presented
- Weaknesses or blind spots
- How this fits into broader discourse
- What you'd add or challenge]

### Related Resources
[If web search is available, suggest:
- Background reading on key topics
- Related discussions/interviews
- Contrasting viewpoints]
```

**Step 3.3: Information Density Enhancement (Optional)**

If the user wants deeper interpretation:

1. **Web Search for Context** (if available):
   - Search for background on key people mentioned
   - Look up technical terms or concepts discussed
   - Find related articles or contrasting viewpoints

2. **Cross-Reference**:
   - Compare claims in the content with external sources
   - Note where the content aligns with or diverges from consensus

3. **Enrich Output**:
   - Add footnotes with additional context
   - Include "See Also" section with related resources
   - Highlight controversial or debated points

## Quality Checklist

Before delivering the final summary, verify:

### Coverage & Completeness
- [ ] **Completeness**: Are all major topics from the original covered?
- [ ] **MECE**: Are themes mutually exclusive (minimal overlap) and collectively exhaustive (cover everything)?
- [ ] **Personal journey**: For interviews/profiles, is the subject's background and formation covered?
- [ ] **Key relationships**: Are important people (mentors, collaborators, influences) identified and their impact explained?
- [ ] **Methodology**: Is there a section explaining HOW they work, not just WHAT they found?

### Specificity & Detail
- [ ] **Accuracy**: Are quotes exact? Are attributions correct?
- [ ] **Stories**: Are there specific anecdotes, not just summaries of ideas?
- [ ] **Vivid details**: Are there concrete, memorable details that bring the content to life?
- [ ] **Philosophy**: Are the core beliefs and intellectual frameworks clearly articulated?

### Balance & Insight
- [ ] **Balance**: Is the summary proportional to the original (not over-weighting minor points)?
- [ ] **Evolution**: For long-form content, is there a sense of how thinking changed over time?
- [ ] **Tensions**: Are open questions, contradictions, or unresolved issues acknowledged?
- [ ] **Insight**: Does the interpretation add value beyond summarization?

### Common Omissions to Double-Check
- [ ] Did we include early life/formation experiences?
- [ ] Did we capture key turning points or decisions?
- [ ] Did we extract specific quotes (not just paraphrases)?
- [ ] Did we note the books/thinkers they reference?
- [ ] Did we identify what questions remain unanswered?

## Example

**Input**: A 2-hour podcast interview about AI safety

**Process**:
1. **Chunk**: Split into 8 chunks (~15 min each by transcript length)
   - Chunk 1: Introduction & background
   - Chunk 2: Current AI capabilities
   - Chunk 3: Safety concerns
   - ...

2. **Extract**: For each chunk, extract key points, quotes, entities

3. **Assemble**:
   - Cluster into themes: Technical Progress, Safety Challenges, Regulatory Landscape, Future Predictions
   - Generate structured output with quotes and interpretation

## Usage Notes

- **Adjust chunk size** based on content density: Dense academic papers may need smaller chunks; conversational podcasts can handle larger ones
- **Preserve original language**: If input is Chinese, output should be Chinese
- **Timestamps**: For podcasts/videos, preserve timestamps when available for easy reference
- **Speaker identification**: For interviews, clearly attribute quotes to speakers
- **Confidence levels**: Mark uncertain attributions or unclear audio with [unclear] or [paraphrased]

## Common Omissions to Avoid

Based on evaluation against baseline summaries, these elements are frequently missed:

### Personal/Background Elements
- **Early life experiences**: Childhood, education, formative moments
- **Family influences**: Parents, upbringing, early environment
- **Turning points**: Key decisions or moments that changed trajectory
- **Personal anecdotes**: Specific stories that reveal character

Example omission: Missing that "高光时刻是打DOTA" reveals personality

### Relationship Elements
- **Mentors and their impact**: Not just naming them, but explaining their influence
- **Collaborators**: Key partnerships and how they shaped work
- **Intellectual lineage**: Who influenced their thinking

Example omission: Missing how 凯明 influenced research methodology through 《金刚经》

### Methodology Elements
- **How they work**: Process, routines, decision-making
- **Philosophical influences**: Books, thinkers, frameworks
- **Evolution of thinking**: How views changed over time

Example omission: Missing "探索中的idea才是真正属于你的idea" philosophy

### Specific Details
- **Exact quotes**: Prefer vivid, specific quotes over generic summaries
- **Concrete stories**: Rejections, failures, breakthroughs with details
- **Vivid details**: What makes the story memorable or human

Example omission: Missing DiT "完全随机过程" story with "什么都没改再投" detail

### Tension/Uncertainty
- **Open questions**: What they admit they don't know
- **Contradictions**: Competing views or unresolved tensions
- **Doubts**: Skepticism about their own or field's direction

Example omission: Missing the JEPA认知转变 from质疑 to认同

## Example: What Good Extraction Looks Like

**Weak extraction**:
- "谢赛宁曾在FAIR工作"

**Strong extraction**:
- "谢赛宁在FAIR与何凯明合作，期间凯明送给他《金刚经》传达'凡所有相皆是虚妄'的研究哲学，影响了他对研究本质的理解"

**Weak extraction**:
- "他两次拒绝了OpenAI"

**Strong extraction**:
- "2018年博士毕业时，Ilya打电话邀请他加入OpenAI，但他选择了FAIR；2024年再次收到邀请，他依然选择拒绝，因为他已决定与杨立昆共同创业。他认为：'不是因为看见，所以相信；因为相信，所以看见'"

## Variations

### Quick Summary (Time-Constrained)
- Skip detailed extraction
- Use larger chunks (~10K tokens)
- Generate only TL;DR + Core Arguments

### Deep Analysis
- Use smaller chunks (~2K tokens)
- Add web search for every major claim
- Include extensive interpretation section
- Generate multiple "perspective" sections (e.g., technical view, business view, ethical view)

### Comparative Analysis
- Process multiple related pieces
- Extract from each individually
- Assembly phase compares and contrasts across sources
