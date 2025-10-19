import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

const SOURCE_PATH = path.join(projectRoot, 'docs', 'privacy_policy.txt');
const TARGET_HTML_PATH = path.join(projectRoot, 'public', 'privacy-policy.html');
const TARGET_TXT_PATH = path.join(projectRoot, 'public', 'privacy-policy.txt');

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function buildHtml(bodyContent) {
  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>PexEdu Privacy Policy</title>
    <link rel="icon" type="image/svg+xml" href="favicon.svg" />
    <style>
      :root {
        color-scheme: light dark;
        font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background-color: #f8f4ef;
        color: #1c1c1c;
        line-height: 1.6;
      }
      @media (prefers-color-scheme: dark) {
        :root {
          background-color: #0f172a;
          color: #e2e8f0;
        }
      }
      body {
        margin: 0;
      }
      main {
        max-width: 820px;
        margin: 0 auto;
        padding: clamp(1.5rem, 4vw, 3rem) clamp(1.25rem, 4vw, 2.5rem) 4rem;
      }
      h1 {
        font-size: clamp(2rem, 3vw, 2.6rem);
        margin-bottom: clamp(1.2rem, 3vw, 1.8rem);
      }
      section + section {
        margin-top: clamp(1.25rem, 3vw, 1.85rem);
      }
      p {
        margin: 0 0 clamp(0.85rem, 2vw, 1.2rem);
      }
      a {
        color: #0ea5e9;
      }
      pre {
        white-space: pre-wrap;
        word-break: break-word;
        background: rgba(14, 165, 233, 0.08);
        border-left: 4px solid rgba(14, 165, 233, 0.35);
        padding: 1rem;
        border-radius: 12px;
      }
    </style>
  </head>
  <body>
    <main>
      <h1>PexEdu Privacy Policy</h1>
      ${bodyContent}
    </main>
  </body>
</html>
`;
}

async function main() {
  let fileContent = '';
  try {
    fileContent = await readFile(SOURCE_PATH, 'utf8');
  } catch (error) {
    console.warn(`[generate-privacy-policy] Could not read ${SOURCE_PATH}:`, error.message);
  }

  const trimmed = fileContent.trim();
  let htmlContent;

  if (trimmed.length === 0) {
    const placeholder = `<p>The privacy policy content has not been provided yet. Please contact <a href="mailto:plasticxpower@gmail.com">plasticxpower@gmail.com</a> for additional information.</p>`;
    htmlContent = buildHtml(placeholder);
  } else {
    const paragraphs = trimmed
      .split(/\r?\n\s*\r?\n/)
      .map((block) => block.trim())
      .filter((block) => block.length > 0)
      .map((block) => {
        const escaped = escapeHtml(block).replace(/\r?\n/g, '<br />');
        return `<section><p>${escaped}</p></section>`;
      })
      .join('\n');

    htmlContent = buildHtml(paragraphs);
  }

  await writeFile(TARGET_HTML_PATH, htmlContent, 'utf8');
  await writeFile(TARGET_TXT_PATH, trimmed.length > 0 ? trimmed : '', 'utf8');
  console.log(`[generate-privacy-policy] Generated ${TARGET_HTML_PATH.replace(projectRoot + path.sep, '')}`);
}

main().catch((error) => {
  console.error('[generate-privacy-policy] Failed to build privacy policy page:', error);
  process.exitCode = 1;
});
