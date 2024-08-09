import logging
import os
import requests  # third party dep

logging.basicConfig(level=logging.DEBUG)

NOTION_API_BASE = "https://api.notion.com/v1/"
NOTION_BLOCKS_API_BASE = f"{NOTION_API_BASE}blocks/"

def retrieve_full_page(page_id: str):
    """
    Retrieve the full content of a Notion page using the 'blocks' endpoint to get all of the page's children.
    """
    children = []
    blog_listing_block_children_url = f"{NOTION_BLOCKS_API_BASE}{page_id}/children?page_size=100"
    token = os.environ['NOTION_API_TOKEN']
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
    }
    has_more = True
    next_cursor = None
    while has_more:
        if next_cursor:
            res = requests.get(
                f"{blog_listing_block_children_url}&start_cursor={next_cursor}",
                headers=headers,
            )
        else:
            res = requests.get(
                blog_listing_block_children_url,
                headers=headers
            )

        data = res.json()
        has_more = data.get("has_more", False)
        if has_more:
            next_cursor = data.get("next_cursor")
        children.extend(data.get("results", []))

    return children

# Replace with your actual Notion page ID
blog_listing_page_id = "72ca210a84414d95b8c4e0f3b2a1c8f5"
children = retrieve_full_page(page_id=blog_listing_page_id)
import pdb; pdb.set_trace()