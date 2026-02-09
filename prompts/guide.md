# iTELL Content Authoring Guide

## What is iTELL?

Intelligent Texts for Enhanced Language Learning (iTELL) is a computational framework designed to enable content managers to transform any machine-readable text into interactive, intelligent content within a web app. iTELL leverages theories of reading comprehension to provide opportunities for users to generate knowledge about the materials they engage with through constructed responses and summary writing. These responses and summaries are automatically scored by large language models (LLMs), specifically trained to generate scores that inform actionable, qualitative feedback for users. Additionally, iTELL includes a structured think-aloud assistant, which helps users make inferences and relevant elaborations about the content through self-explanations. Feedback from these AI integrations supports multiple goals, such as guiding learning, correcting misconceptions, reviewing missed topics, preparing for upcoming materials, connecting content to real-world contexts, and helping users deepen their understanding.

## Introduction to the Content Authoring Guide

This is the official format guide for iTELL volumes published by LEAR Lab. This guide will show you how to create and edit an iTELL volume using the iTELL JSON format. Adhering to this guide will ensure that your text conforms to iTELL standards for style and formatting.

## Quick Reference: Key Decisions for JSON Generation

### Volume-Level Fields (REQUIRED)

- **Title**: Volume title (required)
- **Description**: 1-2 sentence description (required)
- **VolumeSummary**: 4-8 sentence comprehensive summary synthesizing all pages (required)
- **Pages**: Array of page objects (required)

### Page-Level Fields (REQUIRED)

- **Title**: Page title in Title Case (required)
- **ReferenceSummary**: Reproduce the page summary if one is provided in the source material (optional)
- **Content**: Array of chunk objects (required)

### Chunk Types

1. **page.chunk** - Standard chunks with learning activities
   - Required fields: `__component`, `Header`, `Text`, `Question`, `ConstructedResponse`, `KeyPhrase`
   - Use for: Main content sections (200-400 words)

2. **page.plain-chunk** - Chunks without learning activities
   - Required fields: `__component`, `Header`, `Text`
   - Use for: Learning Objectives, References, Key Takeaways, short sections

### Markdown Formatting Quick Reference

- Paragraphs: Separate with blank lines
- Bold: `**text**`
- Italics: `*text*`
- Ampersands: `&` (use as-is)
- Learning Objectives: Blockquote with bold header
- Math inline: `$...$`
- Math block: `$$...$$`

### Generation Best Practices

1. Always include Title, Description, VolumeSummary at volume level
2. Use Title Case for all headers
3. Keep chunks 200-400 words
4. Keyphrases: 3-5 terms, comma-separated, from the chunk text
5. Questions: An open-ended reading comprehension question
6. ConstructedResponse: A reference answer that will be used to score student responses
7. Balance chunk types: plain-chunk for supplementary, chunk for main content

## Structure of iTELL Volume

The core organizational unit is the **page**, which usually corresponds to an organization unit in the source text such as the chapter or a chapter section, and is not related to page boundaries in the printed source text. Each page belongs to a volume.

Pages are divided into **chunks**. Chunks are short segments of content (about 1-3 paragraphs) that typically have a header. They come in two flavors: the **text chunk** and the **plain chunk**. The text chunk has learning activities associated with it such as constructed responses. A plain chunk is a text chunk without learning activities and is appropriate for supplementary material such as learning objectives, a keyword list, or appendices.

## Adapting the Structure of the Source Material for iTELL

Content authors have broad editorial power to change the organizational structure of a text when adapting it for iTELL, including removing or adding content as needed.

### Things You Can Modify

- Organization of content within chapters, pages, and chunks
- Formatting of text

### Things You Should Always Modify

- Multimedia elements like images should be represented using markdown image syntax
- Adapt the content to fit the interactive and digital format of iTELL
- Check for and correct any grammatical or typographical errors

## Title Case Style

Headers and titles should use title case, with major words capitalized and minor words lowercase.

## JSON Structure Overview

Each iTELL volume is represented as a single JSON file with the following top-level structure:

