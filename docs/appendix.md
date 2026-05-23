# APPENDIX

This appendix collects supporting material and references. Place each item below under the appendix when generating a table of contents.

A. Plagiarism Report

- Status: (placeholder) — add your plagiarism scan/report PDF or text here. Filename suggestion: `docs/appendix/plagiarism_report.pdf` or `docs/appendix/plagiarism_report.md`.

B. Publications / Patents

- Status: (placeholder) — add published papers, patent references, or links. Suggested path: `docs/appendix/publications.md`.

C. Certificates / Awards

- Status: (placeholder) — add scanned certificates or award listings. Suggested path: `docs/appendix/certificates.md`.

D. Routine Calculations and Supporting Material

- `A.1 Standard Calculations` — include calculation spreadsheets or derivations in `docs/appendix/standard_calculations.md`.
- `A.2 Standard Data and Tables` — include CSVs/tables under `docs/appendix/data/`.

E. Additional Resources (Project docs consolidated)

- Installation and Setup Guide — [docs/installation_setup_guide.md](installation_setup_guide.md)
- User Manual — [docs/user_manual.md](user_manual.md)
- Developer Guide — [docs/developer_guide.md](developer_guide.md)
- Configuration Files — [docs/configuration_files.md](configuration_files.md)

F. Certificates and Awards (mirrored)

- If you want the certificates and awards listed separately, add them under `docs/appendix/certificates.md` and link here.

Notes on TOC and Page Numbers

- Markdown itself does not control page numbers; page numbering comes from your document generator (Pandoc, LaTeX, Word). When generating a printable/numbered PDF, ensure `docs/appendix.md` is included in the build and placed after the main chapters so the generator assigns the Appendix a dedicated page range.
- Suggested Pandoc (example) to produce PDF with appendix appended:

```powershell
pandoc --toc -o output.pdf \
  README.md \
  docs/installation_setup_guide.md \
  docs/user_manual.md \
  docs/developer_guide.md \
  docs/configuration_files.md \
  docs/appendix.md
```

That will include the appendix entries in the generated table of contents; adjust order to match desired page numbers.

If you want, I can:

- create placeholder files under `docs/appendix/` for each Appendix item, or
- update your existing TOC build script so the Appendix appears as a single top-level entry with sub-entries A, B, C.

Tell me which you prefer and I will proceed.