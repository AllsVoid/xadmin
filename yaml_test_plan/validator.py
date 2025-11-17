"""
Smart YAML Validator - Detects common YAML syntax errors
"""

import yaml
from typing import Dict, List, Any, Tuple

try:
    from yamllint import linter
    from yamllint.config import YamlLintConfig
    YAMLLINT_AVAILABLE = True
except ImportError:
    YAMLLINT_AVAILABLE = False


def validate_yaml_syntax(yaml_content: str) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Comprehensive YAML syntax validation
    
    Returns:
        Tuple of (is_valid, error_list)
        Each error is a dict with 'line', 'column', 'message'
    """
    errors = []
    lines = yaml_content.split('\n')
    
    # Track syntax errors that may cause cascading issues
    syntax_error_lines = set()  # Lines with missing colons
    
    # Track list items and their expected indentation
    list_item_lines = {}  # line_num -> indent level
    
    for line_num, line in enumerate(lines, 1):
        if not line.strip() or line.strip().startswith('#'):
            continue
        
        indent = len(line) - len(line.lstrip())
        content = line.strip()
        
        # Rule 1: Check for missing colons (e.g., "type debian" should be "type: debian")
        if not content.startswith('-') and ' ' in content and ':' not in content:
            # Skip if it's part of a multiline value
            parts = content.split(' ', 1)
            if len(parts) == 2 and not parts[1].startswith('#'):
                # Check if this looks like a key-value pair
                if not any(c in parts[0] for c in ['[', ']', '{', '}', ',']):
                    syntax_error_lines.add(line_num)
                    errors.append({
                        'line': line_num,
                        'column': len(parts[0]) + 1,
                        'message': f"syntax error: could not find expected ':'"
                    })
        
        # Rule 1b: Check for single word keys without colons (e.g., "selected_components" → "selected_components:")
        if (not content.startswith('-') and ' ' not in content and ':' not in content 
            and '[]' not in content and content and not content.startswith('#')):
            # Check if next line is indented more (this is a parent key)
            if line_num < len(lines):
                next_line = lines[line_num]
                next_content = next_line.strip()
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # If next line exists, is not empty/comment, and is more indented
                if next_content and not next_content.startswith('#') and next_indent > indent:
                    syntax_error_lines.add(line_num)
                    errors.append({
                        'line': line_num,
                        'column': len(content) + 1,
                        'message': f"syntax error: could not find expected ':' (missing colon after '{content}')"
                    })
        
        # Rule 2: Track list items (lines starting with '- ')
        if content.startswith('- '):
            list_item_lines[line_num] = indent
            
            # If the list item has inline key-value (e.g., "- id: 102")
            if ':' in content[2:]:
                # Next lines should be indented at least 2 spaces more than the '-'
                expected_indent = indent + 2
                
                # Collect all sibling keys within this list item
                sibling_keys = []
                for next_line_num in range(line_num + 1, len(lines) + 1):
                    if next_line_num > len(lines):
                        break
                    
                    next_line = lines[next_line_num - 1]
                    next_content = next_line.strip()
                    
                    if not next_content or next_content.startswith('#'):
                        continue
                    
                    next_indent = len(next_line) - len(next_line.lstrip())
                    
                    # If we encounter another list item at SAME indentation, stop (it's a sibling list item, NOT an error)
                    if next_content.startswith('-') and next_indent == indent:
                        break
                    
                    # If we encounter a less indented key, stop (we've exited this list item)
                    if ':' in next_content and not next_content.startswith('-') and next_indent < indent:
                        break
                    
                    # If this line is a key within the list item (not starting with '-')
                    if ':' in next_content and not next_content.startswith('-'):
                        # It should be indented at least expected_indent
                        if next_indent < expected_indent:
                            sibling_keys.append(next_line_num)
                
                # Report error for the group of sibling keys
                # But only if there's no syntax error above that could cause this
                if sibling_keys:
                    first_line = sibling_keys[0]
                    last_line = sibling_keys[-1]
                    actual_indent = len(lines[first_line - 1]) - len(lines[first_line - 1].lstrip())
                    
                    # Check if there's a syntax error in recent lines that could cause this
                    has_recent_syntax_error = any(
                        err_line in syntax_error_lines and err_line < first_line and first_line - err_line < 100
                        for err_line in syntax_error_lines
                    )
                    
                    # Only report if not likely caused by a syntax error above
                    if not has_recent_syntax_error:
                        if len(sibling_keys) > 1:
                            errors.append({
                                'line': first_line,
                                'column': 1,
                                'message': f"wrong indentation in lines {first_line}-{last_line}: expected {expected_indent} but found {actual_indent}"
                            })
                        else:
                            errors.append({
                                'line': first_line,
                                'column': 1,
                                'message': f"wrong indentation: expected {expected_indent} but found {actual_indent}"
                            })
        
        # Rule 3: Check for list items that should not have '-' prefix
        if content.startswith('- ') and ':' in content:
            # Check if next line is indented and contains keys
            if line_num < len(lines):
                next_line = lines[line_num]
                next_content = next_line.strip()
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # If next line is a key (not a list item) and more indented
                if next_content and ':' in next_content and not next_content.startswith('-'):
                    if next_indent > indent and next_indent > indent + 2:
                        # This suggests the current line should not be a list item
                        key_part = content[2:].split(':')[0]
                        errors.append({
                            'line': line_num,
                            'column': 1,
                            'message': f"syntax error: could not find expected ':' (should be '{key_part}:' without '-')"
                        })
        
        # Rule 4: Check for keys with missing values that should have explicit empty list
        if ':' in content and not content.startswith('-'):
            key_part = content.split(':')[0].strip()
            value_part = content.split(':', 1)[1].strip()
            
            # If value is empty, check next line
            if not value_part:
                # Look at next line
                if line_num < len(lines):
                    next_line = lines[line_num]
                    next_content = next_line.strip()
                    next_indent = len(next_line) - len(next_line.lstrip())
                    
                    # If next line is a sibling key (same or less indent), current key has empty value
                    if next_content and ':' in next_content and not next_content.startswith('-'):
                        if next_indent <= indent:
                            # Check if this key typically should have a value or []
                            if key_part in ['machines', 'firmware', 'kernel_drivers', 'ras_reliability_tools']:
                                errors.append({
                                    'line': line_num,
                                    'column': len(key_part) + 2,
                                    'message': f"empty value for '{key_part}' (should be explicit empty list '[]' or nested content)"
                                })
    
    # Use yamllint for additional syntax checks (not indentation)
    if YAMLLINT_AVAILABLE:
        config = YamlLintConfig('''
extends: default
rules:
  line-length: disable
  comments: disable
  document-start: disable
  document-end: disable
  trailing-spaces: disable
  new-line-at-end-of-file: disable
  empty-lines: disable
  new-lines: disable
  indentation: disable
''')
        yamllint_problems = linter.run(yaml_content, config)
        
        for problem in yamllint_problems:
            # Only add syntax errors, not indentation (we handle that above)
            if 'indentation' not in problem.message.lower():
                errors.append({
                    'line': problem.line,
                    'column': problem.column,
                    'message': problem.message
                })
    
    # Sort by line number
    errors.sort(key=lambda x: x['line'])
    
    # Advanced deduplication:
    # If we have "wrong indentation in lines X-Y", remove individual line errors for X+1 to Y
    range_errors = [e for e in errors if 'in lines' in e['message']]
    line_ranges_to_skip = set()
    
    for err in range_errors:
        # Extract range from message like "wrong indentation in lines 22-26"
        import re
        match = re.search(r'in lines (\d+)-(\d+)', err['message'])
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            # Skip individual errors for lines start+1 to end
            for line in range(start + 1, end + 1):
                line_ranges_to_skip.add(line)
    
    # Remove duplicates and lines covered by range errors
    seen = set()
    unique_errors = []
    for err in errors:
        # Skip if this line is covered by a range error
        if err['line'] in line_ranges_to_skip:
            continue
        
        # Skip duplicates
        key = (err['line'], err['message'])
        if key not in seen:
            seen.add(key)
            unique_errors.append(err)
    
    return (len(unique_errors) == 0, unique_errors)


# Alias for compatibility
validate_yaml_full = validate_yaml_syntax

