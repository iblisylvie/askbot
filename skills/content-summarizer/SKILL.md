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

### Phase 0: Input Preprocessing (if needed)

Before chunking, check the input format:

- **If the input is a PDF file**: Run `/root/askbot/scripts/pdf2md.py <pdf-path>` to convert it to markdown first. Use the resulting markdown as the input for Phase 1.
- **If the input is already text/markdown**: Proceed directly to Phase 1.

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

### Charts & Visuals (if present in chunk)
- **Title/Description**: [what the chart shows]
- **Type**: [bar/line/pie/table/flowchart/diagram/etc.]
- **Source Location**: [e.g., "Figure 3", "Table 2", "page 15" — MUST preserve the original identifier]
- **Key Data Points**: [the most important numbers, trends, or comparisons]
- **Why It Matters**: [what conclusion or insight this chart supports]
- **Has Image Embed?**: [YES / NO — be explicit. Some figures (e.g., text-based tables, inline ASCII charts) have a caption but no `![](path)` image in the source]
- **Original Image Embed**: [if YES, copy-paste the EXACT `![](path)` markdown here, character-for-character. Do NOT retype or paraphrase the path. Do NOT summarize. If NO, write "NONE"]
- **Suggested Usage**: [should this be preserved as a reference, or summarized in text?]

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

**Inline Visuals**: When a figure, chart, table, or diagram directly supports a specific argument, **embed it inline within that argument's section** rather than isolating it in a separate gallery. Place the image near the text that references it, so the visual evidence and its explanation form a coherent paragraph.

**Image Path Rules (critical for accuracy):**
1. **Only embed `![](path)` if the source explicitly contained an image for this figure** (extraction field "Has Image Embed?" = YES). Text-only figures MUST NOT receive a fabricated image embed.
2. **Copy-paste the path exactly** from the extraction field "Original Image Embed". Never retype, abbreviate, or "fix" the path. A single character difference breaks the image.
3. **After assembly, verify**: no two distinct figures share the same `![](path)`. If they do, you misassigned an image — trace back to the extraction notes and correct it.

### 1. [Theme Name]
[2-3 sentence synthesis of this theme across all relevant chunks]

**Key Evidence:**
- Point from chunk X
- Point from chunk Y
- Quote: "..." (Speaker)
- **Visual evidence** (if relevant): If a figure/table from the source directly illustrates this theme, embed it here with a brief caption explaining what it shows and why it matters for this argument. Preserve original `![](path)` image links for markdown sources.

### 2. [Theme Name]
...

### 3. [Theme Name]
...

## Key Data & Visuals (Optional Fallback)

**Prefer inline embedding**: Charts, graphs, tables, diagrams, and figures should first be embedded within the Core Arguments or other relevant sections where they provide direct evidence (see "Inline Visuals" guidance above).

**Use this section only for**: Visuals that do not have a natural thematic home, or for a concise index/overview of all significant figures when the source contains many visuals.

For visuals placed here, produce an entry following this format:

```markdown
**[Original Identifier]**: [brief description of what it shows]
- **Location**: [Figure X / Table Y / page N]
- **Key Evidence**: [the most important numbers, trends, or comparisons in 2-3 sentences]
- **Why It Matters**: [what conclusion or insight this visual supports]
```

**For PDF inputs specifically**:
- Preserve the original figure/table numbering (e.g., "Figure 1", "Table 3") so readers can locate it in the source document
- If the PDF page was visible, include the page number in parentheses: "(see original Figure 3, page 15)"
- If a chart is the densest or most persuasive piece of evidence for a claim, do not skip it. Either preserve a reference or describe its conclusion in the relevant theme section

**For Markdown inputs specifically**:
- If the source contains `![](path)` image embeds (e.g., `![](images/figure1.png)`), **preserve the original markdown image syntax in the summary output** whenever the image path remains valid (e.g., summary is saved in the same directory as the source)
- Do NOT strip out image links and replace them with plain text descriptions. Keep the image embed so the summary remains visually inspectable
- **Do NOT invent image embeds for text-only figures**. If a figure caption exists but the source has no `![](...)` nearby, describe the figure in text/italics instead of fabricating an image link.
- **Copy-paste paths character-for-character** from the source. Never retype long hash-based filenames from memory.
- If the summary is saved to a different directory and paths would break, either: (a) copy the image files alongside the summary, or (b) update the relative paths, or (c) preserve the image link and note the path may need adjustment

**Option A - Preserve Original Reference** (when the image is accessible and adds significant value):
- Include a brief description of what the chart shows
- Reference the original chart location explicitly (e.g., "see original Figure 3")
- For markdown sources, keep the `![](path)` embed in the output
- Note the key takeaway in 1-2 sentences

**Option B - Textual Redescription** (when the image is not accessible, or the data is more important than the visual):
- Describe the core comparison, trend, or distribution in words
- Include the most important specific numbers or percentages
- Explain why this data point matters in context

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
- [ ] **Charts & visuals — integrated inline**: Are figures, charts, and tables embedded within the relevant Core Arguments or sections where they provide direct evidence, rather than isolated in a separate gallery? Each visual should appear near the text that discusses it.
- [ ] **Image embeds preserved**: If the source is markdown and contains `![](path)` image links, are those image embeds preserved in the summary output (not stripped to plain text)?
- [ ] **No fabricated images**: Text-only figures (those without `![](...)` in the source) do NOT have image embeds invented for them.
- [ ] **Image paths exact**: Every `![](path)` in the output is a character-perfect copy from the source. No typos in long hash filenames. No two distinct figures share the same path unless the source also does.

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
- [ ] Did we preserve original figure/table identifiers (Figure X, Table Y, page N) for all significant visuals, especially from PDFs?
- [ ] Did we preserve original markdown image embeds (`![](path)`) in the summary output when the source is markdown? Do not strip image links to plain text.
- [ ] Did we embed visuals **inline within the relevant arguments/sections** rather than dumping them all into an isolated "Key Data & Visuals" gallery? Each figure should appear where it is discussed.

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
- **Charts and data visuals — embed inline**: Place visuals within the Core Arguments or relevant sections where they provide direct evidence, rather than isolating them in a separate gallery. A figure about architecture should appear in the architecture argument; a performance chart should appear where performance is discussed. Only use a standalone "Key Data & Visuals" section as a fallback for visuals without a natural thematic home. Do not silently omit high-density visual evidence. **For PDFs: always preserve the original figure/table number (e.g., "Figure 1", "Table 3") and page location so the reference remains traceable to the source document.**

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
