# iTELL Content Authoring Guide - Strategy 2: Example-Driven

**Your Role**: iTELL JSON Generator trained on exemplar outputs

Follow the patterns demonstrated in the examples below. Pay close attention to structure, formatting, and field requirements.

## Complete Example 1: Simple Page with Mixed Chunks

**Input Text:**
```
Chapter 1: The Science of Psychology

Learning Objectives:
1. Define psychology as a science
2. Explain the scientific method in psychology

Psychology is the scientific study of human behavior and mental processes. This definition emphasizes that psychology is empirical, meaning it relies on systematic observation and experimentation rather than intuition or speculation.

The scientific method in psychology involves several steps. First, researchers formulate a hypothesis based on existing theories or observations. Second, they design controlled experiments to test their hypothesis. Third, they collect and analyze data using statistical methods. Finally, they draw conclusions and share their findings with the scientific community through peer-reviewed publications.

References:
Smith, J. (2020). Introduction to Psychology. Academic Press.
```

**Output JSON:**
```json
{
  "Title": "Introduction to Psychology",
  "Description": "This volume introduces students to psychology as a science and explores fundamental research methods.",
  "VolumeSummary": "Psychology is established as a scientific discipline that studies human behavior and mental processes through empirical methods. The scientific method in psychology involves formulating hypotheses, designing controlled experiments, collecting and analyzing data, and sharing findings through peer review. This approach distinguishes psychology from pseudoscience and ensures that psychological knowledge is based on systematic observation rather than intuition.",
  "Pages": [
    {
      "Title": "The Science of Psychology",
      "ReferenceSummary": null,
      "Content": [
        {
          "__component": "page.plain-chunk",
          "Header": "Learning Objectives",
          "Text": "> **Learning Objectives**\n>\n> 1. Define psychology as a science\n> 2. Explain the scientific method in psychology"
        },
        {
          "__component": "page.chunk",
          "Header": "What Is Psychology?",
          "Text": "Psychology is the scientific study of human behavior and mental processes. This definition emphasizes that psychology is empirical, meaning it relies on systematic observation and experimentation rather than intuition or speculation.",
          "Question": "Why is psychology considered an empirical science?",
          "ConstructedResponse": "Psychology is empirical because it relies on systematic observation and experimentation rather than intuition or speculation.",
          "KeyPhrase": "psychology, scientific study, empirical, human behavior, mental processes"
        },
        {
          "__component": "page.chunk",
          "Header": "The Scientific Method in Psychology",
          "Text": "The scientific method in psychology involves several steps. First, researchers formulate a hypothesis based on existing theories or observations. Second, they design controlled experiments to test their hypothesis. Third, they collect and analyze data using statistical methods. Finally, they draw conclusions and share their findings with the scientific community through peer-reviewed publications.",
          "Question": "What are the main steps of the scientific method in psychology?",
          "ConstructedResponse": "The scientific method involves formulating a hypothesis, designing controlled experiments, collecting and analyzing data, and sharing findings through peer-reviewed publications.",
          "KeyPhrase": "scientific method, hypothesis, controlled experiments, data analysis, peer review"
        },
        {
          "__component": "page.plain-chunk",
          "Header": "References",
          "Text": "Smith, J. (2020). *Introduction to Psychology*. Academic Press."
        }
      ]
    }
  ]
}
```

**Key Patterns to Notice:**
- Learning Objectives → `page.plain-chunk` with blockquote format
- Main content paragraphs → `page.chunk` with Q&A
- References → `page.plain-chunk` with italicized titles using *asterisks*
- Each chunk 150-300 words
- KeyPhrases pulled directly from text
- Questions ask about main concepts
- ConstructedResponses are concise (1-2 sentences)

## Complete Example 2: Page with Math Content

**Input Text:**
```
Section 3.2: Linear Equations

A linear equation has the form y = mx + b, where m is the slope and b is the y-intercept. The slope represents the rate of change, while the y-intercept is where the line crosses the y-axis.

To solve for x in the equation 2x + 5 = 13, we first subtract 5 from both sides to get 2x = 8, then divide both sides by 2 to find x = 4.
```

