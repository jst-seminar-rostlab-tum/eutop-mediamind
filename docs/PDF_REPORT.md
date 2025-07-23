
# MediaMind PDF Report Flow

## How it Works

1. **ReportService triggers PDF creation**
   - When a report is needed, `ReportService` calls `PDFService.create_pdf` with the search profile, timeslot, and language.

2. **PDFService generates the PDF**
   - Uses the **ReportLab** library to draw the PDF as a canvas.
   - Content is split into sections:
     - **Cover page** (`_draw_cover_elements`): Title, date, and intro.
     - **Summaries** (`_create_summaries_elements`): Multi-column article summaries with links.
     - **Full articles** (`_create_full_articles_elements`): Full text, single-column.
     - **Originals** (`_create_original_elements`): Appendix with original articles.
   - Anchor flowables are used for internal links (e.g., table of contents).
   - All PDF metadata is cleaned for privacy.

3. **PDF is uploaded to AWS S3**
   - The PDF is stored at a path based on environment, search profile, and report ID.
   - A presigned S3 link is generated, valid for 7 days (for privacy).

## Main Components

- **PDFService.create_pdf**: Main entry point. Collects articles, translates, and assembles the PDF.
- **PDFService._PDFService__draw_cover_elements**: Draws the cover page (branding, title, date).
- **PDFService._PDFService__create_summaries_elements**: Builds the summary section (multi-column, with links).
- **PDFService._PDFService__create_full_articles_elements**: Renders the full articles (single-column, readable).
- **PDFService._PDFService__create_original_elements**: Adds the appendix with original articles.
- **Anchor Flowables**: Used for clickable navigation inside the PDF.
- **S3 Upload Logic**: Handles secure, temporary storage and presigned link generation.

## Language Localization

- Each report is generated in the language chosen by the user/search profile.
- Article content, titles, summaries, and metadata are selected in the requested language.
- At the end of the PDF, the original news articles are included in their original language for reference.

## Custom Fonts and Styles

- The PDF uses the Inter font family, which supports a wide range of language symbols (e.g., German, Turkish, etc.).
- All font variants (Regular, Bold, Oblique, etc.) are stored in the `fonts` folder and registered at runtime.
- Changing the font for the entire PDF is simple—just update the font files; all styles reference these font variables for consistent branding and readability.

## Privacy

- **Efficient Delivery**: PDFs are uploaded to S3 instead of being sent as email attachments, so large files don't consume users' email data plans.
- **Temporary Access**: S3 links expire after 7 days, so PDFs can't be accessed indefinitely. After expiration, a new S3 link can be generated via MediaMind, or users can view the report and news directly in the MediaMind dashboard.
- **Metadata Cleaning**: All identifying metadata is stripped from the PDF before upload.

<div align="center">

### [View example PDF report](example_report_pdf)

</div>

## Summary

The PDF service creates privacy-friendly, well-structured reports using ReportLab, and makes them available for a short time via S3. All navigation and layout is handled in modular components for easy maintenance and branding.

