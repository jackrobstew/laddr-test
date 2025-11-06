"""
Read-only vault analysis tools for advisory agents
These tools NEVER modify the vault, only read and analyze
"""
from laddr import tool
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import Counter
import os


def _find_vault_root() -> Optional[Path]:
    """Find the Strwbrry vault root directory"""
    # Check if VAULT_PATH is set in environment
    vault_path = os.getenv("VAULT_PATH")
    if vault_path and Path(vault_path).exists():
        return Path(vault_path)

    # Common locations
    common_paths = [
        Path.home() / "Documents" / "SPLN",
        Path.home() / "SPLN",
        Path("/mnt/user/Documents/SPLN"),
    ]

    for path in common_paths:
        if path.exists() and path.is_dir():
            return path

    return None


@tool
def check_vault_connection() -> Dict:
    """
    Verify connection to the Strwbrry vault.
    Returns vault location and basic stats.
    """
    vault_root = _find_vault_root()

    if not vault_root:
        return {
            "status": "not_found",
            "message": "Vault not found. Set VAULT_PATH environment variable.",
            "suggestion": "export VAULT_PATH=/path/to/Documents/SPLN"
        }

    # Count markdown files
    md_files = list(vault_root.rglob("*.md"))

    # Count by area
    area_counts = {}
    for md_file in md_files:
        parts = md_file.relative_to(vault_root).parts
        if parts:
            area = parts[0]
            area_counts[area] = area_counts.get(area, 0) + 1

    return {
        "status": "connected",
        "vault_path": str(vault_root),
        "total_notes": len(md_files),
        "areas": area_counts
    }


@tool
def read_vault_area(area_name: str, file_limit: int = 20) -> Dict:
    """
    Read notes from a specific JD area.
    Returns list of note paths and basic info.

    Args:
        area_name: Area folder name (e.g., "10-19 - Living", "50-59 - Work")
        file_limit: Maximum number of files to return

    Returns:
        Dictionary with note information
    """
    vault_root = _find_vault_root()
    if not vault_root:
        return {"error": "Vault not found"}

    area_path = vault_root / area_name
    if not area_path.exists():
        return {"error": f"Area {area_name} not found in vault"}

    md_files = list(area_path.rglob("*.md"))[:file_limit]

    notes = []
    for md_file in md_files:
        rel_path = md_file.relative_to(vault_root)
        # Get file stats
        stat = md_file.stat()
        notes.append({
            "path": str(rel_path),
            "name": md_file.name,
            "size_kb": round(stat.st_size / 1024, 2),
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
            "modified_timestamp": stat.st_mtime
        })

    # Sort by modification time (most recent first)
    notes.sort(key=lambda x: x["modified_timestamp"], reverse=True)

    return {
        "area": area_name,
        "total_notes": len(md_files),
        "notes": notes,
        "most_recent": notes[0]["modified"] if notes else None
    }


@tool
def count_updates_by_area(days: int = 30) -> Dict:
    """
    Count file updates across all JD areas in the last N days.
    Reveals where attention is actually going.

    Args:
        days: Number of days to look back

    Returns:
        Dictionary with update counts per area
    """
    vault_root = _find_vault_root()
    if not vault_root:
        return {"error": "Vault not found"}

    cutoff_time = (datetime.now() - timedelta(days=days)).timestamp()

    area_updates = {}
    total_updates = 0

    # Get all top-level area folders
    for area_dir in sorted(vault_root.iterdir()):
        if area_dir.is_dir() and not area_dir.name.startswith('.'):
            md_files = list(area_dir.rglob("*.md"))
            updated_files = [
                f for f in md_files
                if f.stat().st_mtime > cutoff_time
            ]

            if updated_files:
                area_updates[area_dir.name] = {
                    "count": len(updated_files),
                    "total_files": len(md_files),
                    "update_rate": round(len(updated_files) / len(md_files) * 100, 1) if md_files else 0
                }
                total_updates += len(updated_files)

    # Calculate percentages
    for area, data in area_updates.items():
        data["percentage"] = round(data["count"] / total_updates * 100, 1) if total_updates else 0

    # Sort by count
    sorted_areas = dict(sorted(area_updates.items(), key=lambda x: x[1]["count"], reverse=True))

    return {
        "period_days": days,
        "total_updates": total_updates,
        "areas": sorted_areas,
        "top_area": list(sorted_areas.keys())[0] if sorted_areas else None
    }


