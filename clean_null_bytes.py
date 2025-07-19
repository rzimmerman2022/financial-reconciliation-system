#!/usr/bin/env python3
"""
Clean null bytes and normalize line endings in Python files.

This script:
1. Finds all .py files in the project (excluding .venv)
2. Removes null bytes (0x00 characters)
3. Converts CRLF to LF line endings
4. Creates backups before modifying files
5. Reports which files were cleaned
"""

import shutil
from pathlib import Path
from datetime import datetime
import argparse


def find_python_files(root_dir, exclude_dirs=None):
    """Find all Python files, excluding specified directories."""
    if exclude_dirs is None:
        exclude_dirs = {'.venv', '__pycache__', '.git', 'venv', 'env'}
    
    python_files = []
    root_path = Path(root_dir)
    
    for py_file in root_path.rglob('*.py'):
        # Check if file is in an excluded directory
        if any(excluded in py_file.parts for excluded in exclude_dirs):
            continue
        python_files.append(py_file)
    
    return python_files


def has_null_bytes(file_path):
    """Check if file contains null bytes."""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            return b'\x00' in content
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False


def has_crlf_endings(file_path):
    """Check if file has Windows line endings."""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            return b'\r\n' in content
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False


def has_bom(file_path):
    """Check if file has Byte Order Mark."""
    try:
        with open(file_path, 'rb') as f:
            content = f.read(3)  # Only need first 3 bytes to check for BOM
            return (content.startswith(b'\xef\xbb\xbf') or  # UTF-8 BOM
                    content.startswith(b'\xff\xfe') or      # UTF-16 LE BOM  
                    content.startswith(b'\xfe\xff'))        # UTF-16 BE BOM
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False


def create_backup(file_path, backup_dir):
    """Create a backup of the file."""
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(exist_ok=True)
    
    # Create a unique backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
    backup_path = backup_dir / backup_name
    
    shutil.copy2(file_path, backup_path)
    return backup_path


def clean_file(file_path, create_backup_flag=True):
    """Clean null bytes, BOM characters, and normalize line endings in a file."""
    changes_made = []
    
    try:
        # Read the file in binary mode
        with open(file_path, 'rb') as f:
            content = f.read()
        
        original_size = len(content)
        
        # Check for null bytes
        has_nulls = b'\x00' in content
        # Check for CRLF
        has_crlf = b'\r\n' in content
        # Check for BOM (UTF-8, UTF-16 LE, UTF-16 BE)
        has_bom = (content.startswith(b'\xef\xbb\xbf') or  # UTF-8 BOM
                   content.startswith(b'\xff\xfe') or      # UTF-16 LE BOM
                   content.startswith(b'\xfe\xff'))        # UTF-16 BE BOM
        
        if not has_nulls and not has_crlf and not has_bom:
            return changes_made  # No changes needed
        
        # Create backup if requested
        if create_backup_flag:
            backup_dir = file_path.parent / 'backups'
            backup_path = create_backup(file_path, backup_dir)
            print(f"Created backup: {backup_path}")
        
        # Remove BOM if present
        if has_bom:
            if content.startswith(b'\xef\xbb\xbf'):  # UTF-8 BOM
                content = content[3:]
                changes_made.append("Removed UTF-8 BOM")
            elif content.startswith(b'\xff\xfe'):    # UTF-16 LE BOM
                content = content[2:]
                # Convert from UTF-16 LE to UTF-8
                try:
                    text = content.decode('utf-16le')
                    content = text.encode('utf-8')
                    changes_made.append("Removed UTF-16 LE BOM and converted to UTF-8")
                except UnicodeDecodeError:
                    content = content[2:]  # Just remove BOM if decode fails
                    changes_made.append("Removed UTF-16 LE BOM")
            elif content.startswith(b'\xfe\xff'):    # UTF-16 BE BOM
                content = content[2:]
                # Convert from UTF-16 BE to UTF-8
                try:
                    text = content.decode('utf-16be')
                    content = text.encode('utf-8')
                    changes_made.append("Removed UTF-16 BE BOM and converted to UTF-8")
                except UnicodeDecodeError:
                    content = content[2:]  # Just remove BOM if decode fails
                    changes_made.append("Removed UTF-16 BE BOM")
        
        # Remove null bytes
        if has_nulls:
            null_count = content.count(b'\x00')
            content = content.replace(b'\x00', b'')
            changes_made.append(f"Removed {null_count} null bytes")
        
        # Convert CRLF to LF
        if has_crlf:
            crlf_count = content.count(b'\r\n')
            content = content.replace(b'\r\n', b'\n')
            changes_made.append(f"Converted {crlf_count} CRLF to LF")
        
        # Write the cleaned content back
        with open(file_path, 'wb') as f:
            f.write(content)
        
        new_size = len(content)
        if new_size != original_size:
            changes_made.append(f"Size changed: {original_size} → {new_size} bytes")
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return [f"ERROR: {e}"]
    
    return changes_made


