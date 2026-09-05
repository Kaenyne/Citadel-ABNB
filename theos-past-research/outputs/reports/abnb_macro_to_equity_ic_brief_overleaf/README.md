# Overleaf upload instructions

1. In Overleaf, choose **New Project > Upload Project** and upload the provided
   ZIP file.
2. Confirm that `main.tex` is the project's main document.
3. Use pdfLaTeX and click **Recompile**.

Do not paste `main.tex` below an existing `\\begin{document}`. The file is a
complete standalone document: `\\documentclass`, every package import, and all
definitions must remain before its own `\\begin{document}`.

The five required project-root files are:

- `main.tex`
- `metrics.tex`
- `correlation_contrast.pdf`
- `guidance_vs_stock_performance.pdf`
- `event_excess_returns.pdf`
