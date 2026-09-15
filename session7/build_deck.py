"""Builds the 09/15/2026 Hadoop & MapReduce deck using the Apple-style dark
template (skills/bda-weekly-deliverables/assets/session-template-apple-style.pptx).
Per the template's agent guide: duplicate each LAYOUT slide, fill its
[BRACKETED] placeholders, never restyle. Run with: .venv/bin/python3 build_deck.py
"""
import copy
import sys

from pptx.util import Inches, Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.oxml.ns import qn
from pptx import Presentation

sys.path.insert(0, "../.claude/skills/bda-weekly-deliverables/scripts")
import pptx_helpers as h  # only for finalize_and_save's cross-platform XML fixes

TEMPLATE = "../.claude/skills/bda-weekly-deliverables/assets/session-template-apple-style.pptx"
OUT = "session7-hadoop-mapreduce.pptx"

FONT = "Helvetica Neue"
ACCENT = RGBColor(0x00, 0x71, 0xE3)
CARD = RGBColor(0x1D, 0x1D, 0x1F)
TEXT = RGBColor(0xF5, 0xF5, 0xF7)
MUTED = RGBColor(0xA1, 0xA1, 0xA6)

COVER, SECTION, STATEMENT, KEYPOINTS, TWOCOL, STAT, IMAGE, QUOTE, DIAGRAM, CODE, STEPS, CLOSING = range(12)


def duplicate(prs, layout_idx):
    """Duplicate LAYOUT slide `layout_idx` (bg + every shape) as a new slide
    appended at the end, per the template guide's 'never build from scratch' rule."""
    template = prs.slides[layout_idx]
    new_slide = prs.slides.add_slide(template.slide_layout)

    new_cSld = new_slide._element.find(qn("p:cSld"))
    src_bg = template._element.find(qn("p:cSld")).find(qn("p:bg"))
    existing_bg = new_cSld.find(qn("p:bg"))
    if existing_bg is not None:
        new_cSld.remove(existing_bg)
    if src_bg is not None:
        new_cSld.insert(0, copy.deepcopy(src_bg))

    new_spTree = new_slide.shapes._spTree
    shape_tags = (qn("p:sp"), qn("p:pic"), qn("p:graphicFrame"), qn("p:grpSp"), qn("p:cxnSp"))
    for child in [c for c in list(new_spTree) if c.tag in shape_tags]:
        new_spTree.remove(child)
    for child in template.shapes._spTree:
        if child.tag in shape_tags:
            new_spTree.append(copy.deepcopy(child))
    return new_slide


def delete_slide(prs, index):
    sldIdLst = prs.slides._sldIdLst
    sld = list(sldIdLst)[index]
    prs.part.drop_rel(sld.get(qn("r:id")))
    sldIdLst.remove(sld)


def shape_by_name(slide, name):
    return next(s for s in slide.shapes if s.name == name)


def set_para(slide, shape_name, para_idx, text):
    shape_by_name(slide, shape_name).text_frame.paragraphs[para_idx].runs[0].text = text


def set_multiline(slide, shape_name, para_idx, lines):
    """Set several physical lines starting at para_idx, cloning that paragraph's
    pPr/defRPr for each extra line -- a single run's text can't hold '\\n' as a
    real line break in OOXML, so each line needs its own <a:p>."""
    tf = shape_by_name(slide, shape_name).text_frame
    p_el = tf.paragraphs[para_idx]._p
    template_p = copy.deepcopy(p_el)
    tf.paragraphs[para_idx].runs[0].text = lines[0]
    prev = p_el
    for line in lines[1:]:
        new_p = copy.deepcopy(template_p)
        new_p.find(qn("a:r")).find(qn("a:t")).text = line
        prev.addnext(new_p)
        prev = new_p


def clear_shape(slide, shape_name):
    sh = shape_by_name(slide, shape_name)
    sh._element.getparent().remove(sh._element)


def fix_code_font(slide, shape_name):
    """The template's Code layout specifies Menlo (Mac-only) for [CODE]; swap
    to Courier New, the confirmed cross-platform monospace face (see
    pptx_helpers.add_code), so Keynote/PowerPoint/Slides all render it."""
    for p in shape_by_name(slide, shape_name).text_frame.paragraphs:
        p.font.name = "Courier New"
        for r in p.runs:
            r.font.name = "Courier New"


