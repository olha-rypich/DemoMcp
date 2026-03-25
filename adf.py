
def to_adf(text: str) -> dict:
    if not text:
        text = ""

    text = text.replace("\\n", "\n")

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    content = []
    for paragraph in paragraphs:
        lines = paragraph.split("\n")
        inline_content = []

        for i, line in enumerate(lines):
            if line.strip():
                inline_content.append({"type": "text", "text": line})

            if i < len(lines) - 1:
                inline_content.append({"type": "hardBreak"})

        if inline_content:
            content.append({
                "type": "paragraph",
                "content": inline_content,
            })

    if not content:
        content = [{
            "type": "paragraph",
            "content": [{"type": "text", "text": " "}]
        }]

    return {
        "type": "doc",
        "version": 1,
        "content": content
    }