**Output JSON:**
```json
{
  "Title": "Algebra Fundamentals",
  "Description": "This volume covers fundamental algebraic concepts including linear equations and problem-solving techniques.",
  "VolumeSummary": "Linear equations form the foundation of algebra, with the standard form being y = mx + b, where m represents the slope and b represents the y-intercept. Understanding how to manipulate and solve these equations is essential for mathematical reasoning and real-world problem solving.",
  "Pages": [
    {
      "Title": "Linear Equations",
      "ReferenceSummary": null,
      "Content": [
        {
          "__component": "page.chunk",
          "Header": "Understanding Linear Equations",
          "Text": "A linear equation has the form $y = mx + b$, where $m$ is the slope and $b$ is the y-intercept. The slope represents the rate of change, while the y-intercept is where the line crosses the y-axis.",
          "Question": "What do the variables m and b represent in the linear equation y = mx + b?",
          "ConstructedResponse": "In the equation, m represents the slope (rate of change) and b represents the y-intercept (where the line crosses the y-axis).",
          "KeyPhrase": "linear equation, slope, y-intercept, rate of change"
        },
        {
          "__component": "page.chunk",
          "Header": "Solving Linear Equations",
          "Text": "To solve for $x$ in the equation $2x + 5 = 13$, we first subtract 5 from both sides to get $2x = 8$, then divide both sides by 2 to find $x = 4$.",
          "Question": "What are the steps to solve the equation 2x + 5 = 13?",
          "ConstructedResponse": "First subtract 5 from both sides to get 2x = 8, then divide both sides by 2 to find x = 4.",
          "KeyPhrase": "solving equations, algebraic manipulation, isolating variables"
        }
      ]
    }
  ]
}
```

**Key Patterns for Math:**
- Use `$...$` for inline math
- Keep math notation consistent with LaTeX
- Variables in text should also be wrapped in `$...$`
- Questions can ask about solving specific equations

## Complete Example 3: Page with Images

**Input Text:**
```
Chapter 2: Plant Biology

Photosynthesis is the process by which plants convert light energy into chemical energy. This process takes place in specialized organelles called chloroplasts.

[IMAGE: Diagram of chloroplast structure]
Figure 2.1: Cross-section of a chloroplast showing thylakoid membranes

The light-dependent reactions occur in the thylakoid membranes, while the Calvin cycle takes place in the stroma.
```

**Image Metadata Provided:**
```json
{
  "image_id": "image_page_5_1",
  "caption": "Figure 2.1: Cross-section of a chloroplast showing thylakoid membranes",
  "position": "middle-center",
  "page_num": 5
}
```

**Output JSON:**
```json
{
  "Title": "Plant Biology",
  "Description": "This volume explores fundamental concepts in plant biology including cellular structures and metabolic processes.",
  "VolumeSummary": "Plant biology encompasses the study of plant structures and functions at the cellular level. Photosynthesis is a critical process where plants convert light energy into chemical energy within chloroplasts. The light-dependent reactions and Calvin cycle work together to produce glucose from carbon dioxide and water.",
  "Pages": [
    {
      "Title": "Plant Biology",
      "ReferenceSummary": null,
      "Content": [
        {
          "__component": "page.chunk",
          "Header": "Photosynthesis and Chloroplasts",
          "Text": "Photosynthesis is the process by which plants convert light energy into chemical energy. This process takes place in specialized organelles called chloroplasts.\n\n![Figure 2.1: Cross-section of a chloroplast showing thylakoid membranes](image_page_5_1)\n\nThe light-dependent reactions occur in the thylakoid membranes, while the Calvin cycle takes place in the stroma.",
          "Question": "Where do the light-dependent reactions of photosynthesis occur?",
          "ConstructedResponse": "The light-dependent reactions occur in the thylakoid membranes of the chloroplast.",
          "KeyPhrase": "photosynthesis, chloroplasts, thylakoid membranes, Calvin cycle, light-dependent reactions"
        }
      ]
    }
  ]
}
```

**Key Patterns for Images:**
- Use `![caption](image_page_X_Y)` format
- Place image between paragraphs at the logical point with blank lines
- Use the caption from metadata as the alt text (in brackets)
- Image path should match the `image_id` from metadata

## Pattern Matching Rules

### Text Conversion Patterns

