#!/usr/bin/env python3
"""Skill initializer for lean, design-first skill scaffolds."""

import sys
from pathlib import Path


SKILL_TEMPLATE = """---
name: {skill_name}
description: Use when [TODO: describe the specific prompts, situations, or symptoms that should trigger this skill].
---

# {skill_title}

## Overview

[TODO: describe the job this skill does in 1-2 sentences.]

## Workflow

1. [TODO: first action after activation]
2. [TODO: main execution step]
3. [TODO: validation or finish step]

## Guardrails

- [TODO: boundary or safety rule]
- [TODO: what not to do]

## References

- Read `references/domain-notes.md` when domain rules or examples are needed.
- Read `references/activation-design.md` when refining triggers or fixing false activations.
"""

DOMAIN_NOTES_TEMPLATE = """# Domain Notes

Use this file for detailed rules, examples, schemas, API notes, or decision tables that do not belong in `SKILL.md`.

## Stable Facts

- [TODO]

## Key Examples

- [TODO]

## Edge Cases

- [TODO]
"""

ACTIVATION_DESIGN_TEMPLATE = """# Activation Design

## Trigger Prompts

- [TODO]

## Non-Trigger Prompts

- [TODO]

## False Positives

- Risk:
- Mitigation:

## False Negatives

- Risk:
- Mitigation:

## First Action After Activation

- [TODO]
"""


def title_case_skill_name(skill_name):
    """Convert hyphenated skill name to Title Case for display."""
    return ' '.join(word.capitalize() for word in skill_name.split('-'))


def init_skill(skill_name, path):
    """
    Initialize a new skill directory with template SKILL.md.

    Args:
        skill_name: Name of the skill
        path: Path where the skill directory should be created

    Returns:
        Path to created skill directory, or None if error
    """
    # Determine skill directory path
    skill_dir = Path(path).resolve() / skill_name

    # Check if directory already exists
    if skill_dir.exists():
        print(f"❌ Error: Skill directory already exists: {skill_dir}")
        return None

    # Create skill directory
    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        print(f"✅ Created skill directory: {skill_dir}")
    except Exception as e:
        print(f"❌ Error creating directory: {e}")
        return None

    # Create SKILL.md from template
    skill_title = title_case_skill_name(skill_name)
    skill_content = SKILL_TEMPLATE.format(
        skill_name=skill_name,
        skill_title=skill_title
    )

    skill_md_path = skill_dir / 'SKILL.md'
    try:
        skill_md_path.write_text(skill_content)
        print("✅ Created SKILL.md")
    except Exception as e:
        print(f"❌ Error creating SKILL.md: {e}")
        return None

    # Create lean reference scaffolding
    try:
        references_dir = skill_dir / 'references'
        references_dir.mkdir(exist_ok=True)
        domain_notes = references_dir / 'domain-notes.md'
        domain_notes.write_text(DOMAIN_NOTES_TEMPLATE)
        print("✅ Created references/domain-notes.md")

        activation_design = references_dir / 'activation-design.md'
        activation_design.write_text(ACTIVATION_DESIGN_TEMPLATE)
        print("✅ Created references/activation-design.md")
    except Exception as e:
        print(f"❌ Error creating resource directories: {e}")
        return None

    # Print next steps
    print(f"\n✅ Skill '{skill_name}' initialized successfully at {skill_dir}")
    print("\nNext steps:")
    print("1. Define trigger prompts, non-goals, and success criteria in references/activation-design.md")
    print("2. Capture reusable domain rules in references/domain-notes.md")
    print("3. Replace the TODOs in SKILL.md with the minimal runtime protocol")
    print("4. Add scripts/ or assets/ only if they solve a concrete repeated task")
    print("5. Run the validator when ready to check the skill structure")

    return skill_dir


def main():
    if len(sys.argv) < 4 or sys.argv[2] != '--path':
        print("Usage: init_skill.py <skill-name> --path <path>")
        print("\nSkill name requirements:")
        print("  - Hyphen-case identifier (e.g., 'data-analyzer')")
        print("  - Lowercase letters, digits, and hyphens only")
        print("  - Max 64 characters")
        print("  - Must match directory name exactly")
        print("\nExamples:")
        print("  init_skill.py my-new-skill --path skills/public")
        print("  init_skill.py my-api-helper --path skills/private")
        print("  init_skill.py custom-skill --path /custom/location")
        sys.exit(1)

    skill_name = sys.argv[1]
    path = sys.argv[3]

    print(f"🚀 Initializing skill: {skill_name}")
    print(f"   Location: {path}")
    print()

    result = init_skill(skill_name, path)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
