const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

const INPUT_DIR = path.join(__dirname, '../frontend/src/images');
const OUTPUT_DIR = path.join(__dirname, '../frontend/dist/images');

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

fs.readdirSync(INPUT_DIR).forEach(file => {
  const ext = path.extname(file).toLowerCase();
  const inputPath = path.join(INPUT_DIR, file);
  const outputPath = path.join(OUTPUT_DIR, file);

  if (['.jpg', '.jpeg', '.png'].includes(ext)) {
    // Example: create both optimized JPEG and WebP
    sharp(inputPath)
      .resize({ width: 1200 }) // Remove or customize resize as needed
      .jpeg({ quality: 80 })
      .toFile(outputPath.replace(ext, '.jpg'))
      .then(() => console.log(`Optimized JPEG: ${file}`))
      .catch(err => console.error(err));

    sharp(inputPath)
      .resize({ width: 1200 })
      .webp({ quality: 80 })
      .toFile(outputPath.replace(ext, '.webp'))
      .then(() => console.log(`Optimized WebP: ${file}`))
      .catch(err => console.error(err));
  }
});