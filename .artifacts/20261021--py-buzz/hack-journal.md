# py-buzz documentation refresh

Focused documentation pass to make the package purpose, first use, and API examples easier to understand.


## Profile and tier

- Profile: documentation
- Tier: low-risk


## Changes

- Reworked the README and user-facing guides in a conversational, lightly playful voice.
- Added matching README and docs landing-page quickstarts covering typed validation and contextual exception handling.
- Clarified feature-guide positioning and corrected examples that did not match the current API or valid Python syntax.
- Quoted extras in shell commands so they work in zsh.
- Corrected `handle_errors()` callback behavior and clarified jittered retry delays.
- Split the feature guide into individual pages, kept `features/index.md`
  as an overview, and updated navigation and links.
- Added standalone and derived-`Buzz` usage examples across the feature
  guides, clarifying exceptions where a class method is not available.
- Added `Advanced use` sections with comprehensive code examples to complex
  guides, covering meaningful options and standalone versus `Buzz` usage.
- Kept standalone examples on non-Buzz exceptions and placed each derived exception next to its Buzz-method example.
- Kept `raise_from` in its own guide while grouping retries and the other small utilities in `other_functions.md`.
- Migrated the docs build to Zensical with a dedicated docs environment and updated CI build triggers.
- Replaced the MkDocs YAML file with native `docs/zensical.toml` configuration.
- Enabled native fenced-code rendering, fixed Griffe warnings, and selected native `typing.TypeForm` on Python 3.15+.


## Verification

- `dt format markdown` completed for all edited Markdown.
- `make docs/build` succeeded with no issues or Griffe warnings.
- `make qa/full` passed: 96 tests, lint, type checks, and coverage threshold.
- `uv run --python 3.11 pytest` passed: 96 tests, confirming the backported `TypeForm` import.