def diagram_box(slide, x, y, w, h, label, sublabel=None, accent=False):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = CARD
    shape.line.color.rgb = ACCENT
    shape.line.width = Pt(1.5 if accent else 0.75)
    shape.adjustments[0] = 0.12
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = label
    p.alignment = PP_ALIGN.CENTER
    p.font.size, p.font.bold, p.font.color.rgb, p.font.name = Pt(16), True, TEXT, FONT
    if sublabel:
        p2 = tf.add_paragraph()
        p2.text = sublabel
        p2.alignment = PP_ALIGN.CENTER
        p2.font.size, p2.font.color.rgb, p2.font.name = Pt(11.5), MUTED, FONT
    return shape


def diagram_arrow(slide, x, y, w, h, rotation=0):
    shape = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x, y, w, h)
    shape.rotation = rotation
    shape.fill.solid()
    shape.fill.fore_color.rgb = ACCENT
    shape.line.fill.background()
    return shape


prs = Presentation(TEMPLATE)

# 1. Cover -------------------------------------------------------------
s = duplicate(prs, COVER)
set_para(s, "TextBox 1", 0, "BDA POP · SESSION 7 · 09/15/2026")
set_para(s, "TextBox 1", 1, "Hadoop & MapReduce")
set_para(s, "TextBox 1", 2, "Distributed processing for data that doesn't fit on one machine")
set_para(s, "TextBox 2", 0, "Faizuddin Shaik  ·  September 15, 2026")

# 2. Statement: the ceiling ---------------------------------------------
s = duplicate(prs, STATEMENT)
set_para(s, "TextBox 1", 0, "Every platform hits a ceiling before it runs out of time.")
h.notes(s, "Set the stakes before any architecture: one machine has two ceilings -- how much fits "
           "in its RAM, and how fast its one CPU runs. Real platform volume hits the RAM ceiling "
           "long before the CPU one matters. That distinction drives the whole session.")

# 3. Key Points: production scale ---------------------------------------
s = duplicate(prs, KEYPOINTS)
set_para(s, "TextBox 1", 0, "This Is Production, Not a Toy")
set_para(s, "TextBox 3", 0, "—  Google indexed the web this way in 2003–04")
set_para(s, "TextBox 3", 1, "—  Facebook, Yahoo, Twitter all run Hadoop pipelines")
set_para(s, "TextBox 3", 2, "—  Word-count is the building block for search & sentiment")
h.notes(s, "Ground this before the mechanics slides -- the audience should hear 'this is the real "
           "production pattern,' not 'this is a classroom toy.'")

# 4. Section: Part 1 -----------------------------------------------------
s = duplicate(prs, SECTION)
set_para(s, "TextBox 1", 0, "PART 1")
set_para(s, "TextBox 1", 1, "MapReduce")

# 5. Steps: Map / Shuffle & Sort / Reduce --------------------------------
s = duplicate(prs, STEPS)
set_para(s, "TextBox 1", 0, "Three Phases, One Pattern")
set_para(s, "TextBox 2", 1, "Map")
set_para(s, "TextBox 2", 2, "Run the same function on each input piece, independently")
set_para(s, "TextBox 3", 1, "Shuffle & Sort")
set_para(s, "TextBox 3", 2, "Group every pair by key so all counts for one key land together")
set_para(s, "TextBox 4", 1, "Reduce")
set_para(s, "TextBox 4", 2, "Combine the grouped values into one final answer per key")
h.notes(s, "This is the conceptual core -- don't rush it. Everything in the demo maps back to these "
           "three words: map, shuffle/sort, reduce.")

# 6. Key Points: why it's safe -------------------------------------------
s = duplicate(prs, KEYPOINTS)
set_para(s, "TextBox 1", 0, "Why It's Safe to Run at Scale")
set_para(s, "TextBox 3", 0, "—  Data locality: a map task sees only its own piece")
set_para(s, "TextBox 3", 1, "—  Fault tolerance: deterministic, so failed tasks just re-run")
set_para(s, "TextBox 3", 2, "—  10 mappers, 2 crash: the other 8 finish the job")
h.notes(s, "The fault-tolerance point is the one beginners miss: it's safe to blindly re-run a task "
           "ONLY because the function is pure.")

# 7. Section: Part 2 ------------------------------------------------------
s = duplicate(prs, SECTION)
set_para(s, "TextBox 1", 0, "PART 2")
set_para(s, "TextBox 1", 1, "Hadoop's Architecture")

