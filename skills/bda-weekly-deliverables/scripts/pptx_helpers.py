# /// script
# requires-python = ">=3.11"
# dependencies = ["python-pptx>=1.0", "lxml"]
# ///
"""Reusable python-pptx slide-building helpers, extracted from
session5/generate_deck.py so the cross-platform fixes below are written
once and imported, not hand-retyped into a new script every week.

Confirmed fixes baked in (see the project's pptx cross-compat memory):
  - FONT = "Arial": Windows-only faces (Segoe UI, Cambria Math, Calibri)
    make Keynote reject the whole file, not just substitute the glyph.
  - finalize_and_save() sets sldSz@type to match the real aspect ratio
    and patches docProps/app.xml's stale slide count/format/titles --
    python-pptx never updates either from the default template.

These are the confirmed-good fixes only. A full session5 deck still
failed to import in Keynote for an unresolved reason as of 2026-08-24;
that root cause is untouched here by design -- see the skill's memlog.

Import and call these from a per-week build script; content (titles,
card text, tables) is that script's job, not this module's.
"""
import copy

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

FONT = "Arial"

BG = RGBColor(0xFF, 0xFF, 0xFF)
CARD = RGBColor(0xF1, 0xF5, 0xF9)
FORMULA_BG = RGBColor(0xEF, 0xF6, 0xFF)
TEXT = RGBColor(0x0F, 0x17, 0x2A)
MUTED = RGBColor(0x47, 0x55, 0x69)
BLUE = RGBColor(0x1D, 0x4E, 0xD8)
CYAN = RGBColor(0x0E, 0x74, 0x90)
BORDER = RGBColor(0xCB, 0xD5, 0xE1)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
CODE_BG = RGBColor(0x11, 0x16, 0x2E)
CODE_TEXT = RGBColor(0xE8, 0xEC, 0xF6)


def new_presentation(width_in=13.333, height_in=7.5):
    prs = Presentation()
    prs.slide_width = Inches(width_in)
    prs.slide_height = Inches(height_in)
    return prs


def new_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = BG
    return slide


def add_title(slide, title, kicker=None):
    top = Inches(0.35)
    if kicker:
        box = slide.shapes.add_textbox(Inches(0.6), top, Inches(11.5), Inches(0.35))
        p = box.text_frame.paragraphs[0]
        p.text = kicker.upper()
        p.font.size, p.font.bold, p.font.color.rgb, p.font.name = Pt(13), True, CYAN, FONT
        top = Inches(0.68)
    box = slide.shapes.add_textbox(Inches(0.6), top, Inches(12.1), Inches(0.8))
    p = box.text_frame.paragraphs[0]
    p.text = title
    p.font.size, p.font.bold, p.font.color.rgb, p.font.name = Pt(30), True, TEXT, FONT


