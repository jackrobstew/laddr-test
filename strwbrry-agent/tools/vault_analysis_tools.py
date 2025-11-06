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
def read_recent_journals(days: int = 7, area: str = "10-19 - Living", preview_chars: int = 2000) -> Dict:
    """
    Read recent journal entries to understand current state.

    Args:
        days: Number of days to look back
        area: Journal area (default: 10-19 - Living)
        preview_chars: Number of characters to include in preview (default: 2000)

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

    # Try to find journal folder - check multiple possible locations
    current_year = datetime.now().year
    possible_paths = [
        area_path / "10 - Daily Journal" / f"10.10 - Daily Journal - {current_year}",
        area_path / "10 - Daily Journal" / f"10.10 - Daily Journal - {current_year - 1}",  # Previous year
        area_path / "10 - Daily Journal",
        area_path,  # Fallback to area root
    ]

    journal_path = None
    for path in possible_paths:
        if path.exists():
            journal_path = path
            break

    if not journal_path:
        return {
            "error": "Daily journal folder not found",
            "searched": str(area_path),
            "tried_paths": [str(p) for p in possible_paths]
        }

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

        # Read preview with better error handling
        try:
            content = journal_file.read_text(encoding='utf-8')
            preview = content[:preview_chars] + "..." if len(content) > preview_chars else content
            word_count = len(content.split())
        except UnicodeDecodeError:
            try:
                content = journal_file.read_text(encoding='latin-1')
                preview = content[:preview_chars] + "..."
                word_count = len(content.split())
            except Exception as e:
                preview = f"[Could not read content: {type(e).__name__}]"
                word_count = 0
        except Exception as e:
            preview = f"[Could not read content: {type(e).__name__}]"
            word_count = 0

        journal_entries.append({
            "date": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d"),
            "name": journal_file.name,
            "size_kb": round(stat.st_size / 1024, 2),
            "preview": preview,
            "word_count": word_count
        })

    return {
        "period_days": days,
        "entries_found": len(journal_entries),
        "entries": journal_entries,
        "journal_path_used": str(journal_path)
    }


@tool
def search_vault_content(query: str, area: Optional[str] = None, limit: int = 10, max_files: int = 500) -> Dict:
    """
    Search for specific content across vault (or specific area).

    Args:
        query: Search term
        area: Optional area to restrict search
        limit: Max results to return
        max_files: Maximum files to scan (default: 500)

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
    md_files = list(search_path.rglob("*.md"))[:max_files]
    files_searched = len(md_files)
    errors = 0

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8').lower()
            if query.lower() in content:
                # Get context around match (larger window)
                index = content.find(query.lower())
                start = max(0, index - 100)
                end = min(len(content), index + len(query) + 100)
                context = content[start:end].strip()

                matches.append({
                    "path": str(md_file.relative_to(vault_root)),
                    "context": f"...{context}...",
                    "modified": datetime.fromtimestamp(md_file.stat().st_mtime).strftime("%Y-%m-%d")
                })

                if len(matches) >= limit:
                    break
        except UnicodeDecodeError:
            errors += 1
            continue
        except Exception:
            errors += 1
            continue

    return {
        "query": query,
        "searched_area": area or "entire vault",
        "matches_found": len(matches),
        "matches": matches,
        "files_searched": files_searched,
        "errors": errors
    }


@tool
def analyze_strwbrry_folder() -> Dict:
    """
    Analyze the 80-Strwbrry folder to understand hopes, implementations, and outcomes.
    Returns structured data about user's self-declared goals and systems.
    Tries multiple possible folder names to be resilient.
    """
    vault_root = _find_vault_root()
    if not vault_root:
        return {"error": "Vault not found"}

    # Try multiple possible paths for Strwbrry folder
    possible_system_areas = ["80-89 - System", "80 - System", "System"]
    possible_strwbrry_names = ["80 - Strwbrry", "80.00 - Strwbrry", "Strwbrry"]

    strwbrry_path = None
    for system_area in possible_system_areas:
        for strwbrry_name in possible_strwbrry_names:
            test_path = vault_root / system_area / strwbrry_name
            if test_path.exists():
                strwbrry_path = test_path
                break
        if strwbrry_path:
            break

    if not strwbrry_path:
        # Try direct strwbrry folder
        for strwbrry_name in possible_strwbrry_names:
            test_path = vault_root / strwbrry_name
            if test_path.exists():
                strwbrry_path = test_path
                break

    if not strwbrry_path:
        return {
            "error": "Strwbrry folder not found",
            "tried_paths": [
                f"{sa}/{sn}" for sa in possible_system_areas for sn in possible_strwbrry_names
            ]
        }

    result = {
        "hopes": [],
        "implementations": [],
        "what_worked": [],
        "what_didnt_work": []
    }

    # Look for key folders with flexible naming
    key_folders_variants = {
        "hopes": ["01 - Hopes", "Hopes", "01-Hopes"],
        "implementations": ["03 - Implementations", "Implementations", "03-Implementations"],
        "what_worked": ["05 - What Has Worked", "What Has Worked", "05-What Has Worked"],
        "what_didnt_work": ["06 - What Hasn't Worked", "What Hasn't Worked", "06-What Hasn't Worked"]
    }

    for key, folder_variants in key_folders_variants.items():
        for folder_name in folder_variants:
            folder_path = strwbrry_path / folder_name
            if folder_path.exists():
                md_files = list(folder_path.rglob("*.md"))
                result[key] = [
                    {
                        "name": f.name,
                        "path": str(f.relative_to(vault_root)),
                        "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d"),
                        "size_kb": round(f.stat().st_size / 1024, 2)
                    }
                    for f in md_files
                ]
                break  # Found the folder, stop trying variants

    return {
        "strwbrry_analysis": result,
        "total_hopes": len(result["hopes"]),
        "total_implementations": len(result["implementations"]),
        "validated_worked": len(result["what_worked"]),
        "validated_failed": len(result["what_didnt_work"]),
        "strwbrry_path_used": str(strwbrry_path)
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
