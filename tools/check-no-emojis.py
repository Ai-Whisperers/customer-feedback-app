#!/usr/bin/env python3
"""
CRITICAL PROJECT RULE ENFORCER: NO EMOJIS ALLOWED

This script enforces the strict no-emoji policy across the entire codebase.
It's designed to be used as a pre-commit hook and CI check.

Usage:
    python tools/check-no-emojis.py file1.py file2.ts file3.md

Exit codes:
    0: No emojis found (success)
    1: Emojis detected (failure)
    2: Script error
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Optional


# Comprehensive emoji unicode ranges
EMOJI_PATTERNS = [
    r'[\U0001F600-\U0001F64F]',  # Emoticons
    r'[\U0001F300-\U0001F5FF]',  # Symbols & Pictographs
    r'[\U0001F680-\U0001F6FF]',  # Transport & Map Symbols
    r'[\U0001F700-\U0001F77F]',  # Alchemical Symbols
    r'[\U0001F780-\U0001F7FF]',  # Geometric Shapes Extended
    r'[\U0001F800-\U0001F8FF]',  # Supplemental Arrows-C
    r'[\U0001F900-\U0001F9FF]',  # Supplemental Symbols and Pictographs
    r'[\U0001FA00-\U0001FA6F]',  # Chess Symbols
    r'[\U0001FA70-\U0001FAFF]',  # Symbols and Pictographs Extended-A
    r'[\U00002600-\U000026FF]',  # Miscellaneous Symbols
    r'[\U00002700-\U000027BF]',  # Dingbats
    r'[\U0000FE00-\U0000FE0F]',  # Variation Selectors
    r'[\U00002000-\U0000206F]',  # General Punctuation (some emoji modifiers)
    # Regional indicator symbols (flag emojis)
    r'[\U0001F1E6-\U0001F1FF]{2}',
    # Keycap sequences
    r'[\U00000030-\U00000039]\U0000FE0F?\U000020E3',
    r'[\U0000002A\U00000023]\U0000FE0F?\U000020E3',
]

# Compile regex pattern
EMOJI_REGEX = re.compile('|'.join(EMOJI_PATTERNS))

# File extensions to check
CHECKED_EXTENSIONS = {
    '.py', '.ts', '.tsx', '.js', '.jsx', '.md', '.txt',
    '.json', '.yaml', '.yml', '.html', '.css', '.scss',
    '.toml', '.ini', '.cfg', '.conf'
}

# Files to always skip
SKIP_FILES = {
    '.git',
    'node_modules',
    '__pycache__',
    '.venv',
    'venv',
    'env',
    'build',
    'dist',
    '.tox',
    'coverage',
    '.coverage',
    '.pytest_cache',
    '.mypy_cache',
}


def should_check_file(file_path: Path) -> bool:
    """Determine if a file should be checked for emojis."""
    # Skip directories in SKIP_FILES
    if any(skip in file_path.parts for skip in SKIP_FILES):
        return False

    # Check file extension
    return file_path.suffix.lower() in CHECKED_EXTENSIONS


def find_emojis_in_file(file_path: Path) -> List[Tuple[int, str, str]]:
    """
    Find all emojis in a file.

    Returns:
        List of tuples: (line_number, line_content, emoji_found)
    """
    emojis_found = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                # Find all emoji matches in the line
                for match in EMOJI_REGEX.finditer(line):
                    emoji = match.group()
                    emojis_found.append((line_num, line.strip(), emoji))

    except (UnicodeDecodeError, IOError) as e:
        print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)

    return emojis_found


def check_files(files: List[Path], verbose: bool = False) -> Tuple[bool, int]:
    """
    Check multiple files for emojis.

    Returns:
        Tuple of (has_emojis, total_emoji_count)
    """
    total_emojis = 0
    has_any_emojis = False

    for file_path in files:
        if not file_path.exists():
            if verbose:
                print(f"Skipping non-existent file: {file_path}")
            continue

        if not should_check_file(file_path):
            if verbose:
                print(f"Skipping file (not in scope): {file_path}")
            continue

        emojis = find_emojis_in_file(file_path)

        if emojis:
            has_any_emojis = True
            total_emojis += len(emojis)

            print(f"\nCRITICAL EMOJI POLICY VIOLATION in {file_path}:")
            print("=" * 60)

            for line_num, line_content, emoji in emojis:
                print(f"Line {line_num:4d}: {emoji} in '{line_content}'")
                print(f"             Unicode: {ord(emoji):04X} ({emoji!r})")

            print(f"\nTotal emojis in this file: {len(emojis)}")

        elif verbose:
            print(f"CLEAN: {file_path}")

    return has_any_emojis, total_emojis


def main():
    """Main entry point for the emoji checker."""
    parser = argparse.ArgumentParser(
        description="Check files for emoji usage (CRITICAL PROJECT RULE)",
        epilog="This tool enforces the strict no-emoji policy for the project."
    )
    parser.add_argument(
        'files',
        nargs='*',
        help='Files to check (if none provided, checks all relevant files)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--check-all',
        action='store_true',
        help='Check all files in the project'
    )

    args = parser.parse_args()

    if args.check_all:
        # Find all relevant files in the project
        project_root = Path.cwd()
        files_to_check = []

        for pattern in ['**/*' + ext for ext in CHECKED_EXTENSIONS]:
            files_to_check.extend(project_root.glob(pattern))

        files_to_check = [f for f in files_to_check if should_check_file(f)]

    elif args.files:
        files_to_check = [Path(f) for f in args.files]
    else:
        print("No files specified. Use --check-all to check entire project.")
        return 0

    if args.verbose:
        print(f"Checking {len(files_to_check)} files for emoji violations...")
        print("Emoji patterns covered: Emoticons, Symbols, Transport, Flags, etc.")
        print()

    has_emojis, total_count = check_files(files_to_check, args.verbose)

    if has_emojis:
        print(f"\n{'='*60}")
        print("CRITICAL PROJECT RULE VIOLATION")
        print(f"{'='*60}")
        print(f"Found {total_count} emoji(s) across {len(files_to_check)} files checked.")
        print()
        print("PROJECT POLICY: NO EMOJIS ARE ALLOWED IN THE CODEBASE")
        print()
        print("Action required:")
        print("1. Remove all emojis from the flagged files")
        print("2. Use descriptive text instead of emojis")
        print("3. For UI elements, use icon libraries or text representations")
        print("4. For documentation, use clear text formatting")
        print()
        print("This policy is enforced to maintain:")
        print("- Professional code standards")
        print("- Cross-platform compatibility")
        print("- Clear communication")
        print("- Consistent project aesthetics")

        return 1

    else:
        if args.verbose:
            print(f"\nSUCCESS: All {len(files_to_check)} files are emoji-free!")
            print("Project policy compliance: PASSED")

        return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)