def _estimate_card_height(w, header, body_lines, body_size):
    """Deterministic content-height estimate in EMU. Shape autofit
    (spAutoFit) isn't reliably applied by LibreOffice or Keynote for
    autoshapes -- confirmed by QA render -- so height is computed here
    instead of left to the host app."""
    margin_pt = 0.14 * 72
    usable_pt = (w / 914400) * 72 - 2 * margin_pt

    def visual_lines(text, size_pt):
        avg_char_pt = size_pt * 0.52
        cpl = max(1, usable_pt / avg_char_pt)
        return max(1, -(-len(text) // cpl))  # ceil

    total_lines_pt = visual_lines(header, 15) * 15 * 1.25
    for line in body_lines:
        total_lines_pt += visual_lines("• " + line, body_size) * body_size * 1.35 + 4
    return Pt(total_lines_pt + 2 * margin_pt)


def add_card(slide, x, y, w, h, header, body_lines, body_size=13.5, header_color=CYAN):
    """h is a cap, not a target: the card shrinks to its estimated content
    height so short cards don't leave a slide-dominating empty box. Pass
    the largest height acceptable for the slide's layout."""
    content_h = _estimate_card_height(w, header, body_lines, body_size)
    if content_h < h:
        h = content_h
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    shape.fill.solid(); shape.fill.fore_color.rgb = CARD
    shape.line.color.rgb = BORDER; shape.line.width = Pt(0.75)
    shape.adjustments[0] = 0.05
    tf = shape.text_frame
    tf.word_wrap = True
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, Inches(0.14))
    p0 = tf.paragraphs[0]
    p0.text = header
    p0.font.bold, p0.font.size, p0.font.color.rgb, p0.font.name = True, Pt(15), header_color, FONT
    for line in body_lines:
        p = tf.add_paragraph()
        p.text = "• " + line
        p.font.size, p.font.color.rgb, p.font.name = Pt(body_size), TEXT, FONT
        p.space_after = Pt(4)
    return shape


def add_formula(slide, x, y, w, h, formula, label=None, size=20):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    shape.fill.solid(); shape.fill.fore_color.rgb = FORMULA_BG
    shape.line.color.rgb = BLUE; shape.line.width = Pt(1)
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = formula
    p.alignment = PP_ALIGN.CENTER
    p.font.size, p.font.italic, p.font.color.rgb, p.font.name = Pt(size), True, CYAN, FONT
    if label:
        p2 = tf.add_paragraph()
        p2.text = label
        p2.alignment = PP_ALIGN.CENTER
        p2.font.size, p2.font.color.rgb, p2.font.name = Pt(11), MUTED, FONT
    return shape


def add_stat_callout(slide, x, y, w, h, value, label, value_color=BLUE):
    """Big-number KPI tile: for a headline metric, use this instead of a
    card+bullet so the slide isn't the same layout as every other one."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    shape.fill.solid(); shape.fill.fore_color.rgb = CARD
    shape.line.color.rgb = BORDER; shape.line.width = Pt(0.75)
    shape.adjustments[0] = 0.08
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = value
    p.alignment = PP_ALIGN.CENTER
    p.font.size, p.font.bold, p.font.color.rgb, p.font.name = Pt(44), True, value_color, FONT
    p2 = tf.add_paragraph()
    p2.text = label
    p2.alignment = PP_ALIGN.CENTER
    p2.font.size, p2.font.color.rgb, p2.font.name = Pt(12.5), MUTED, FONT
    return shape


def add_table(slide, x, y, w, h, data):
    rows, cols = len(data), len(data[0])
    tbl = slide.shapes.add_table(rows, cols, x, y, w, h).table
    for r in range(rows):
        for c in range(cols):
            cell = tbl.cell(r, c)
            cell.text = str(data[r][c])
            cell.fill.solid()
            cell.fill.fore_color.rgb = BLUE if r == 0 else CARD
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            para = cell.text_frame.paragraphs[0]
            para.font.size = Pt(12.5)
            para.font.bold = (r == 0)
            para.font.color.rgb = WHITE if r == 0 else TEXT
            para.font.name = FONT
    return tbl


def add_code(slide, x, y, w, h, code_lines, label=None):
    """Monospace code block. Courier New (not FONT/Arial) -- it's a
    cross-platform face present on Mac and Windows alike, the same choice
    build_hybrid_deck.js's CODE_FONT already made for Keynote safety."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    shape.fill.solid(); shape.fill.fore_color.rgb = CODE_BG
    shape.line.color.rgb = BORDER; shape.line.width = Pt(0.75)
    shape.adjustments[0] = 0.05
    tf = shape.text_frame
    tf.word_wrap = True
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, Inches(0.16))
    for i, line in enumerate(code_lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.size, p.font.color.rgb, p.font.name = Pt(13), CODE_TEXT, "Courier New"
    if label:
        p = tf.add_paragraph()
        p.text = label
        p.font.size, p.font.color.rgb, p.font.name = Pt(10.5), MUTED, FONT
        p.space_before = Pt(6)
    return shape


def add_bullets(slide, x, y, w, h, items, size=15):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = "• " + item
        p.font.size, p.font.color.rgb, p.font.name = Pt(size), TEXT, FONT
        p.space_after = Pt(8)
    return box


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def duplicate_slide(prs, index):
    """Duplicate slide `index` (0-based) and return the new slide, appended
    at the end of prs.slides. Used to turn one of the apple-style template's
    12 LAYOUT pattern slides into a real content slide: the new slide keeps
    the source's layout (so theme/placeholders match) and its shape content,
    ready for you to edit in place. The source slide at `index` is untouched
    and keeps its index, so it's safe to call this repeatedly against the
    same template index. These template slides carry no images and no notes
    worth keeping, so only shape XML is copied -- set real notes on the
    result with notes(), don't expect the source's."""
    source = prs.slides[index]
    dest = prs.slides.add_slide(source.slide_layout)
    for shape in list(dest.shapes):
        shape._element.getparent().remove(shape._element)
    for shape in source.shapes:
        dest.shapes._spTree.append(copy.deepcopy(shape._element))

    # Slide-level background (e.g. the template's solid-white override) lives
    # as a <p:bg> sibling of <p:spTree>, not inside it -- shape copying above
    # never touches it, so without this the duplicate silently falls back to
    # the master's default background.
    source_bg = source.part._element.find(qn("p:cSld")).find(qn("p:bg"))
    if source_bg is not None:
        dest_cSld = dest.part._element.find(qn("p:cSld"))
        dest_bg = dest_cSld.find(qn("p:bg"))
        if dest_bg is not None:
            dest_cSld.remove(dest_bg)
        dest_cSld.insert(0, copy.deepcopy(source_bg))
    return dest


def delete_slide(prs, index):
    """Remove slide `index` (0-based). Use this to drop the template's
    original 12 LAYOUT pattern slides once their content has been
    duplicated elsewhere -- deleting by a fixed index repeatedly (e.g.
    delete_slide(prs, 0) twelve times) works since every deletion shifts
    later slides down by one and the patterns are always the first 12."""
    sldId = prs.slides._sldIdLst.sldId_lst[index]
    prs.part.drop_rel(sldId.get(qn("r:id")))
    prs.slides._sldIdLst.remove(sldId)


def finalize_and_save(prs, path):
    """Patch sldSz@type, docProps/app.xml, and a missing notesMasterIdLst,
    then save. Call this last."""
    w, h = prs.slide_width, prs.slide_height
    sld_type = "screen16x9" if abs(w / h - 16 / 9) < abs(w / h - 4 / 3) else "screen4x3"
    prs.part._element.find(qn("p:sldSz")).set("type", sld_type)

    # If notes were added, python-pptx links notesMaster1.xml in
    # presentation.xml.rels but never declares <p:notesMasterIdLst> for it.
    # PowerPoint tolerates that orphaned relationship; Keynote rejects the
    # whole file. Add the element if the relationship exists.
    pres_el = prs.part._element
    if pres_el.find(qn("p:notesMasterIdLst")) is None:
        for rel in prs.part.rels.values():
            if rel.reltype.endswith("/notesMaster"):
                lst = pres_el.makeelement(qn("p:notesMasterIdLst"), {})
                item = lst.makeelement(qn("p:notesMasterId"), {qn("r:id"): rel.rId})
                lst.append(item)
                pres_el.insert(list(pres_el).index(pres_el.find(qn("p:sldMasterIdLst"))) + 1, lst)
                break

    from lxml import etree
    EP_NS = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
    VT_NS = "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"
    app_part = next(p for p in prs.part.package.iter_parts() if p.partname == "/docProps/app.xml")
    app_xml = etree.fromstring(app_part.blob)
    ns = {"ep": EP_NS, "vt": VT_NS}

    app_xml.find("ep:Slides", ns).text = str(len(prs.slides))
    app_xml.find("ep:PresentationFormat", ns).text = (
        "On-screen Show (16:9)" if sld_type == "screen16x9" else "On-screen Show (4:3)"
    )

    heading_pairs = app_xml.find("ep:HeadingPairs/vt:vector", ns)
    heading_pairs[3].find("vt:i4", ns).text = str(len(prs.slides))

    titles_vector = app_xml.find("ep:TitlesOfParts/vt:vector", ns)
    for _ in prs.slides:
        etree.SubElement(titles_vector, f"{{{VT_NS}}}lpstr")
    titles_vector.set("size", str(int(titles_vector.get("size")) + len(prs.slides)))

    app_part.blob = etree.tostring(app_xml, xml_declaration=True, encoding="UTF-8", standalone=True)

    prs.save(path)
    return path
