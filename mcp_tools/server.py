import asyncio
import json
from typing import List, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from .resume_parser import parse_resume as core_parse_resume
from .job_recommender import recommend_jobs as core_recommend_jobs

server = Server("resume-job-matcher")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """Return the list of tools this MCP server exposes."""
    return [
        Tool(
            name="parse_resume",
            description="Extract structured info from a resume file (PDF/TXT).",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the resume file (PDF/TXT)",
                    }
                },
                "required": ["file_path"],
            },
        ),
        Tool(
            name="recommend_jobs",
            description="Suggest jobs based on extracted skills.",
            inputSchema={
                "type": "object",
                "properties": {
                    "skills": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of skill names",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Maximum number of jobs to return",
                        "default": 5,
                    },
                },
                "required": ["skills"],
            },
        ),
    ]

@server.call_tool()
async def call_tool(
    name: str, arguments: dict
) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    try:
        if name == "parse_resume":
            file_path = arguments["file_path"]
            result = core_parse_resume(file_path)
            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2),
                )
            ]

        elif name == "recommend_jobs":
            skills = arguments.get("skills", [])
            top_k = int(arguments.get("top_k", 5))
            jobs = core_recommend_jobs(skills, top_k=top_k)
            return [
                TextContent(
                    type="text",
                    text=json.dumps(jobs, indent=2),
                )
            ]

        else:
            return [
                TextContent(
                    type="text",
                    text=f"Error: unknown tool '{name}'",
                )
            ]

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Error while executing tool '{name}': {e}",
            )
        ]

async def serve() -> None:
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)


def main() -> None:
    asyncio.run(serve())

if __name__ == "__main__":
    main()