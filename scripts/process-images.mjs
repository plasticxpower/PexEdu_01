import { mkdir, readdir, stat } from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';

const ROOT = process.cwd();
console.log(`[process-images] Root directory: ${ROOT}`);

const imageTasks = [
  {
    directory: path.join(ROOT, 'public', 'assets', 'animals'),
    pattern: /\.(jpe?g|png)$/i,
    outputs: [
      { suffix: '-400w', width: 400 },
      { suffix: '-800w', width: 800 },
      { suffix: '-1200w', width: 1200 },
    ],
    formats: [
      { extension: 'webp', options: { quality: 70 } },
      { extension: 'avif', options: { quality: 45 } },
    ],
  },
  {
    directory: path.join(ROOT, 'public', 'assets', 'icons'),
    pattern: /\.(png|jpe?g)$/i,
    outputs: [
      { suffix: '-256w', width: 256 },
      { suffix: '-512w', width: 512 },
    ],
    formats: [
      { extension: 'webp', options: { quality: 80 } },
    ],
  },
];

async function ensureDir(filePath) {
  const dir = path.dirname(filePath);
  await mkdir(dir, { recursive: true });
}

async function processImage(filePath, config) {
  try {
    const fileStat = await stat(filePath);
    const baseName = path.basename(filePath, path.extname(filePath));
    const dir = path.dirname(filePath);

    const jobs = [];
    for (const output of config.outputs) {
      for (const format of config.formats) {
        const fileName = `${baseName}${output.suffix}.${format.extension}`;
        const targetPath = path.join(dir, fileName);
        jobs.push(
          writeVariant({
            source: filePath,
            targetPath,
            width: output.width,
            format: format.extension,
            options: format.options,
            sourceMtime: fileStat.mtimeMs,
          })
        );
      }
    }
    await Promise.all(jobs);
  } catch (error) {
    console.warn(`[process-images] Skipped ${filePath}: ${error.message}`);
  }
}

async function writeVariant({ source, targetPath, width, format, options, sourceMtime }) {
  try {
    const targetStat = await stat(targetPath);
    if (targetStat.mtimeMs >= sourceMtime) {
      return;
    }
  } catch {
    // Missing file – proceed with generation.
  }

  await ensureDir(targetPath);
  await sharp(source)
    .resize({ width, withoutEnlargement: true })
    .toFormat(format, options)
    .toFile(targetPath);
}

async function run() {
  for (const task of imageTasks) {
    let files = [];
    try {
      files = await readdir(task.directory);
    } catch {
      continue;
    }
    const targets = files
      .filter((file) => task.pattern.test(file))
      .map((file) => path.join(task.directory, file));
    if (targets.length === 0) {
      continue;
    }
    console.log(`[process-images] Processing ${targets.length} files in ${path.relative(ROOT, task.directory)}`);
    await Promise.all(targets.map((file) => processImage(file, task)));
  }
}

run().catch((error) => {
  console.error('[process-images] Failed to generate responsive assets:');
  console.error(error);
  process.exitCode = 1;
});
