from fpdf import FPDF

def generate_pdf(text, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)

    lines = []
    for paragraph in text.split("\n"):
        paragraph = paragraph.strip()
        if paragraph:
            while len(paragraph) > 0:
                wrap_at = 90
                if len(paragraph) <= wrap_at:
                    lines.append(paragraph)
                    break
                else:
                    split_at = paragraph.rfind(" ", 0, wrap_at)
                    if split_at == -1:
                        split_at = wrap_at
                    lines.append(paragraph[:split_at].strip())
                    paragraph = paragraph[split_at:].strip()
        else:
            lines.append("")

    for line in lines:
        pdf.cell(0, 10, text=line, new_x="LMARGIN", new_y="NEXT")

    pdf.output(output_path)
    return True
