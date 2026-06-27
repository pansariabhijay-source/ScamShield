// Rasterize the HLD SVG to a high-res PNG using sharp (from web/node_modules).
//   node scripts/svg_to_png.js
const path = require("path");
const sharp = require(path.join(__dirname, "..", "web", "node_modules", "sharp"));

const dir = path.join(__dirname, "..", "docs", "architecture");
sharp(path.join(dir, "hld.svg"), { density: 200 })
  .png()
  .toFile(path.join(dir, "hld.png"))
  .then((i) => console.log(`hld.png ${i.width}x${i.height}`))
  .catch((e) => {
    console.error("sharp failed:", e.message);
    process.exit(1);
  });