def main():
    parser = argparse.ArgumentParser(description='Clean null bytes and normalize line endings in Python files')
    parser.add_argument('--root', default='.', help='Root directory to search (default: current directory)')
    parser.add_argument('--no-backup', action='store_true', help='Do not create backups')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--exclude', nargs='*', default=['.venv', '__pycache__', '.git', 'venv', 'env'], 
                        help='Directories to exclude')
    
    args = parser.parse_args()
    
    root_dir = Path(args.root).resolve()
    print(f"Cleaning Python files in: {root_dir}")
    print(f"Excluding directories: {args.exclude}")
    print("-" * 60)
    
    # Find all Python files
    python_files = find_python_files(root_dir, set(args.exclude))
    print(f"Found {len(python_files)} Python files")
    
    if not python_files:
        print("No Python files found!")
        return
    
    # Check which files need cleaning
    files_with_nulls = []
    files_with_crlf = []
    files_with_bom = []
    
    for py_file in python_files:
        if has_null_bytes(py_file):
            files_with_nulls.append(py_file)
        if has_crlf_endings(py_file):
            files_with_crlf.append(py_file)
        if has_bom(py_file):
            files_with_bom.append(py_file)
    
    print(f"\nFiles with null bytes: {len(files_with_nulls)}")
    for f in files_with_nulls:
        print(f"  - {f}")
    
    print(f"\nFiles with CRLF endings: {len(files_with_crlf)}")
    for f in files_with_crlf:
        print(f"  - {f}")
    
    print(f"\nFiles with BOM: {len(files_with_bom)}")
    for f in files_with_bom:
        print(f"  - {f}")
    
    files_to_clean = set(files_with_nulls + files_with_crlf + files_with_bom)
    
    if not files_to_clean:
        print("\n✅ No files need cleaning!")
        return
    
    print(f"\nTotal files to clean: {len(files_to_clean)}")
    
    if args.dry_run:
        print("\n🔍 DRY RUN - No changes will be made")
        return
    
    # Clean the files
    print("\n🧹 Cleaning files...")
    print("-" * 40)
    
    cleaned_count = 0
    error_count = 0
    
    for py_file in files_to_clean:
        print(f"\nProcessing: {py_file}")
        
        changes = clean_file(py_file, create_backup_flag=not args.no_backup)
        
        if changes:
            if any("ERROR" in change for change in changes):
                error_count += 1
                print(f"  ❌ {'; '.join(changes)}")
            else:
                cleaned_count += 1
                print(f"  ✅ {'; '.join(changes)}")
        else:
            print("  ℹ️  No changes needed")
    
    print(f"\n{'='*60}")
    print("SUMMARY:")
    print(f"  Files processed: {len(files_to_clean)}")
    print(f"  Files cleaned: {cleaned_count}")
    print(f"  Errors: {error_count}")
    
    if not args.no_backup and cleaned_count > 0:
        print(f"  Backups created in: {root_dir}/backups/")
    
    print("\n✅ Cleaning complete!")
    
    # Verify the cleaning worked
    print("\n🔍 Verifying cleanup...")
    remaining_nulls = [f for f in python_files if has_null_bytes(f)]
    if remaining_nulls:
        print(f"⚠️  {len(remaining_nulls)} files still have null bytes:")
        for f in remaining_nulls:
            print(f"  - {f}")
    else:
        print("✅ No null bytes remaining in any Python files!")


if __name__ == '__main__':
    main()
