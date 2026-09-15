const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const Fa = require("react-icons/fa");

// ---------- palette ----------
const NAVY = "1E2761";
const NAVY_DARK = "0B0E24";
const ICE = "CADCFC";
const CARD_BG = "EEF3FC";
const CODE_BG = "11162E";
const R_COLOR = "2C7FB0";
const SQL_COLOR = "E8912D";
const TEXT_DARK = "232946";
const MUTED = "5B6480";
const WHITE = "FFFFFF";
const GOOD = "1E8F6B";
const WARN = "C4472B";

const TITLE_FONT = "Cambria";
const BODY_FONT = "Calibri";
const CODE_FONT = "Courier New";

const shadow = () => ({ type: "outer", color: "0B0E24", opacity: 0.22, blur: 7, offset: 2, angle: 90 });

async function iconPng(name, px = 256) {
  const Icon = Fa[name];
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Icon, { size: px, color: "#FFFFFF" }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

// Charts are rasterized from hand-built SVG rather than pptxgenjs native charts:
// native OOXML charts render unreliably in Keynote (blank/missing), even when
// they validate and render fine in PowerPoint/LibreOffice. A rasterized image
// is guaranteed identical everywhere.
async function svgPng(svg, wIn, hIn) {
  const buf = await sharp(Buffer.from(svg), { density: 220 }).resize(Math.round(wIn * 220), Math.round(hIn * 220)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

function buildResidualSvg(fitted, resid) {
  const W = 1120, H = 700, x0 = 78, x1 = 1100, y0 = 16, y1 = 640;
  const xMin = 500, xMax = 3500, yMin = -300, yMax = 300;
  const mapX = (v) => x0 + ((v - xMin) / (xMax - xMin)) * (x1 - x0);
  const mapY = (v) => y1 - ((v - yMin) / (yMax - yMin)) * (y1 - y0);
  const yTicks = [-300, -200, -100, 0, 100, 200, 300];
  const xTicks = [500, 1000, 1500, 2000, 2500, 3000, 3500];
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="Calibri,Arial,sans-serif">`;
  s += `<rect x="0" y="0" width="${W}" height="${H}" fill="none"/>`;
  for (const t of yTicks) {
    const y = mapY(t);
    s += `<line x1="${x0}" y1="${y}" x2="${x1}" y2="${y}" stroke="#DCE3F2" stroke-width="1.5"/>`;
    s += `<text x="${x0 - 10}" y="${y + 5}" font-size="17" fill="#5B6480" text-anchor="end">${t}</text>`;
  }
  for (const t of xTicks) {
    const x = mapX(t);
    s += `<text x="${x}" y="${y1 + 26}" font-size="16" fill="#5B6480" text-anchor="middle">${t}</text>`;
  }
  s += `<line x1="${mapX(xMin)}" y1="${mapY(0)}" x2="${mapX(xMax)}" y2="${mapY(0)}" stroke="#C4472B" stroke-width="2.5" stroke-dasharray="9,6"/>`;
  for (let i = 0; i < fitted.length; i++) {
    s += `<circle cx="${mapX(fitted[i])}" cy="${mapY(resid[i])}" r="7" fill="#1E2761"/>`;
  }
  s += `<text x="${(x0 + x1) / 2}" y="${H - 8}" font-size="17" fill="#232946" text-anchor="middle">Fitted revenue</text>`;
  s += `<text x="22" y="${(y0 + y1) / 2}" font-size="17" fill="#232946" text-anchor="middle" transform="rotate(-90 22 ${(y0 + y1) / 2})">Residual</text>`;
  s += `</svg>`;
  return s;
}

function buildRocSvg(fpr, tprModel) {
  const W = 1120, H = 870, x0 = 78, x1 = 1100, y0 = 24, y1 = 760;
  const mapX = (v) => x0 + v * (x1 - x0);
  const mapY = (v) => y1 - v * (y1 - y0);
  const ticks = [0, 0.2, 0.4, 0.6, 0.8, 1.0];
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="Calibri,Arial,sans-serif">`;
  for (const t of ticks) {
    const y = mapY(t), x = mapX(t);
    s += `<line x1="${x0}" y1="${y}" x2="${x1}" y2="${y}" stroke="#DCE3F2" stroke-width="1.5"/>`;
    s += `<text x="${x0 - 10}" y="${y + 6}" font-size="18" fill="#5B6480" text-anchor="end">${t}</text>`;
    s += `<text x="${x}" y="${y1 + 30}" font-size="18" fill="#5B6480" text-anchor="middle">${t}</text>`;
  }
  s += `<line x1="${mapX(0)}" y1="${mapY(0)}" x2="${mapX(1)}" y2="${mapY(1)}" stroke="#C7CCDE" stroke-width="3"/>`;
  const pts = fpr.map((v, i) => `${mapX(v)},${mapY(tprModel[i])}`).join(" ");
  s += `<polyline points="${pts}" fill="none" stroke="#2C7FB0" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>`;
  s += `<text x="${(x0 + x1) / 2}" y="${H - 44}" font-size="19" fill="#232946" text-anchor="middle">False Positive Rate</text>`;
  s += `<text x="24" y="${(y0 + y1) / 2}" font-size="19" fill="#232946" text-anchor="middle" transform="rotate(-90 24 ${(y0 + y1) / 2})">True Positive Rate</text>`;
  const legY = H - 12;
  s += `<line x1="${W / 2 - 220}" y1="${legY - 6}" x2="${W / 2 - 170}" y2="${legY - 6}" stroke="#2C7FB0" stroke-width="5"/>`;
  s += `<text x="${W / 2 - 160}" y="${legY}" font-size="17" fill="#232946">Model (AUC 0.77)</text>`;
  s += `<line x1="${W / 2 + 40}" y1="${legY - 6}" x2="${W / 2 + 90}" y2="${legY - 6}" stroke="#C7CCDE" stroke-width="5"/>`;
  s += `<text x="${W / 2 + 100}" y="${legY}" font-size="17" fill="#232946">Random</text>`;
  s += `</svg>`;
  return s;
}

function buildElbowSvg(ks, wcss) {
  const W = 1120, H = 720, x0 = 78, x1 = 1090, y0 = 40, y1 = 660;
  const vMax = 450;
  const mapX = (i) => x0 + ((i + 0.5) / ks.length) * (x1 - x0);
  const mapY = (v) => y1 - (v / vMax) * (y1 - y0);
  const yTicks = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450];
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="Calibri,Arial,sans-serif">`;
  for (const t of yTicks) {
    const y = mapY(t);
    s += `<line x1="${x0}" y1="${y}" x2="${x1}" y2="${y}" stroke="#DCE3F2" stroke-width="1.5"/>`;
    s += `<text x="${x0 - 10}" y="${y + 5}" font-size="16" fill="#5B6480" text-anchor="end">${t}</text>`;
  }
  ks.forEach((k, i) => {
    s += `<text x="${mapX(i)}" y="${y1 + 30}" font-size="17" fill="#5B6480" text-anchor="middle">k=${k}</text>`;
  });
  const pts = wcss.map((v, i) => `${mapX(i)},${mapY(v)}`).join(" ");
  s += `<polyline points="${pts}" fill="none" stroke="#1E2761" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>`;
  wcss.forEach((v, i) => {
    s += `<circle cx="${mapX(i)}" cy="${mapY(v)}" r="9" fill="#1E2761"/>`;
    s += `<text x="${mapX(i)}" y="${mapY(v) - 20}" font-size="18" font-weight="bold" fill="#1E2761" text-anchor="middle">${v}</text>`;
  });
  s += `</svg>`;
  return s;
}

async function main() {
  const iconNames = [
    "FaProjectDiagram", "FaDatabase", "FaChartLine", "FaLayerGroup",
    "FaCheckCircle", "FaShieldAlt", "FaBalanceScale", "FaClipboardCheck",
    "FaExclamationTriangle", "FaBullseye", "FaCode", "FaRulerCombined",
  ];
  const icons = {};
  for (const n of iconNames) icons[n] = await iconPng(n);

  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
  pres.author = "BDA Program of Practice";
  pres.company = "BDA POP";
  pres.title = "Validating Big Data Models at Scale";

  function badge(slide, cx, cy, d, iconKey, bg) {
    slide.addShape("ellipse", { x: cx - d / 2, y: cy - d / 2, w: d, h: d, fill: { color: bg }, line: { type: "none" }, shadow: shadow() });
    const id = d * 0.52;
    slide.addImage({ data: icons[iconKey], x: cx - id / 2, y: cy - id / 2, w: id, h: id });
  }

  function header(slide, eyebrow, title, dark) {
    slide.addText(eyebrow.toUpperCase(), {
      x: 0.6, y: 0.38, w: 10, h: 0.3, fontFace: BODY_FONT, fontSize: 12, bold: true,
      color: dark ? ICE : SQL_COLOR, charSpacing: 2,
    });
    slide.addText(title, {
      x: 0.6, y: 0.66, w: 12.1, h: 0.72, fontFace: TITLE_FONT, fontSize: 32, bold: true,
      color: dark ? WHITE : NAVY,
    });
  }

  function footer(slide, n, dark) {
    slide.addText("BDA POP — Hybrid Model Validation (R + SQL)", {
      x: 0.6, y: 7.14, w: 8, h: 0.28, fontFace: BODY_FONT, fontSize: 9,
      color: dark ? "6B75A0" : "9AA3BF",
    });
    slide.addText(`${n} / 10`, {
      x: 12.0, y: 7.14, w: 0.73, h: 0.28, fontFace: BODY_FONT, fontSize: 9,
      color: dark ? "6B75A0" : "9AA3BF", align: "right",
    });
  }

  function iconRow(slide, x, y, w, iconKey, bg, title, desc) {
    badge(slide, x + 0.34, y + 0.34, 0.68, iconKey, bg);
    slide.addText(title, { x: x + 0.82, y: y - 0.02, w: w - 0.82, h: 0.32, fontFace: BODY_FONT, bold: true, fontSize: 14.5, color: NAVY });
    slide.addText(desc, { x: x + 0.82, y: y + 0.29, w: w - 0.82, h: 0.42, fontFace: BODY_FONT, fontSize: 12, color: MUTED, valign: "top" });
  }

  function card(slide, x, y, w, h, fill) {
    slide.addShape("roundRect", { x, y, w, h, rectRadius: 0.09, fill: { color: fill || CARD_BG }, line: { type: "none" }, shadow: shadow() });
  }

  function codeBox(slide, x, y, w, h, code, engine) {
    slide.addShape("roundRect", { x, y, w, h, rectRadius: 0.09, fill: { color: CODE_BG }, line: { type: "none" }, shadow: shadow() });
    const tabColor = engine === "SQL" ? SQL_COLOR : R_COLOR;
    slide.addShape("roundRect", { x: x + 0.3, y: y - 0.19, w: 0.95, h: 0.38, rectRadius: 0.19, fill: { color: tabColor }, line: { type: "none" } });
    slide.addText(engine, { x: x + 0.3, y: y - 0.19, w: 0.95, h: 0.38, align: "center", valign: "middle", bold: true, color: WHITE, fontSize: 12.5, fontFace: BODY_FONT });
    slide.addText(code, { x: x + 0.35, y: y + 0.35, w: w - 0.7, h: h - 0.55, fontFace: CODE_FONT, fontSize: 12, color: "E8ECF7", valign: "top", lineSpacingMultiple: 1.22, paraSpaceBefore: 0, paraSpaceAfter: 0 });
  }

  function metricPill(slide, x, y, w, label, value, threshold, ok) {
    slide.addShape("roundRect", { x, y, w, h: 0.9, rectRadius: 0.08, fill: { color: CARD_BG }, line: { type: "none" }, shadow: shadow() });
    slide.addText(label, { x: x + 0.2, y: y + 0.08, w: w - 0.4, h: 0.28, fontFace: BODY_FONT, fontSize: 11.5, bold: true, color: MUTED });
    slide.addText(value, { x: x + 0.2, y: y + 0.32, w: w * 0.55, h: 0.5, fontFace: TITLE_FONT, fontSize: 24, bold: true, color: NAVY });
    slide.addText(threshold, { x: x + w * 0.55, y: y + 0.42, w: w * 0.43, h: 0.4, fontFace: BODY_FONT, fontSize: 10.5, color: ok ? GOOD : WARN, align: "right", valign: "bottom", bold: true });
  }

  // ============================================================ SLIDE 1
  {
    const s = pres.addSlide();
    s.background = { color: NAVY_DARK };
    s.addText("BIG DATA ANALYTICS — PROGRAM OF PRACTICE", { x: 0.9, y: 0.9, w: 8, h: 0.35, fontFace: BODY_FONT, fontSize: 12, bold: true, color: ICE, charSpacing: 2 });
    s.addText("Validating Big Data Models at Scale", { x: 0.9, y: 2.6, w: 11.5, h: 1.5, fontFace: TITLE_FONT, fontSize: 44, bold: true, color: WHITE });
    s.addText("A hybrid diagnostic framework — R for statistical rigor, SQL for in-database scale", {
      x: 0.9, y: 3.95, w: 10.5, h: 0.6, fontFace: BODY_FONT, fontSize: 18, color: ICE,
    });
    badge(s, 10.9, 1.35, 1.05, "FaChartLine", R_COLOR);
    badge(s, 11.75, 1.9, 1.05, "FaDatabase", SQL_COLOR);
    s.addShape("line", { x: 11.3, y: 1.55, w: 0.55, h: 0.55, line: { color: ICE, width: 1.5, dashType: "sysDot" } });
    s.addText("Regression  ·  Classification  ·  Clustering", { x: 0.9, y: 6.6, w: 8, h: 0.35, fontFace: BODY_FONT, fontSize: 13, italic: true, color: "8B95C4" });
    footer(s, 1, true);
    s.addNotes("This session is about one idea: validation isn't optional at big-data scale, and it doesn't have to live in one tool. We diagnose in R because that's where the statistical depth lives, then push the scoring step into SQL because that's where the row counts live. By the end of this deck you'll have a repeatable pattern for regression, classification, and clustering diagnostics that works whether you're validating on a laptop or a live warehouse table.");
  }

  // ============================================================ SLIDE 2
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    header(s, "Executive Summary", "The Hybrid Architecture: R + SQL");
    iconRow(s, 0.6, 1.85, 5.7, "FaChartLine", R_COLOR, "R diagnoses", "Residuals, ROC curves, silhouette — the statistical depth SQL can't express.");
    iconRow(s, 0.6, 2.95, 5.7, "FaDatabase", SQL_COLOR, "SQL scales", "Window functions and aggregates score millions of rows in place.");
    iconRow(s, 0.6, 4.05, 5.7, "FaCheckCircle", NAVY, "One protocol", "Fit, score, evaluate against a threshold — every model, either engine.");

    // architecture diagram
    card(s, 6.75, 1.85, 5.95, 4.7, CARD_BG);
    s.addText("MODEL VALIDATION PIPELINE", { x: 6.95, y: 2.0, w: 5.55, h: 0.3, fontFace: BODY_FONT, fontSize: 10.5, bold: true, color: MUTED, charSpacing: 1.5 });
    s.addShape("roundRect", { x: 7.0, y: 2.5, w: 2.3, h: 1.5, rectRadius: 0.1, fill: { color: NAVY }, line: { type: "none" }, shadow: shadow() });
    badge(s, 8.15, 2.85, 0.6, "FaChartLine", R_COLOR);
    s.addText("R — Diagnose", { x: 7.0, y: 3.25, w: 2.3, h: 0.3, align: "center", bold: true, color: WHITE, fontSize: 12.5, fontFace: BODY_FONT });
    s.addText("Fit · Residuals · ROC", { x: 7.0, y: 3.55, w: 2.3, h: 0.35, align: "center", color: ICE, fontSize: 9.5, fontFace: BODY_FONT });

    s.addShape("roundRect", { x: 10.15, y: 2.5, w: 2.3, h: 1.5, rectRadius: 0.1, fill: { color: NAVY }, line: { type: "none" }, shadow: shadow() });
    badge(s, 11.3, 2.85, 0.6, "FaDatabase", SQL_COLOR);
    s.addText("SQL — Score", { x: 10.15, y: 3.25, w: 2.3, h: 0.3, align: "center", bold: true, color: WHITE, fontSize: 12.5, fontFace: BODY_FONT });
    s.addText("Window fns · Aggregates", { x: 10.15, y: 3.55, w: 2.3, h: 0.35, align: "center", color: ICE, fontSize: 9.5, fontFace: BODY_FONT });

    s.addShape("line", { x: 9.3, y: 3.25, w: 0.85, h: 0, line: { color: NAVY, width: 2, endArrowType: "triangle", beginArrowType: "triangle" } });
    s.addText("coefficients / centroids move — not the data", { x: 7.0, y: 4.25, w: 5.5, h: 0.3, align: "center", italic: true, color: MUTED, fontSize: 10.5, fontFace: BODY_FONT });

    s.addShape("roundRect", { x: 7.0, y: 4.85, w: 5.45, h: 1.5, rectRadius: 0.1, fill: { color: WHITE }, line: { color: ICE, width: 1 } });
    s.addText([
      { text: "Rule of thumb:  ", options: { bold: true, color: NAVY } },
      { text: "prototype and diagnose on a sample in R; once the metric and threshold are set, run the evaluate step as a query against the full table.", options: { color: TEXT_DARK } },
    ], { x: 7.2, y: 5.0, w: 5.05, h: 1.2, fontFace: BODY_FONT, fontSize: 11.5, valign: "top", lineSpacingMultiple: 1.15 });
    footer(s, 2, false);
    s.addNotes("This is the mental model for the whole deck: R and SQL aren't competing tools, they're two stages of the same pipeline. You diagnose where the statistical libraries live, then you deploy the scoring logic to where the data already sits, so you never pull a billion-row table into memory just to compute an average.");
  }

  // ============================================================ SLIDE 3
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    header(s, "Linear Regression", "Diagnostic Framework & Key Metrics");
    iconRow(s, 0.6, 1.85, 5.7, "FaRulerCombined", NAVY, "R² and Adjusted R²", "Share of variance the model actually explains.");
    iconRow(s, 0.6, 2.95, 5.7, "FaChartLine", NAVY, "RMSE", "Typical error, in the same units as the target.");
    iconRow(s, 0.6, 4.05, 5.7, "FaCheckCircle", NAVY, "Residual plot", "No funnel, no curve — errors scatter randomly around zero.");
    metricPill(s, 0.6, 5.35, 2.75, "HOLDOUT R²", "0.84", "≥ 0.60", true);
    metricPill(s, 3.55, 5.35, 2.75, "HOLDOUT RMSE", "17%", "≤ 20% mean", true);

    card(s, 6.75, 1.85, 5.95, 5.25, CARD_BG);
    s.addText("RESIDUALS vs. FITTED VALUES", { x: 6.95, y: 2.0, w: 5.55, h: 0.3, fontFace: BODY_FONT, fontSize: 10.5, bold: true, color: MUTED, charSpacing: 1.5 });
    const fitted = [820, 910, 1040, 1120, 1205, 1260, 1340, 1410, 1480, 1560, 1610, 1690, 1750, 1820, 1900, 1965, 2040, 2110, 2180, 2260, 2330, 2410, 2480, 2560, 2630, 2710, 2790, 2860, 2940, 3020];
    const resid = [-180, 140, -90, 210, -60, 30, -220, 160, 90, -140, 200, -40, 110, -170, 60, -230, 150, -20, 180, -110, 40, -190, 120, -70, 210, -150, 30, -100, 170, -60];
    s.addImage({ data: await svgPng(buildResidualSvg(fitted, resid), 5.6, 3.5), x: 6.9, y: 2.35, w: 5.6, h: 3.5 });
    s.addText("No pattern in the scatter = model isn't missing a trend", { x: 6.95, y: 6.05, w: 5.55, h: 0.4, italic: true, color: MUTED, fontSize: 10.5, fontFace: BODY_FONT });
    footer(s, 3, false);
    s.addNotes("R² tells you the headline story, but it can't tell you whether the model is systematically wrong somewhere specific — only the residual plot can. Here the scatter is flat and random around zero across the whole range, which is exactly what a well-specified model looks like. A curved or funnel-shaped residual plot would be the red flag, even with a great R².");
  }

  // ============================================================ SLIDE 4
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    header(s, "Linear Regression", "In-Database SQL Scaling");
    iconRow(s, 0.6, 1.95, 5.7, "FaDatabase", SQL_COLOR, "Score in place", "Predictions land in the warehouse, not in R's memory.");
    iconRow(s, 0.6, 3.05, 5.7, "FaCode", SQL_COLOR, "Window functions", "AVG() OVER() computes the mean without a second pass.");
    iconRow(s, 0.6, 4.15, 5.7, "FaCheckCircle", SQL_COLOR, "One query, full table", "R² and RMSE recomputed on every row, on a schedule.");
    card(s, 0.6, 5.35, 5.95, 1.35, CARD_BG);
    s.addText([
      { text: "Why this matters:  ", options: { bold: true, color: NAVY } },
      { text: "the R model only supplies coefficients — scoring millions of restaurants never has to leave the database.", options: { color: TEXT_DARK } },
    ], { x: 0.85, y: 5.5, w: 5.5, h: 1.05, fontFace: BODY_FONT, fontSize: 12, valign: "top", lineSpacingMultiple: 1.2 });

    codeBox(s, 6.85, 2.0, 5.85, 5.1,
`WITH scored AS (
  SELECT
    actual_revenue,
    predicted_revenue,
    actual_revenue - predicted_revenue
      AS residual,
    AVG(actual_revenue) OVER ()
      AS mean_actual
  FROM model_scores
)
SELECT
  1 - SUM(POWER(residual, 2))
    / SUM(POWER(actual_revenue
        - mean_actual, 2))   AS r_squared,
  SQRT(AVG(POWER(residual, 2)))
                              AS rmse
FROM scored;`, "SQL");
    footer(s, 4, false);
    s.addNotes("This is the exact same R² and RMSE definition from the last slide, just expressed as one aggregate query. The window function computes the grand mean in the same pass as everything else, so the whole evaluate step is a single scan of the table — no row-by-row loop, no pulling data out to R.");
  }

  // ============================================================ SLIDE 5
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    header(s, "Classification", "Diagnostic Framework & Confusion Matrices");
    iconRow(s, 0.6, 1.85, 5.7, "FaBullseye", NAVY, "Precision", "Of the positive calls, how many were right.");
    iconRow(s, 0.6, 2.95, 5.7, "FaCheckCircle", NAVY, "Recall", "Of the true positives, how many got caught.");
    iconRow(s, 0.6, 4.05, 5.7, "FaBalanceScale", NAVY, "F1 score", "Harmonic mean — punishes a weak side, either side.");
    card(s, 0.6, 5.15, 5.95, 1.55, CARD_BG);
    s.addText([
      { text: "Precision  86.6%   ", options: { bold: true, color: NAVY, fontSize: 15 } },
      { text: "·  ", options: { color: MUTED } },
      { text: "Recall  76.5%   ", options: { bold: true, color: NAVY, fontSize: 15 } },
      { text: "·  ", options: { color: MUTED } },
      { text: "F1  81.2%", options: { bold: true, color: NAVY, fontSize: 15 } },
    ], { x: 0.85, y: 5.35, w: 5.5, h: 0.4, fontFace: BODY_FONT });
    s.addText("Accuracy alone (86%) looked fine — the matrix is what caught the recall gap.", { x: 0.85, y: 5.75, w: 5.5, h: 0.75, italic: true, color: MUTED, fontSize: 11.5, fontFace: BODY_FONT, valign: "top" });

    card(s, 6.75, 1.85, 5.95, 4.9, CARD_BG);
    s.addText("HOLDOUT CONFUSION MATRIX  (n = 2,000)", { x: 6.95, y: 2.0, w: 5.55, h: 0.3, fontFace: BODY_FONT, fontSize: 10.5, bold: true, color: MUTED, charSpacing: 1.5 });
    const cellOpt = (fill, val, lbl) => ([{ text: val + "\n", options: { bold: true, fontSize: 22, color: NAVY, breakLine: true } }, { text: lbl, options: { fontSize: 10.5, color: MUTED } }]);
    s.addTable([
      [
        { text: "", options: { fill: { color: WHITE } } },
        { text: "Predicted:\nPositive", options: { fill: { color: NAVY }, color: WHITE, bold: true, align: "center", fontSize: 11 } },
        { text: "Predicted:\nNegative", options: { fill: { color: NAVY }, color: WHITE, bold: true, align: "center", fontSize: 11 } },
      ],
      [
        { text: "Actual:\nPositive", options: { fill: { color: NAVY }, color: WHITE, bold: true, align: "center", fontSize: 11 } },
        { text: cellOpt("E5F3EE", "612", "True Positive"), options: { fill: { color: "E5F3EE" }, align: "center", valign: "middle" } },
        { text: cellOpt("FBEAE6", "188", "False Negative"), options: { fill: { color: "FBEAE6" }, align: "center", valign: "middle" } },
      ],
      [
        { text: "Actual:\nNegative", options: { fill: { color: NAVY }, color: WHITE, bold: true, align: "center", fontSize: 11 } },
        { text: cellOpt("FBEAE6", "95", "False Positive"), options: { fill: { color: "FBEAE6" }, align: "center", valign: "middle" } },
        { text: cellOpt("E5F3EE", "1,105", "True Negative"), options: { fill: { color: "E5F3EE" }, align: "center", valign: "middle" } },
      ],
    ], { x: 6.95, y: 2.45, w: 5.55, h: 4.1, colW: [1.35, 2.1, 2.1], rowH: [0.6, 1.75, 1.75], fontFace: BODY_FONT, border: { type: "solid", color: WHITE, pt: 2 } });
    footer(s, 5, false);
    s.addNotes("Accuracy and AUC both look healthy on their own, and that's exactly the trap a headline metric sets. The matrix breaks the same result into four numbers, and here the false-negative cell is the one that matters most — it tells you which real cases the model is quietly missing, something no single summary number can show you.");
  }

  // ============================================================ SLIDE 6
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    header(s, "Classification", "Advanced Evaluation & R ROC Curves");
    iconRow(s, 0.6, 1.95, 5.7, "FaChartLine", R_COLOR, "AUC", "Separability across every possible cutoff, not just one.");
    iconRow(s, 0.6, 3.05, 5.7, "FaBullseye", R_COLOR, "TPR vs. FPR", "Plotted at each threshold to trace the ROC curve.");
    iconRow(s, 0.6, 4.15, 5.7, "FaCheckCircle", R_COLOR, "Above the diagonal", "Distance from the diagonal is real signal.");
    codeBox(s, 0.6, 5.35, 5.95, 1.75,
`roc_obj <- roc(holdout$actual,
               holdout$pred_prob)
plot(roc_obj, print.auc = TRUE,
     col = "#2C7FB0", lwd = 2)`, "R");

    card(s, 6.75, 1.85, 5.95, 5.25, CARD_BG);
    s.addText("ROC CURVE — HOLDOUT SET", { x: 6.95, y: 2.0, w: 5.55, h: 0.3, fontFace: BODY_FONT, fontSize: 10.5, bold: true, color: MUTED, charSpacing: 1.5 });
    const fpr = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0];
    const tprModel = [0, 0.18, 0.32, 0.44, 0.53, 0.6, 0.66, 0.71, 0.75, 0.79, 0.82, 0.85, 0.87, 0.89, 0.91, 0.93, 0.94, 0.96, 0.97, 0.99, 1.0];
    s.addImage({ data: await svgPng(buildRocSvg(fpr, tprModel), 5.6, 4.35), x: 6.9, y: 2.35, w: 5.6, h: 4.35 });
    footer(s, 6, false);
    s.addNotes("The curve bows well above the diagonal, which is the visual version of an AUC comfortably above 0.5 — a random classifier would trace that dashed diagonal line exactly. This is the same holdout set from the confusion matrix slide; AUC and the matrix are two independent checks on the same model, and both need to pass.");
  }

  // ============================================================ SLIDE 7
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    header(s, "Unsupervised Clustering", "Validation Framework: WCSS vs. BCSS");
    iconRow(s, 0.6, 1.85, 5.7, "FaLayerGroup", NAVY, "WCSS", "Within-cluster spread — smaller means tighter clusters.");
    iconRow(s, 0.6, 2.95, 5.7, "FaProjectDiagram", NAVY, "BCSS", "Between-cluster spread — bigger means cleaner separation.");
    iconRow(s, 0.6, 4.05, 5.7, "FaCheckCircle", NAVY, "Silhouette score", "Combines both into one −1 to 1 verdict per point.");
    metricPill(s, 0.6, 5.35, 5.7, "SILHOUETTE, BEST k (k = 3)", "0.42", "≥ 0.50 target", false);

    card(s, 6.75, 1.85, 5.95, 5.25, CARD_BG);
    s.addText("WCSS BY CLUSTER COUNT (ELBOW)", { x: 6.95, y: 2.0, w: 5.55, h: 0.3, fontFace: BODY_FONT, fontSize: 10.5, bold: true, color: MUTED, charSpacing: 1.5 });
    s.addImage({ data: await svgPng(buildElbowSvg([2, 3, 4, 5, 6], [420, 268, 178, 150, 136]), 5.6, 3.6), x: 6.9, y: 2.35, w: 5.6, h: 3.6 });
    s.addShape("roundRect", { x: 8.35, y: 5.3, w: 1.55, h: 0.4, rectRadius: 0.06, fill: { color: SQL_COLOR }, line: { type: "none" } });
    s.addText("elbow ≈ k=3", { x: 8.35, y: 5.3, w: 1.55, h: 0.4, align: "center", valign: "middle", bold: true, color: WHITE, fontSize: 11, fontFace: BODY_FONT });
    s.addText("Diminishing returns past k=3 — but silhouette says the segments still overlap.", { x: 6.95, y: 6.15, w: 5.55, h: 0.4, italic: true, color: MUTED, fontSize: 10.5, fontFace: BODY_FONT });
    footer(s, 7, false);
    s.addNotes("The elbow chart and the silhouette score are answering two different questions. The elbow says three clusters is where adding more stops paying off in tightness. Silhouette says even at three, points aren't cleanly closer to their own cluster than the next one — 0.42 against a 0.50 bar. Both checks matter before you build a plan on top of the segments.");
  }

  // ============================================================ SLIDE 8
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    header(s, "Unsupervised Clustering", "In-Database Centroid Distance");
    iconRow(s, 0.6, 1.95, 5.7, "FaDatabase", SQL_COLOR, "Centroids as a lookup", "A handful of rows — cheap to join against.");
    iconRow(s, 0.6, 3.05, 5.7, "FaCode", SQL_COLOR, "CROSS JOIN + window", "Every row compared to every centroid, ranked.");
    iconRow(s, 0.6, 4.15, 5.7, "FaCheckCircle", SQL_COLOR, "ROW_NUMBER() = 1", "Nearest centroid, and its distance, in one pass.");
    card(s, 0.6, 5.35, 5.95, 1.35, CARD_BG);
    s.addText([
      { text: "Why this matters:  ", options: { bold: true, color: NAVY } },
      { text: "WCSS for millions of rows becomes one grouped SUM() over this same result set.", options: { color: TEXT_DARK } },
    ], { x: 0.85, y: 5.5, w: 5.5, h: 1.05, fontFace: BODY_FONT, fontSize: 12, valign: "top", lineSpacingMultiple: 1.2 });

    codeBox(s, 6.85, 2.0, 5.85, 5.1,
`WITH distances AS (
  SELECT
    r.restaurant_id, c.cluster_id,
    SQRT(
      POWER(r.cost_scaled
        - c.cost_centroid, 2) +
      POWER(r.rating_scaled
        - c.rating_centroid, 2)
    ) AS dist,
    ROW_NUMBER() OVER (
      PARTITION BY r.restaurant_id
      ORDER BY dist
    ) AS rn
  FROM restaurants r
  CROSS JOIN centroids c
)
SELECT restaurant_id, cluster_id,
       dist AS wcss_contribution
FROM distances WHERE rn = 1;`, "SQL");
    footer(s, 8, false);
    s.addNotes("Centroids are tiny — three or four rows — so the cross join stays cheap even at scale; it's the row count on the restaurants side that would kill this in R's memory. ROW_NUMBER over the ranked distances picks each row's nearest centroid, and summing that distance column grouped by cluster reproduces WCSS as a single aggregate query.");
  }

  // ============================================================ SLIDE 9
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    header(s, "Architecture Guardrails", "Big Data Diagnostics Best Practices");
    const cards = [
      ["FaBalanceScale", NAVY, "Threshold governance", "Set the bar before scoring — a metric with no threshold is an opinion."],
      ["FaExclamationTriangle", WARN, "Drift monitoring", "Recompute R² and AUC on a rolling holdout, on a schedule."],
      ["FaDatabase", SQL_COLOR, "Compute placement", "Diagnose in R, score in SQL — move the model, not the data."],
      ["FaClipboardCheck", GOOD, "Reproducibility", "Version coefficients and thresholds together, same as code."],
    ];
    const gx = [0.6, 6.85], gy = [1.85, 4.35];
    let i = 0;
    for (const gyv of gy) for (const gxv of gx) {
      const [icon, col, title, desc] = cards[i++];
      card(s, gxv, gyv, 5.95, 2.25, CARD_BG);
      badge(s, gxv + 0.65, gyv + 0.6, 0.8, icon, col);
      s.addText(title, { x: gxv + 1.2, y: gyv + 0.3, w: 4.55, h: 0.4, fontFace: BODY_FONT, bold: true, fontSize: 16, color: NAVY });
      s.addText(desc, { x: gxv + 0.4, y: gyv + 1.15, w: 5.15, h: 0.9, fontFace: BODY_FONT, fontSize: 12, color: TEXT_DARK, valign: "top", lineSpacingMultiple: 1.15 });
    }
    footer(s, 9, false);
    s.addNotes("These four guardrails are what keep the hybrid pattern from drifting apart in production: agree on thresholds up front, re-check them on a schedule rather than once at launch, keep the heavy compute where the data already lives, and version the model artifact the same way you'd version code.");
  }

  // ============================================================ SLIDE 10
  {
    const s = pres.addSlide();
    s.background = { color: NAVY_DARK };
    s.addText("CONCLUSION", { x: 0.9, y: 0.7, w: 8, h: 0.35, fontFace: BODY_FONT, fontSize: 12, bold: true, color: SQL_COLOR, charSpacing: 2 });
    s.addText("Next Steps", { x: 0.9, y: 1.0, w: 10, h: 0.85, fontFace: TITLE_FONT, fontSize: 38, bold: true, color: WHITE });
    const steps = [
      "Adopt fit → score → evaluate for every model, every time",
      "Prototype diagnostics in R, then push scoring into SQL",
      "Re-run every metric on a live holdout, not once at launch",
    ];
    let y = 2.35;
    steps.forEach((t, idx) => {
      s.addShape("ellipse", { x: 0.9, y, w: 0.5, h: 0.5, fill: { color: idx === 1 ? SQL_COLOR : R_COLOR }, line: { type: "none" } });
      s.addText(String(idx + 1), { x: 0.9, y, w: 0.5, h: 0.5, align: "center", valign: "middle", bold: true, color: WHITE, fontSize: 16, fontFace: BODY_FONT });
      s.addText(t, { x: 1.65, y: y + 0.02, w: 9.5, h: 0.5, fontFace: BODY_FONT, fontSize: 16.5, color: WHITE, valign: "middle" });
      y += 0.85;
    });
    s.addText("Questions?", { x: 0.9, y: 5.6, w: 8, h: 0.9, fontFace: TITLE_FONT, fontSize: 34, bold: true, color: ICE });
    badge(s, 12.0, 6.2, 0.95, "FaCheckCircle", GOOD);
    footer(s, 10, true);
    s.addNotes("The takeaway to leave the room with: R and SQL aren't a choice you make once — they're two stages every model passes through, diagnose then deploy. Bring a model of your own next session and we'll run this exact protocol on it live. Happy to take questions now.");
  }

  await pres.writeFile({ fileName: "session6-sql-r-model-validation.pptx" });
  console.log(`Saved session6-sql-r-model-validation.pptx — ${pres.slides.length} slides`);
}

main().catch((e) => { console.error(e); process.exit(1); });
