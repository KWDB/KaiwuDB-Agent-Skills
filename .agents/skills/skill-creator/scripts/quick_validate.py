#!/usr/bin/env python3
"""Quick validation script for skills."""

import re
import sys
from pathlib import Path


ALLOWED_PROPERTIES = {"name", "description", "metadata"}
NAME_PATTERN = re.compile(r"^[a-z0-9-]+$")
FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
INTERNAL_METADATA_PATTERN = re.compile(r"^internal:\s*true\s*$", re.MULTILINE)


def _parse_frontmatter(frontmatter_text):
    """Parse the limited frontmatter shape used by local skills."""
    data = {}
    current_key = None

    for raw_line in frontmatter_text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue

        if line.startswith("  "):
            if current_key != "metadata":
                return None, f"Unexpected indented line in frontmatter: {line.strip()}"
            continue

        key, sep, value = line.partition(":")
        if not sep:
            return None, f"Invalid frontmatter line: {line}"

        key = key.strip()
        value = value.strip()

        if key == "metadata":
            current_key = key
            metadata = {}
            if value:
                return None, "Metadata must be expressed as an indented mapping"

            metadata_match = INTERNAL_METADATA_PATTERN.search(frontmatter_text)
            if metadata_match:
                metadata["internal"] = True
            data[key] = metadata
            continue

        current_key = key
        data[key] = value

    return data, None

def validate_skill(skill_path):
    """Basic validation of a skill"""
    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    # Read and validate frontmatter
    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "No YAML frontmatter found"

    # Extract frontmatter
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)
    if len(frontmatter_text) > 1024:
        return False, "Frontmatter is too long. Maximum is 1024 characters."

    frontmatter, parse_error = _parse_frontmatter(frontmatter_text)
    if parse_error:
        return False, parse_error
    if not isinstance(frontmatter, dict):
        return False, "Frontmatter must be a YAML dictionary"

    # Check for unexpected properties
    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        return False, (
            f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    # Check required fields
    if 'name' not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if 'description' not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    # Extract name for validation
    name = frontmatter.get('name', '')
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if not name:
        return False, "Name cannot be empty"
    if not NAME_PATTERN.match(name):
        return False, f"Name '{name}' should be hyphen-case (lowercase letters, digits, and hyphens only)"
    if name.startswith('-') or name.endswith('-') or '--' in name:
        return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
    if len(name) > 64:
        return False, f"Name is too long ({len(name)} characters). Maximum is 64 characters."

    # Extract and validate description
    description = frontmatter.get('description', '')
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if not description:
        return False, "Description cannot be empty"
    if '<' in description or '>' in description:
        return False, "Description cannot contain angle brackets (< or >)"
    if len(description) > 1024:
        return False, f"Description is too long ({len(description)} characters). Maximum is 1024 characters."
    if not description.startswith("Use when"):
        return False, "Description must start with 'Use when' and describe the trigger conditions."

    metadata = frontmatter.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, dict):
            return False, "Metadata must be a mapping"
        unexpected_metadata_keys = set(metadata.keys()) - {"internal"}
        if unexpected_metadata_keys:
            return False, (
                "Unexpected key(s) in metadata: "
                f"{', '.join(sorted(unexpected_metadata_keys))}. Allowed properties are: internal"
            )
        internal = metadata.get("internal")
        if internal is not None and internal is not True:
            return False, "metadata.internal must be true when provided"

    return True, "Skill is valid!"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)
    
    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