# 8. Diagram: HDFS ---------------------------------------------------------
s = duplicate(prs, DIAGRAM)
set_para(s, "TextBox 1", 0, "HDFS: Distributed Storage")
clear_shape(s, "TextBox 3")
diagram_box(s, Inches(4.9), Inches(2.0), Inches(3.5), Inches(1.1), "NameNode", "Metadata only — never stores file data", accent=True)
for i, (label, sub) in enumerate([
    ("DataNode A", "Block 1"), ("DataNode B", "Block 1 (copy)"), ("DataNode C", "Block 1 (copy)")
]):
    diagram_box(s, Inches(1.0 + i * 3.9), Inches(4.6), Inches(3.4), Inches(1.3), label, sub)
    diagram_arrow(s, Inches(2.4 + i * 3.9), Inches(3.35), Inches(0.6), Inches(1.0), rotation=90)
h.notes(s, "Library analogy: the NameNode is the card catalog, DataNodes are the shelves. Each "
           "block is replicated 3x across different DataNodes/racks -- a whole rack can fail and "
           "two copies still stand. A missed heartbeat triggers automatic re-replication; nobody "
           "pages a human. Honest caveat: the NameNode itself is a single point of failure -- "
           "production clusters run NameNode HA pairs specifically because of it.")

# 9. Diagram: YARN ----------------------------------------------------------
s = duplicate(prs, DIAGRAM)
set_para(s, "TextBox 1", 0, "YARN: Resource Management")
clear_shape(s, "TextBox 3")
diagram_box(s, Inches(4.9), Inches(1.95), Inches(3.5), Inches(0.95), "ResourceManager", "One per cluster — hands out containers", accent=True)
diagram_arrow(s, Inches(6.35), Inches(2.95), Inches(0.6), Inches(0.55), rotation=90)
diagram_box(s, Inches(4.9), Inches(3.55), Inches(3.5), Inches(0.95), "NodeManager", "One per machine — runs containers")
diagram_arrow(s, Inches(6.35), Inches(4.55), Inches(0.6), Inches(0.55), rotation=90)
diagram_box(s, Inches(4.9), Inches(5.15), Inches(3.5), Inches(0.95), "ApplicationMaster", "One per job — supervises its own tasks")
h.notes(s, "Hadoop 1.0 used a single JobTracker doing all of this -- it hit scaling limits. Hadoop "
           "2.0 split it into these three roles specifically to fix that. Payoff: YARN isn't wired "
           "to MapReduce specifically, so Spark, Hive, and other engines all run on the same "
           "cluster, sharing the same capacity.")

# 10. Statement: data locality payoff ---------------------------------------
s = duplicate(prs, STATEMENT)
set_para(s, "TextBox 1", 0, "The computation moves to the data — not the other way around.")
h.notes(s, "A single-machine script structurally cannot do this, no matter how it's written -- it "
           "has to pull all the data to itself first. This is the actual mechanism this session's "
           "demo is standing in for.")

# 11. Two Column: vertical vs horizontal scaling -----------------------------
s = duplicate(prs, TWOCOL)
set_para(s, "TextBox 1", 0, "Why Not Just Buy a Bigger Machine?")
set_para(s, "TextBox 3", 0, "Vertical Scaling")
set_para(s, "TextBox 3", 1, "One bigger box — hard RAM/CPU ceiling, cost climbs fastest near it")
set_para(s, "TextBox 5", 0, "Horizontal Scaling")
set_para(s, "TextBox 5", 1, "More ordinary boxes — no fixed ceiling, the choice Hadoop is built around")
h.notes(s, "Someone in the audience will ask 'why not just get more RAM' -- answer it here, "
           "proactively, before the RAM-ceiling numbers make it concrete a few slides from now.")

# 12. Section: Part 3 ---------------------------------------------------------
s = duplicate(prs, SECTION)
set_para(s, "TextBox 1", 0, "PART 3")
set_para(s, "TextBox 1", 1, "Seeing It Break")

# 13. Code: naive approach ----------------------------------------------------
s = duplicate(prs, CODE)
set_para(s, "TextBox 1", 0, "The Naive Approach")
set_multiline(s, "TextBox 3", 0, [
    "naive_wordcount <- function(reviews) {",
    "  tally <- new.env()",
    "  for (review in reviews) {",
    "    words <- strsplit(review, \" \")[[1]]",
    "    for (w in words) {",
    "      if (is.null(tally[[w]])) tally[[w]] <- 0L",
    "      tally[[w]] <- tally[[w]] + 1L",
    "    }",
    "  }",
    "  sort(unlist(as.list(tally)), decreasing = TRUE)",
    "}",
])
fix_code_font(s, "TextBox 3")
h.notes(s, "Emphasize: this code is not badly written. At toy scale (200 reviews, 8,000 words) it "
           "finishes in 0.014s. The flaw isn't speed -- it's that every review has to already be "
           "sitting in one process's memory before this can even start.")