```json
{
  "Title": "Volume Title",
  "Description": "Brief volume description",
  "VolumeSummary": "Comprehensive summary of volume content",
  "Pages": [
    {
      "Title": "Page Title",
      "ReferenceSummary": "The summary of the page content as it appears in the source material",
      "Content": [...]
    }
  ]
}
```

**Important**: Title, Description, and VolumeSummary are **required fields** at the volume level and must be included in every JSON file.

## Volume

A volume in iTELL has several main fields that must be populated:

- **Title**: The title of the volume.
- **Description**: A brief (one to two sentences) description of the volume. This will describe the goals of the volume and the target audience. 
- **VolumeSummary**: A comprehensive summary of the volume content that synthesizes all pages.

### How to Generate a Volume Summary

The volume summary should be a comprehensive overview (typically 4-8 sentences) that synthesizes the main topics and themes covered across all pages in the volume. It should provide enough information to give readers a clear understanding of what to expect from the volume without going into excessive detail. The summary should:

- Cover the main topics from all pages in the volume
- Flow logically from one concept to the next
- Be written in complete, well-structured sentences
- Avoid bullet points or lists
- Capture the essence and scope of the entire volume

## Page

Pages in iTELL have three main fields that must be populated:

- **Title**: Used as the heading for the page. It appears at the beginning of the page and in the table of contents on the left.
- **ReferenceSummary**: If the source text includes a summary for the page content, include it here.
- **Content**: This will be an array of chunks (objects with __component, Header, Text, and potentially Question, ConstructedResponse, KeyPhrase).

### Page Structure Example

```json
    {
      "Title": "18.1 Intercultural Communication",
      "Content": [
        {
          "__component": "page.plain-chunk",
          "Header": "Learning Objectives",
          "Text": "> **Learning Objectives**\n>\n> Content here"
        },
        {
          "__component": "page.chunk",
          "Header": "What is Intercultural Communication?",
          "Text": "Communication is the sharing of understanding...",
          "Question": "What is culture according to Donald Klopf?",
          "ConstructedResponse": "Culture is described as 'that part of the environment made by humans.'",
          "KeyPhrase": "intercultural communication, culture, psychological aspects of culture"
        }
      ]
    }
```

### How to Split Page Content into Chunks

- Select text chunks of around 300 words (can range from 200-400 words depending on natural breaks).
- Select chunks that form a coherent and cohesive passage about a topic or subdivision of the topic. This topic should be reflected in the header.
- Consider splitting long, original paragraphs into multiple paragraphs.
- When adapting from source material, you may split a subsection into multiple chunks. You will likely need to create a new header when subdividing an organization unit into multiple chunks.
- You may number the chunks as in `[Original Header]` and `[Original Header] II`
- Alternatively, you may create a new header for one or both chunks based on the content.
- Each chunk should have a clear, descriptive header in Title Case.

## Chunk

There are two types of chunks:

- **Chunks** (`page.chunk`) are used for most content and include interactive feedback features.
- **Plain-Chunks** (`page.plain-chunk`) are used for text content without interactive features. Use these for content such as learning objectives, references, and short introductory sections.  

### Components of a Chunk

| Field | Description | Required for page.chunk | Required for page.plain-chunk |
|---|---|---|---|
| `__component` | The type of chunk: "page.chunk" or "page.plain-chunk" | ✓ | ✓ |
| Header | Use title case capitalization (e.g., "Introduction to Macroeconomics") | ✓ | ✓ |
| Text | The main body of text formatted as Markdown | ✓ | ✓ |
| Question | A question related to the chunk content, used for generating constructed responses | ✓ | ✗ |
| ConstructedResponse | A model answer for the question, used for scoring constructed responses | ✓ | ✗ |
| KeyPhrase | Important terms or concepts from the chunk content, comma-separated | ✓ | ✗ |

### Complete Chunk Examples

#### Example 1: Normal Chunk (page.chunk)