@tool
def read_recent_journals(days: int = 7, area: str = "10-19 - Living") -> Dict:
    """
    Read recent journal entries to understand current state.

    Args:
        days: Number of days to look back
        area: Journal area (default: 10-19 - Living)

    Returns:
        Dictionary with journal entries
    """
    vault_root = _find_vault_root()
    if not vault_root:
        return {"error": "Vault not found"}

    area_path = vault_root / area
    if not area_path.exists():
        return {"error": f"Area {area} not found"}

    cutoff_time = (datetime.now() - timedelta(days=days)).timestamp()

    # Look for journal files (typically in daily journal folder)
    journal_path = area_path / "10 - Daily Journal" / "10.10 - Daily Journal - 2025"
    if not journal_path.exists():
        journal_path = area_path / "10 - Daily Journal"

    if not journal_path.exists():
        return {"error": "Daily journal folder not found", "searched": str(area_path)}

    md_files = list(journal_path.rglob("*.md"))
    recent_journals = [
        f for f in md_files
        if f.stat().st_mtime > cutoff_time
    ]

    # Sort by modification time
    recent_journals.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    journal_entries = []
    for journal_file in recent_journals[:days]:
        stat = journal_file.stat()

        # Read first 500 chars for preview
        try:
            content = journal_file.read_text(encoding='utf-8')
            preview = content[:500] + "..." if len(content) > 500 else content
        except:
            preview = "[Could not read content]"

        journal_entries.append({
            "date": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d"),
            "name": journal_file.name,
            "size_kb": round(stat.st_size / 1024, 2),
            "preview": preview
        })

    return {
        "period_days": days,
        "entries_found": len(journal_entries),
        "entries": journal_entries
    }


@tool
def search_vault_content(query: str, area: Optional[str] = None, limit: int = 10) -> Dict:
    """
    Search for specific content across vault (or specific area).

    Args:
        query: Search term
        area: Optional area to restrict search
        limit: Max results to return

    Returns:
        Dictionary with matching files
    """
    vault_root = _find_vault_root()
    if not vault_root:
        return {"error": "Vault not found"}

    search_path = vault_root / area if area else vault_root
    if not search_path.exists():
        return {"error": f"Path {search_path} not found"}

    matches = []
    md_files = list(search_path.rglob("*.md"))[:100]  # Limit to first 100 for performance

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8').lower()
            if query.lower() in content:
                # Get context around match
                index = content.find(query.lower())
                start = max(0, index - 50)
                end = min(len(content), index + len(query) + 50)
                context = content[start:end]

                matches.append({
                    "path": str(md_file.relative_to(vault_root)),
                    "context": f"...{context}..."
                })

                if len(matches) >= limit:
                    break
        except:
            continue

    return {
        "query": query,
        "searched_area": area or "entire vault",
        "matches_found": len(matches),
        "matches": matches
    }


@tool
def analyze_strwbrry_folder() -> Dict:
    """
    Analyze the 80-Strwbrry folder to understand hopes, implementations, and outcomes.
    Returns structured data about user's self-declared goals and systems.
    """
    vault_root = _find_vault_root()
    if not vault_root:
        return {"error": "Vault not found"}

    strwbrry_path = vault_root / "80-89 - System" / "80 - Strwbrry"
    if not strwbrry_path.exists():
        return {"error": "Strwbrry folder not found"}

    result = {
        "hopes": [],
        "implementations": [],
        "what_worked": [],
        "what_didnt_work": []
    }

    # Look for key files
    key_files = {
        "hopes": "01 - Hopes",
        "implementations": "03 - Implementations",
        "worked": "05 - What Has Worked",
        "didnt_work": "06 - What Hasn't Worked"
    }

    for key, folder_name in key_files.items():
        folder_path = strwbrry_path / folder_name
        if folder_path.exists():
            md_files = list(folder_path.rglob("*.md"))
            result[key] = [
                {
                    "name": f.name,
                    "path": str(f.relative_to(vault_root)),
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d")
                }
                for f in md_files
            ]

    return {
        "strwbrry_analysis": result,
        "total_hopes": len(result["hopes"]),
        "total_implementations": len(result["implementations"]),
        "validated_worked": len(result["what_worked"]),
        "validated_failed": len(result["what_didnt_work"])
    }


@tool
def compare_areas(area1: str, area2: str, days: int = 30) -> Dict:
    """
    Compare activity between two vault areas.
    Useful for detecting stated vs actual priorities.

    Args:
        area1: First area name
        area2: Second area name
        days: Period to analyze

    Returns:
        Comparison data
    """
    vault_root = _find_vault_root()
    if not vault_root:
        return {"error": "Vault not found"}

    cutoff_time = (datetime.now() - timedelta(days=days)).timestamp()

    def get_area_stats(area_name):
        area_path = vault_root / area_name
        if not area_path.exists():
            return None

        md_files = list(area_path.rglob("*.md"))
        updated = [f for f in md_files if f.stat().st_mtime > cutoff_time]

        return {
            "total_files": len(md_files),
            "updated_files": len(updated),
            "update_rate": round(len(updated) / len(md_files) * 100, 1) if md_files else 0
        }

    stats1 = get_area_stats(area1)
    stats2 = get_area_stats(area2)

    if not stats1 or not stats2:
        return {"error": "One or both areas not found"}

    return {
        "period_days": days,
        area1: stats1,
        area2: stats2,
        "comparison": {
            "more_active": area1 if stats1["updated_files"] > stats2["updated_files"] else area2,
            "difference": abs(stats1["updated_files"] - stats2["updated_files"]),
            "ratio": round(stats1["updated_files"] / stats2["updated_files"], 2) if stats2["updated_files"] > 0 else "infinite"
        }
    }