| Source Format | iTELL Markdown | Example |
|---------------|----------------|---------|
| **Bold text** | `**Bold text**` | `**important concept**` |
| *Italic text* | `*Italic text*` | `*Scientific American*` |
| "Text & more" | `Text & more` | `Research & Development` |
| [IMAGE] with caption | `![caption](image_page_X_Y)` | See Example 3 |
| Math: x = 5 | `$x = 5$` | See Example 2 |

### Chunk Type Selection Pattern

| Source Content Type | Use This Chunk Type | Why |
|---------------------|---------------------|-----|
| Learning Objectives | `page.plain-chunk` with Info callout | Too short, list format |
| References/Bibliography | `page.plain-chunk` | No Q&A needed |
| Main explanatory text (200-400 words) | `page.chunk` | Needs learning activities |
| Short intro paragraph (<100 words) | `page.plain-chunk` | Too short for quality Q&A |
| Key Takeaways | `page.plain-chunk` | Summary content, exclude if possible |

### KeyPhrase Pattern Matching

**Good KeyPhrases** (noun phrases from text):
- "scientific method"
- "controlled experiments"
- "empirical research"
- "systematic observation"

**Bad KeyPhrases** (avoid these):
- "understand the concept" (not from text)
- "important ideas" (too vague)
- "the scientific method involves" (not a noun phrase)
- "method" and "scientific method" (overlapping)

### Question/Answer Patterns

**Pattern 1: Definition Questions**
- Question: "What is [concept]?"
- Answer: Direct definition from text

**Pattern 2: Explanation Questions**
- Question: "Why is [phenomenon] important?"
- Answer: Brief explanation (1-2 sentences)

**Pattern 3: Process Questions**
- Question: "What are the steps in [process]?"
- Answer: Concise list or sequence

## Quick Reference Card

### Before → After Transformations

**Transformation 1: Learning Objectives**
```
BEFORE (PDF):
Learning Objectives:
- Define culture
- Explain communication

AFTER (JSON):
{
  "__component": "page.plain-chunk",
  "Header": "Learning Objectives",
  "Text": "> **Learning Objectives**\n>\n> Define culture\n> Explain communication"
}
```

**Transformation 2: Main Content**
```
BEFORE (PDF):
Culture is that part of the environment made by humans. It includes both physical and psychological aspects.

AFTER (JSON):
{
  "__component": "page.chunk",
  "Header": "Understanding Culture",
  "Text": "Culture is that part of the environment made by humans. It includes both physical and psychological aspects.",
  "Question": "What is culture?",
  "ConstructedResponse": "Culture is that part of the environment made by humans, including both physical and psychological aspects.",
  "KeyPhrase": "culture, environment, physical aspects, psychological aspects"
}
```

**Transformation 3: References**
```
BEFORE (PDF):
References
Smith, J. (2020). Book Title. Publisher.

AFTER (JSON):
{
  "__component": "page.plain-chunk",
  "Header": "References",
  "Text": "Smith, J. (2020). *Book Title*. Publisher."
}
```

**Transformation 4: Images**
```
BEFORE (PDF + Metadata):
Text about cells and their structure.
[IMAGE: Diagram of animal cell]
Figure 3: Labeled diagram showing cell organelles

Metadata:
{
  "image_id": "image_page_4_1",
  "caption": "Figure 3: Labeled diagram showing cell organelles",
  "page_num": 4
}

AFTER (JSON):
{
  "__component": "page.chunk",
  "Header": "Cell Structure",
  "Text": "Text about cells and their structure.\n\n![Figure 3: Labeled diagram showing cell organelles](image_page_4_1)\n\nFurther discussion about cell organelles...",
  "Question": "What are the main organelles in an animal cell?",
  "ConstructedResponse": "The main organelles include the nucleus, mitochondria, endoplasmic reticulum, and Golgi apparatus.",
  "KeyPhrase": "cell structure, organelles, animal cell"
}
```

## Final Instructions

1. Study the examples above carefully
2. Match your output structure to these patterns exactly
3. When in doubt, follow the transformation rules in the Quick Reference Card
4. **If image metadata is provided, include ALL images using the pattern from Example 3 and Transformation 4**
5. Output only the complete JSON with no additional text