```json
{
  "__component": "page.chunk",
  "Header": "What is Intercultural Communication?",
  "Text": "Communication is the sharing of understanding and meaning (Pearson, J. and Nelson, P., 2000), but what is intercultural communication? If you answered, \"The sharing of understanding and meaning across cultures,\" you'd be close, but the definition requires more attention.\n\nWhat is a culture? Where does one culture stop and another start? How are cultures created, maintained, and dissolved? Donald Klopf described culture as \"that part of the environment made by humans\" (Klopf, D., 1991). From the building we erect that represents design values to the fences we install that delineate borders, our environment is a representation of culture, but it is not all that is culture.",
  "Question": "What is culture according to Donald Klopf?",
  "ConstructedResponse": "Culture is described as 'that part of the environment made by humans.'",
  "KeyPhrase": "intercultural communication, culture definition, psychological aspects of culture, communication context, nonverbal feedback"
}
```

#### Example 2: Plain Chunk for Learning Objectives (page.plain-chunk)

```json
{
  "__component": "page.plain-chunk",
  "Header": "Learning Objectives",
  "Text": "> **Learning Objectives**\n>\n> 1. Define and discuss how to facilitate intercultural communication.\n> 2. Define and discuss the effects of ethnocentrism."
}
```

#### Example 3: Plain Chunk for References (page.plain-chunk)

```json
{
  "__component": "page.plain-chunk",
  "Header": "References",
  "Text": "Klopf, D. (1991). *Intercultural encounters: The fundamentals of intercultural communication* (2nd ed.). Inglewood, CA: Morton Publishing Company.\n\nPearson, J., & Nelson, P. (2000). *An introduction to human communication: Understanding and sharing.* Boston, MA: McGraw-Hill."
}
```

### When should the normal chunk be used?

Normal chunks are used for standard content sections that require keyphrase extraction and constructed responses.

### When should the "plain chunk" be used?

Plain chunks are different from normal chunks because they do not have keyphrases extracted or constructed responses. A chunk with minimal text in paragraph form should be added as a Plain-Chunk.

Use plain chunks for content like abstracts and references in research papers or content where sections are too short for quality keyphrases and constructed responses. Examples:

- Learning Objectives
- Abstracts
- References
- Chunks with only tables

### How to generate Keyphrases for normal chunks?

The keyphrases should be 3 to 5 terms that are pulled from the chunk. The keyphrases should represent important concepts in the chunk. A good keyphrase will be concise, and will likely be a noun phrase, like "patent infringement" or "epistemological belief." A bad keyphrase will be wordy and vague, like "extend the idea of scope," or will end mid-sentence like "defective condition unreasonably dangerous." Make sure the keyphrases do not overlap. For example, "sale" and "contract for sale" should not both be provided as keyphrases. The keyphrases will be a single line of terms each separated by a comma.

### How to write a question and constructed response for normal chunks?

The question and constructed response should be a question/answer pair that addresses a main idea in the chunk text. The constructed response will serve as a reference answer for evaluating student responses to the question. The constructed response should be a concise answer, usually a phrase or a single sentence. The question should have a clear, correct answer that can be found in the chunk text. Avoid yes/no questions.

## Special Formatting Options

iTELL provides several custom components that can be used to enhance content presentation and create interactive learning experiences. These components should be used strategically to emphasize important information, provide supplementary context, and engage learners.

### Callouts

Callouts are boxed sections that visually offset content from the main text. Use blockquotes to create callouts.

**Best Practices for Callouts:**

- Use callouts sparingly—too many can disrupt reading flow
- Keep callout content concise (typically a list or a short paragraph)
- Ensure the callout content is directly relevant to the surrounding text

#### Info Callouts

Info callouts should be used for supplementary information that supports the main content, such as learning objectives, definitions, or key concepts.

```markdown
> **Learning Objectives**
>
> Your content here with markdown formatting
```

**When to use:**

- Learning objectives at the beginning of a page
- Key definitions or terminology
- Important background information
- Helpful tips or reminders

#### Warning Callouts

Warning callouts should be used to alert learners to common mistakes, misconceptions, or important cautions.

```markdown
> **Warning**
>
> Your warning content here with markdown formatting
```

**When to use:**

- Common errors or misconceptions
- Important limitations or exceptions
- Critical safety or ethical considerations
- Prerequisites that must be met

### General Callouts

