# iTELL Content Authoring Guide

## What is iTELL?

Intelligent Texts for Enhanced Language Learning (iTELL) is a computational framework designed to enable content managers to transform any machine-readable text into interactive, intelligent content within a web app. iTELL leverages theories of reading comprehension to provide opportunities for users to generate knowledge about the materials they engage with through constructed responses and summary writing. These responses and summaries are automatically scored by large language models (LLMs), specifically trained to generate scores that inform actionable, qualitative feedback for users. Additionally, iTELL includes a structured think-aloud assistant, which helps users make inferences and relevant elaborations about the content through self-explanations. Feedback from these AI integrations supports multiple goals, such as guiding learning, correcting misconceptions, reviewing missed topics, preparing for upcoming materials, connecting content to real-world contexts, and helping users deepen their understanding.

## Introduction to the Content Authoring Guide

This is the official format guide for iTELL volumes published by LEAR Lab. This guide will show you how to create and edit an iTELL volume using iTELL's content management system (CMS). Adhering to this guide will ensure that your text conforms to iTELL standards for style and formatting.

## The iTELL Library Structure

The iTELL library is a collection of volumes. Volumes may be an entire textbook or a single-page document. Each volume will have its own URL and iTELL web app associated with it. All volumes are part of the iTELL library.

A collection of volumes belonging to a single organization is a **stack**.

## Structure of iTELL Volume

Volumes can optionally be divided into modules and chapters. The core organizational unit is the **page**, which can be thought of conventionally as a chapter section (i.e. one page could be section 12.3 of chapter 12). Each page belongs to a volume.

Pages are divided into **chunks**. Chunks are short segments of content (about 1-3 paragraphs) that typically have a header. They come in three flavors: the **text chunk**, the **plain chunk**, and the **video chunk**. The text chunk has learning activities associated with it such as constructed responses. A plain chunk is a text chunk without learning activities and is appropriate for supplementary material such as a keyword list or appendices. A video chunk also has learning activities associated with it and typically consists of a single YouTube video.

## Adapting the Structure of the Source Material for iTELL

Content authors should aim for a volume that is open-source and functions well in iTELL (i.e., contains enough text or videos and has a conventional structure). iTELL volumes are typically based on pre-existing learning materials. Content authors have broad editorial power to change the organizational structure of a text when adapting it for iTELL, including removing or adding content as needed.

### Things That Cannot Be Changed

- The core structure of iTELL volumes
- Mandatory fields must be populated
- Pre-defined styles and branding guidelines

### Things You Can Modify

- Organization of content within chapters, pages, and sections (chunks in iTELL)
- Formatting of text
- Inclusion of multimedia elements like images and videos

### Things You Should Always Modify

- Ensure that all content is up-to-date and accurately reflects the source material
- Adapt the content to fit the interactive and digital format of iTELL
- Check for and correct any grammatical or typographical errors

## Style Guide

### Title Case Capitalization

Headers and titles should use title case, with major words capitalized and minor words lowercase.

### Page Titles

- **Clear and Descriptive**
- **Consistent Formatting**: Use title case and ensure consistent formatting across all chapters

## How to Split a Page into Chunks

### Lengthwise (not suggested):
**1-4 Paragraphs**: Each chunk should contain 1 to 4 paragraphs. Learning activities will be generated for each chunk, and iTELL works best when learning activities are frequent.

### Content-wise (suggested):
- Select text chunks of around 500 words.
- Select chunks that form a coherent and cohesive passage about a topic or subdivision of the topic. This topic should be reflected in the header.
- Consider splitting long, original paragraphs into multiple paragraphs.
- When adapting from source material, you may split a section into multiple chunks. You will likely need to create a new header when subdividing an organization unit into multiple chunks.
- You may number the chunks as in `[Original Header]` and `[Original Header] II`
- You can hide the second chunk title by setting `[Original Header] II` ShowHeader field to False.
- Alternatively, you may create a new header for one or both chunks based on the content.

## Page

Pages must always have a relation to an iTELL volume. This can be done by selecting the volume from the drop down menu. The volume must be created first. The process is the same for adding chapter relations. Chapters may be further organized into modules.

- **Title**: Used as the heading for the page. It appears at the beginning of the page and in the table of contents on the left.
- **ReferenceSummary**: A reference or model summary of the page content. If the source text includes a summary, include it here. Otherwise, leave this blank. This should not be used except for experimental design.
- **Content**: In the CMS, this is called a "DynamicZone." It can be populated with chunks.

## Chunk

There are three types of chunks:
- **Chunks** are used for most content and include interactive feedback features.
- **Plain-Chunks** are used for text content without interactive features. Use these for content such as learning objectives.
- **Video chunks** consist of a single YouTube video and include interactive feedback features.

### Components of a Chunk

| Component | Description |
|-----------|-------------|
| **Header** | Use title case capitalization (e.g., "Introduction to Macroeconomics") |
| Slug | A URL-friendly version. Hit the 'Regenerate' button after filling out the Header field. |
| ShowHeader boolean | Indicates whether the header should be displayed. |
| Text Content | The main body of text, images, videos, or other multimedia within the chunk, formatted as HTML. |

### When should the normal chunk be used?
Normal chunks are used for standard content sections that require keyphrase extraction and constructed responses.

### When should the "plain chunk" be used?
Plain chunks are different from normal chunks because they do not have keyphrases extracted or constructed responses. A chunk with minimal text in paragraph form should be added as a Plain-Chunk.

Use plain chunks for content like abstracts and references in research papers or content where sections are too short for quality keyphrases and constructed responses. Examples:
- Learning Objectives
- Introductions
- Abstracts
- References
- Content with only tables

### When should the video chunk be used?
Video chunks are used for content that includes a single YouTube video and requires associated learning activities. Use this for tutorial videos or lectures with accompanying questions and activities.

For example, if the page being worked on includes or is accompanied by a Youtube video that expands on the concepts mentioned in the previous chunk, authors should create a separate video chunk to include the video.

### How to add content into chunks
- Add the text
- Adjust formatting (capitalization, bold, italics, underline) as needed
- Add tables with appropriate captions
- Add images with appropriate alt text, but use a placeholder url

## Special Formatting Options

iTELL includes several custom components that can be used to offset or emphasize content within a chunk. Each iTELL volume may use these elements slightly differently, but make sure they are used consistently within a volume.

## Which Content Should We Exclude

iTELL automatically generates learning activities with automated assessments. These include constructed response items and an end-of-page summary writing activity. However, some texts may include reflection questions, end-of-chapter summaries, and other activities. These should generally be excluded when adapting source material for iTELL to avoid redundancy. Examples of common elements that should be excluded are "Summary," "Key Takeaway," and "Review Questions". Questions in the form of math or coding exercises, however, should and are encouraged to be included in the page.

- Exclude chunks that might contain summary of the text.
- Exclude chunks that have review questions which have the same functions as iTELL's Question and Reference Answer pair.

## Headers

- **Hierarchy and Structure**: Maintain a clear hierarchical structure with distinct levels of headers. Use H3 for subheaders inside Chunks.
- **Uniform Formatting**: Use consistent capitalization and numbering across all headers.
- **Capitalization**: Use Title Case for all headers. Example: '1. Introduction to Macroeconomics'.
- **Logical Sequence**: Ensure that the headers follow a logical sequence and accurately reflect the content hierarchy.

## Frequently Asked Questions

**What should I do if the source material does not include a header?**

Read the content and write a header yourself that matches the content as well as the style and tone of other headers in the text.