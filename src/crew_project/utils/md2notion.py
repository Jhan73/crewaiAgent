import re

def parse_markdown_to_blocks(markdown_content: str) -> list:
        """Convert markdown content to Notion blocks."""
        blocks = []
        # Split content into lines
        lines = markdown_content.split('\n')
        current_list_type = None
        list_items = []

        def parse_inline_formatting(text: str) -> list:
            """Parse inline markdown formatting (bold, links, code) into rich text segments."""
            rich_text = []
            i = 0
            while i < len(text):
                # Handle bold text
                if text[i:i+2] == '**':
                    end = text.find('**', i+2)
                    if end != -1:
                        rich_text.append({
                            "type": "text",
                            "text": {"content": text[i+2:end]},
                            "annotations": {"bold": True}
                        })
                        i = end + 2
                        continue
                # Handle links
                elif text[i] == '[':
                    end_bracket = text.find(']', i)
                    if end_bracket != -1 and text[end_bracket+1:end_bracket+2] == '(':
                        end_url = text.find(')', end_bracket+2)
                        if end_url != -1:
                            link_text = text[i+1:end_bracket]
                            link_url = text[end_bracket+2:end_url]
                            rich_text.append({
                                "type": "text",
                                "text": {"content": link_text, "link": {"url": link_url}}
                            })
                            i = end_url + 1
                            continue
                # Handle inline code
                elif text[i] == '`':
                    end = text.find('`', i+1)
                    if end != -1:
                        rich_text.append({
                            "type": "text",
                            "text": {"content": text[i+1:end]},
                            "annotations": {"code": True}
                        })
                        i = end + 1
                        continue
                # Regular text
                if i < len(text):
                    # Find the next special character
                    next_special = len(text)
                    for special in ['**', '[', '`']:
                        pos = text.find(special, i)
                        if pos != -1 and pos < next_special:
                            next_special = pos
                    
                    if next_special > i:
                        rich_text.append({
                            "type": "text",
                            "text": {"content": text[i:next_special]}
                        })
                        i = next_special
                    else:
                        rich_text.append({
                            "type": "text",
                            "text": {"content": text[i:]}
                        })
                        break
            return rich_text

        i = 0
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
                continue

            # Headers
            if line.startswith('# '):
                blocks.append({
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {"rich_text": parse_inline_formatting(line[2:])}
                })
            elif line.startswith('## '):
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {"rich_text": parse_inline_formatting(line[3:])}
                })
            elif line.startswith('### '):
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {"rich_text": parse_inline_formatting(line[4:])}
                })
            # Code blocks
            elif line.startswith('```'):
                # Extract language if specified
                language = line[3:].strip() or "plain text"
                # Find the closing ```
                code_content = []
                i += 1  # Move to next line
                while i < len(lines) and not lines[i].startswith('```'):
                    code_content.append(lines[i])
                    i += 1
                
                blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": '\n'.join(code_content)}}],
                        "language": language
                    }
                })
            # Bullet lists
            elif line.strip().startswith('- '):
                if current_list_type != "bulleted_list_item":
                    # Add previous list if exists
                    if list_items:
                        blocks.extend(list_items)
                        list_items = []
                current_list_type = "bulleted_list_item"
                content = line.strip()[2:]  # Remove the bullet point
                list_items.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": parse_inline_formatting(content)}
                })
            # Numbered lists
            elif re.match(r'^\d+\. ', line.strip()):
                if current_list_type != "numbered_list_item":
                    # Add previous list if exists
                    if list_items:
                        blocks.extend(list_items)
                        list_items = []
                current_list_type = "numbered_list_item"
                content = re.sub(r'^\d+\. ', '', line.strip())
                list_items.append({
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {"rich_text": parse_inline_formatting(content)}
                })
            # Regular paragraph
            else:
                if list_items:
                    blocks.extend(list_items)
                    list_items = []
                    current_list_type = None
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": parse_inline_formatting(line)}
                })
            i += 1

        # Add any remaining list items
        if list_items:
            blocks.extend(list_items)

        return blocks