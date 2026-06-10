import json
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("notes")

NOTES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes.json")


def load_notes():
    """Load notes from the JSON file."""
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r") as f:
            return json.load(f)
    return []


def save_notes(notes):
    """Save notes to the JSON file."""
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=2)


@mcp.tool()
def create_note(title: str, content: str, tags: list[str] | None = None) -> str:
    """Create a new note with a title, content, and optional tags.

    Args:
        title: The title of the note
        content: The body content of the note
        tags: Optional list of tags to categorize the note
    """
    notes = load_notes()
    note = {
        "id": len(notes) + 1,
        "title": title,
        "content": content,
        "tags": tags or [],
        "created_at": datetime.now().isoformat(),
    }
    notes.append(note)
    save_notes(notes)
    return f"Note '{title}' created successfully with ID {note['id']}."


@mcp.tool()
def search_notes(query: str) -> str:
    """Search notes by title or content.

    Args:
        query: The search term to look for in note titles and content
    """
    notes = load_notes()
    query_lower = query.lower()
    matches = [
        n
        for n in notes
        if query_lower in n["title"].lower() or query_lower in n["content"].lower()
    ]
    if not matches:
        return "No notes found matching your query."
    results = []
    for note in matches:
        tags_str = ", ".join(note["tags"]) if note["tags"] else "none"
        results.append(
            f"[ID: {note['id']}] {note['title']}\n"
            f"  Tags: {tags_str}\n"
            f"  {note['content'][:100]}"
        )
    return "\n---\n".join(results)


@mcp.tool()
def delete_note(note_id: int) -> str:
    """Delete a note by its ID.

    Args:
        note_id: The unique ID of the note to delete
    """
    notes = load_notes()
    original_count = len(notes)
    notes = [n for n in notes if n["id"] != note_id]
    if len(notes) == original_count:
        return f"No note found with ID {note_id}."
    save_notes(notes)
    return f"Note {note_id} deleted successfully."

@mcp.resource("notes://all")
def get_all_notes() -> str:
    """Get all notes as formatted text."""
    notes = load_notes()
    if not notes:
        return "No notes stored yet."
    results = []
    for note in notes:
        tags_str = ", ".join(note["tags"]) if note["tags"] else "none"
        results.append(
            f"[ID: {note['id']}] {note['title']}\n"
            f"  Tags: {tags_str}\n"
            f"  Created: {note['created_at']}\n"
            f"  {note['content']}"
        )
    return "\n---\n".join(results)


@mcp.resource("notes://tags")
def get_all_tags() -> str:
    """Get all unique tags used across notes."""
    notes = load_notes()
    all_tags = set()
    for note in notes:
        all_tags.update(note.get("tags", []))
    if not all_tags:
        return "No tags found."
    return ", ".join(sorted(all_tags))


@mcp.prompt()
def summarize_notes() -> str:
    """Generate a prompt asking Claude to summarize and analyze all notes."""
    return (
        "Please read all my notes using the notes://all resource and provide:\n"
        "1. A brief summary of each note\n"
        "2. Common themes or topics across notes\n"
        "3. Any suggested actions or follow-ups based on the content"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")