General callouts can be used for any content that should be visually distinguished but doesn't fit the info or warning categories.

```markdown
> Your content here with markdown formatting
```

**When to use:**

- Examples or case studies
- Historical context or interesting facts
- Additional explanations or clarifications

### Math Equations

iTELL supports LaTeX-style mathematical notation for both inline and block equations.

**Inline Math:**

Use inline math for equations within text, like `The formula $E = mc^2$ demonstrates mass-energy equivalence.`

```markdown
$E = mc^2$
```

**Block Math:**

Use block math for displayed equations that should appear on their own line.

```markdown
$$\int_{0}^{\infty} e^{-x^2} dx = \frac{\sqrt{\pi}}{2}$$
```

**Best Practices for Math:**

- Use inline math (`$...$`) for simple expressions and variables within sentences
- Use block math (`$$...$$`) for complex equations that deserve emphasis
- Ensure LaTeX syntax is correct
- Define variables and notation before or immediately after introducing them
- Number important equations if you need to reference them later

### General Formatting Guidelines

- **Valid Markdown**: All content within custom components must use valid Markdown structure
- **Consistency**: Use formatting elements consistently throughout the volume
- **Purpose**: Each special formatting element should serve a clear pedagogical purpose—don't use them solely for visual variety
- **Blockquotes**: Use blockquotes (>) for callout sections

## Which Content Should We Exclude

Some texts may include reflection questions, end-of-chapter summaries, and other activities. These should generally be excluded when adapting source material for iTELL to avoid redundancy. Examples of common elements that should be excluded are "Summary," "Key Takeaway," and "Review Questions". Questions in the form of math exercises, however, should be included in the page.

- Exclude any summaries of the page (include in the ReferenceSummary instead).
- Include images using markdown image syntax when provided in metadata.
- Exclude chunks that have review questions which have the same functions as iTELL's Question and ConstructedResponse pair.

## Headers

- **Hierarchy and Structure**: Maintain a clear hierarchical structure with distinct levels of headers. Use H3 for subheaders inside Chunks.
- **Uniform Formatting**: Use consistent capitalization and numbering across all headers.
- **Capitalization**: Use Title Case for all headers. Example: '1. Introduction to Macroeconomics'.
- **Logical Sequence**: Ensure that the headers follow a logical sequence and accurately reflect the content hierarchy.

### What Should I Do if the Source Material Does Not Include a Header?

Read the content and write a header yourself that matches the content as well as the style and tone of other headers in the text.

## Best Practices for iTELL JSON

1. **Always include all required fields**: Title, Description, VolumeSummary at volume level; all chunk fields for page.chunk
2. **Use proper Markdown formatting**: Separate paragraphs with blank lines, use **bold** and *italic* syntax correctly
3. **Maintain consistent structure**: All pages in Pages array, all chunks in Content array
4. **Apply Title Case consistently**: All headers and titles should use Title Case
5. **Balance chunk types**: Use page.plain-chunk for supplementary material (objectives, references), page.chunk for main content
6. **Keep chunks focused**: 200-400 words per chunk, centered on a single topic
7. **Write natural keyphrases**: Pull directly from text, use noun phrases
8. **Create clear Q&A pairs**: Questions should be specific, answers should be concise (1-2 sentences)
9. **Validate JSON structure**: Ensure proper nesting, commas, and brackets

## Common Mistakes to Avoid

1. **Missing required fields**: Every page.chunk must have Question, ConstructedResponse, and KeyPhrase
2. **Incorrect __component values**: Must be exactly "page.chunk" or "page.plain-chunk"
3. **Malformed Markdown**: Missing blank lines between paragraphs, incorrect bold/italic syntax
4. **Overly long chunks**: Keep chunks under 500 words
5. **Generic keyphrases**: Avoid vague terms like "important concepts" or "key ideas"
6. **Yes/no questions**: Questions should require substantive answers
7. **Missing Title/Description/VolumeSummary**: These are required at volume level
8. **Inconsistent capitalization**: Use Title Case for all headers
9. **Bullet points in VolumeSummary**: Use complete, flowing sentences instead