# 14. Stat: RAM ceiling --------------------------------------------------------
s = duplicate(prs, STAT)
set_para(s, "TextBox 1", 0, "26.4×")
set_para(s, "TextBox 1", 1, "Over a single machine's 256 GB RAM ceiling")
h.notes(s, "500M reviews/day, ~150 bytes each, 90-day trailing window = 6.75 TB. A single machine's "
           "RAM ceiling is 256 GB. 6.75 TB / 256 GB = 26.4x. No amount of loop optimization fixes "
           "this -- the data has to live somewhere else from the start.")

# 15. Code: the fix -------------------------------------------------------------
s = duplicate(prs, CODE)
set_para(s, "TextBox 1", 0, "The Fix: Partition Like HDFS Would")
set_multiline(s, "TextBox 3", 0, [
    "partitions <- split(review_text, cut(seq_along(review_text), 8, labels = FALSE))",
    "",
    "map_fn <- function(reviews) table(unlist(strsplit(reviews, \" \")))",
    "",
    "partial_counts <- mclapply(partitions, map_fn, mc.cores = detectCores())",
    "final_counts   <- Reduce(reduce_fn, partial_counts)",
])
fix_code_font(s, "TextBox 3")
h.notes(s, "split() stands in for HDFS's pre-sharded blocks; mclapply() stands in for one mapper "
           "task per node. Point at what crosses the 'network' in this simulation: only the small "
           "partial tallies in reduce_fn, never the raw review text.")

# 16. Two Column: correctness + shard size -------------------------------------
s = duplicate(prs, TWOCOL)
set_para(s, "TextBox 1", 0, "Same Answer, Different Machine")
set_para(s, "TextBox 3", 0, "Correctness")
set_para(s, "TextBox 3", 1, "identical() confirms the exact same tally as the naive result")
set_para(s, "TextBox 5", 0, "Shard Size")
set_para(s, "TextBox 5", 1, "33.75 GB per node at 200 nodes — well under the 256 GB ceiling")
h.notes(s, "Both numbers come straight from the Rmd's actual run -- round(shard_gb, 2) = 33.75, "
           "identical() = TRUE. Nothing here is illustrative fiction.")

# 17. Key Points: honest complication -------------------------------------------
s = duplicate(prs, KEYPOINTS)
set_para(s, "TextBox 1", 0, "An Honest Complication")
set_para(s, "TextBox 3", 0, "—  Naive, single loop: 0.014s on the toy 8,000-word corpus")
set_para(s, "TextBox 3", 1, "—  Partitioned, 8 cores: 0.14s — slower, not faster")
set_para(s, "TextBox 3", 2, "—  Distribution pays off only once local work outweighs coordination cost")
h.notes(s, "This is a genuinely measured result from this week's Rmd, kept in rather than edited "
           "out. Nobody runs Hadoop on 8,000 words -- that's the 26x-over-RAM scenario, not this "
           "toy corpus, and this slide is why the distinction matters.")

# 18. Two Column: where MapReduce falls short + AI bridge -----------------------
s = duplicate(prs, TWOCOL)
set_para(s, "TextBox 1", 0, "Where MapReduce Falls Short")
set_para(s, "TextBox 3", 0, "The Honest Weak Spot")
set_para(s, "TextBox 3", 1, "Every stage round-trips through disk — 100 passes means 100 round-trips")
set_para(s, "TextBox 5", 0, "The Pattern Lives On")
set_para(s, "TextBox 5", 1, "Chunk → embed → route → assemble is map → shuffle → reduce for AI pipelines")
h.notes(s, "Teaching MapReduce's limitations builds credibility. This is the specific gap Spark "
           "closed by keeping data in memory across steps. The AI bridge is the payoff for a mixed "
           "exec/engineer audience: this architecture underpins infrastructure they're using today.")

# 19. Statement: the takeaway ------------------------------------------------
s = duplicate(prs, STATEMENT)
set_para(s, "TextBox 1", 0, "The pattern outlasts the engine.")
h.notes(s, "Closing idea for this section. Before reaching for a distributed system, ask the "
           "RAM-ceiling question first: does this actually not fit on one machine?")

# 20. Closing -----------------------------------------------------------------
s = duplicate(prs, CLOSING)
set_para(s, "TextBox 1", 0, "Thank you.")
set_para(s, "TextBox 1", 1, "Next: where a real cluster's shuffle step spends its time")
set_para(s, "TextBox 1", 2, "Questions?")

# Drop the 12 raw LAYOUT template slides now that every duplicate is filled.
for i in range(11, -1, -1):
    delete_slide(prs, i)

h.finalize_and_save(prs, OUT)
print(f"Saved {OUT} — {len(prs.slides)} slides")
