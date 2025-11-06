"""
Custom tools for Strwbrry vault operations
"""
from laddr import tool
from pathlib import Path
from typing import Dict, List


# Johnny Decimal structure reference (from your vault documentation)
JD_STRUCTURE = {
    "00-09": {
        "name": "Meta",
        "description": "About the vault itself",
        "categories": {
            "00": "Vault Index",
            "01": "Vault Core",
            "02": "Vault Extensions",
            "03": "Vault Discussions",
            "04": "Human Interface",
            "05": "Program Interface",
            "06": "Vault Maintenance",
            "09": "Vault Templates"
        }
    },
    "10-19": {
        "name": "Living",
        "description": "About living life day to day",
        "nature": "Temporal, present-focused",
        "categories": {
            "10": "Daily Journal",
            "11": "Weekly Journal",
            "12": "Monthly Journal",
            "13": "Annual Journal",
            "14": "Monthly Action Board"
        }
    },
    "20-29": {
        "name": "Life",
        "description": "About your life",
        "nature": "Personal, self-focused",
        "categories": {
            "20": "Personal Identity & Values",
            "21": "Mental Health",
            "22": "My Personal Growth",
            "23": "My Daily Rhythm",
            "24": "Physical Health",
            "25": "My Diet and Cooking",
            "26": "My Living Space",
            "27": "My Relationships",
            "28": "Personal Finances",
            "29": "Legal Documents"
        }
    },
    "30-39": {
        "name": "Lived",
        "description": "About making or made memories",
        "nature": "Past-focused, reflective",
        "categories": {
            "30": "Looking Back At My Life",
            "31": "Remembering Those Around Me",
            "32": "Events",
            "33": "Trips and Vacations"
        }
    },
    "40-49": {
        "name": "Learn",
        "description": "About learning and education",
        "categories": {
            "40": "Credentials & Certificates",
            "41": "Academic",
            "42": "Self-Guided",
            "43": "Courses & Workshops",
            "44": "Textbook & Wiki Repo",
            "45": "Articles & Video",
            "46": "Resources & Tools"
        }
    },
    "50-59": {
        "name": "Work",
        "description": "About career and job",
        "categories": {
            "50": "Resume & Job Searching",
            "51": "Audio Engineering",
            "52": "Chris Miller Photography",
            "54": "Joose Rocks",
            "55": "Drone Pilot",
            "56": "Aji's-Shiki Sushi & Grill"
        }
    },
    "60-69": {
        "name": "Play",
        "description": "About recreation and fun",
        "categories": {
            "60": "Overarching Fun",
            "61": "Video Games"
        }
    },
    "70-79": {
        "name": "Creation",
        "description": "About making something",
        "categories": {
            "70": "Brainstorm",
            "71": "Writing",
            "72": "Art",
            "73": "Music",
            "74": "Code",
            "75": "Video",
            "76": "Photo",
            "77": "Maker Builds",
            "78": "Home DIY",
            "79": "Fabrication"
        }
    },
    "80-89": {
        "name": "System",
        "description": "About systems and reference",
        "nature": "Technical, objective",
        "categories": {
            "80": "Strwbrry",
            "81": "Inventory",
            "82": "Devices & Hardware",
            "83": "Software & Services",
            "84": "Configurations",
            "85": "Script & Automation",
            "86": "Data Repository",
            "87": "Device Usage",
            "88": "Reference",
            "89": "System Design"
        }
    },
    "90-99": {
        "name": "Archive",
        "description": "About data and past",
        "categories": {
            "90": "Overall Archive",
            "91": "Photo Library",
            "92": "Video Library",
            "93": "Computer Backups",
            "99": "Inactive"
        }
    },
    "100": {
        "name": "Inbox",
        "description": "Unsorted items awaiting processing"
    }
}


@tool
def get_jd_structure() -> Dict:
    """
    Returns the complete Johnny Decimal structure for the Strwbrry vault.

    Returns:
        Dictionary containing all areas (00-100) with their categories and descriptions
    """
    return JD_STRUCTURE


@tool
def find_jd_category(area_code: str, category_number: str) -> Dict:
    """
    Look up a specific JD category by area and category number.

    Args:
        area_code: Area range like "20-29", "50-59", etc.
        category_number: Two-digit category like "25", "51", etc.

    Returns:
        Dictionary with category details or error
    """
    if area_code not in JD_STRUCTURE:
        return {"error": f"Area {area_code} not found"}

    area = JD_STRUCTURE[area_code]
    if "categories" in area and category_number in area["categories"]:
        return {
            "area": area_code,
            "area_name": area["name"],
            "category": category_number,
            "category_name": area["categories"][category_number],
            "area_description": area.get("description", "")
        }

    return {"error": f"Category {category_number} not found in area {area_code}"}


@tool
def suggest_jd_location(content_description: str, keywords: List[str] = None) -> Dict:
    """
    Suggests appropriate Johnny Decimal location based on content description.
    This is a helper tool that formats the structure for easier LLM decision-making.

    Args:
        content_description: Description of the note content
        keywords: Optional list of keywords to help categorization

    Returns:
        Dictionary with suggestions and reasoning structure
    """
    # Return structured info for the LLM to make informed decisions
    return {
        "task": "Analyze the content and suggest appropriate JD location",
        "content": content_description,
        "keywords": keywords or [],
        "jd_structure": JD_STRUCTURE,
        "guidance": {
            "ethereal_to_concrete": "Areas 10-30 are personal/subjective, 70-90 are technical/objective",
            "temporal_flow": "10s=present (Living), 30s=past (Lived), 40s=learning (future)",
            "special_folders": {
                "XX.00": "Root/overview folders for each category",
                "XX.99": "External or miscellaneous items in category"
            }
        }
    }


@tool
def generate_frontmatter(title: str, note_type: str = "human", tags: List[str] = None) -> str:
    """
    Generates Strwbrry-compliant frontmatter for a markdown note.

    Args:
        title: Note title
        note_type: Type of note ("human" or "machine")
        tags: Optional list of tags

    Returns:
        Formatted YAML frontmatter string
    """
    import uuid
    from datetime import datetime

    frontmatter = [
        "---",
        f"UUID: {uuid.uuid4()}",
        f"Date: {datetime.now().strftime('%Y-%m-%d')}",
        f"Type: {note_type}",
        f"Title: {title}"
    ]

    if tags:
        frontmatter.append(f"Tags: {', '.join(tags)}")

    frontmatter.append("---")
    frontmatter.append("")  # Blank line after frontmatter

    return "\n".join(frontmatter)
