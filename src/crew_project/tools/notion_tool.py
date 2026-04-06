from crewai.tools import BaseTool
from typing import Type, Any, Optional
from pydantic import BaseModel, Field, PrivateAttr
import dotenv, os
from notion_client import Client
from ..utils.md2notion import parse_markdown_to_blocks


dotenv.load_dotenv()

class NotionToolInput(BaseModel):
    """Input schema for NotionTool."""
    title: str = Field(..., description="Title of the page to create")
    content: str = Field(..., description="Markdown content to add to the page")

class NotionTool(BaseTool):
    name: str = "Notion_tool"
    description: str = (
        "A tool that creates a new page in a Notion database with the specified title and markdown content"
    )
    args_schema: Type[BaseModel] = NotionToolInput
    
    _notion: Any = PrivateAttr()
    _db_id: str = PrivateAttr()

    class Config:
        extra= "allow"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        token = os.getenv("NOTION_TOKEN")
        if not token:
            raise ValueError("NOTION_TOKEN is not set in environment variables")    

        db_id = os.getenv("NOTION_DB_ID")
        if not db_id:
            raise ValueError("NOTION_DB_ID is not set in environment variables")
        
        self._notion = Client(auth=token)
        self._db_id = db_id


    def _run(self, title: str, content: str) -> str:
        blocks = parse_markdown_to_blocks(content)
        first_chunck = blocks[:100]
        try:
            page = self._notion.pages.create(
                parent={"database_id": self._db_id},
                properties={
                    "Name": {"title": [{"text": {"content": title}}]},
                    "Type": {"multi_select": [{"name": "Video"}]},
                    "Status": {"status": {"name": "In progress"}},
                },
                children=first_chunck
            )
            remaining_blocks = blocks[100:]
            if remaining_blocks:
                for i in range(0, len(remaining_blocks), 100):
                    batch = remaining_blocks[i: i + 100]
                    self._notion.blocks.children.append(
                        block_id=page["id"],
                        children=batch
                    )
            return f"Created page {title} with {len(blocks)} blocks"
        
        except Exception as e:
            return f"There was an error creating the Notion page {e}."
