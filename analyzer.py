import subprocess
import re
import os

def analyze_code(file_path):

    extension = os.path.splitext(file_path)[1]
    score = 0.0
    issues = []

    # --- Python Analysis ---
    if extension == ".py":
        # Pylint
        try:
            pylint_result = subprocess.run(
                ['pylint', file_path, '--output-format=text'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            for line in pylint_result.stdout.splitlines():
                match = re.search(r'Your code has been rated at ([\d\.]+)/10', line)
                if match:
                    score = float(match.group(1))
                elif line.strip().startswith(file_path):
                    parts = line.strip().split(':')
                    if len(parts) >= 4:
                        issues.append({
                            "tool": "pylint",
                            "line": int(parts[1].strip()),
                            "description": ":".join(parts[3:]).strip()
                        })
        except subprocess.SubprocessError as e:
            print("[Pylint Error]", e)

        # Flake8
        try:
            flake8_result = subprocess.run(
                ['flake8', file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            for line in flake8_result.stdout.strip().splitlines():
                parts = line.strip().split(":")
                if len(parts) >= 4:
                    issues.append({
                        "tool": "flake8",
                        "line": int(parts[1].strip()),
                        "description": parts[3].strip()
                    })
        except subprocess.SubprocessError as e:
            print("[Flake8 Error]", e)

    # --- C++ Analysis ---
    elif extension in [".cpp", ".cc", ".cxx", ".c"]:
        try:
            cppcheck_result = subprocess.run(
                ['cppcheck', '--enable=all', '--quiet', file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            for line in cppcheck_result.stderr.splitlines():
                parts = line.strip().split(":")
                if len(parts) >= 4:
                    issues.append({
                        "tool": "cppcheck",
                        "line": int(parts[1].strip()),
                        "description": ":".join(parts[3:]).strip()
                    })
        except subprocess.SubprocessError as e:
            print("[Cppcheck Error]", e)

    # --- Java Analysis ---
    elif extension == ".java":
        try:
            # Requires checkstyle jar and XML config (you can modify path)
            checkstyle_result = subprocess.run(
                ['java', '-jar', 'checkstyle.jar', '-c', 'google_checks.xml', file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            for line in checkstyle_result.stdout.strip().splitlines():
                parts = line.strip().split(":")
                if len(parts) >= 4 and parts[1].strip().isdigit():
                    issues.append({
                        "tool": "checkstyle",
                        "line": int(parts[1].strip()),
                        "description": ":".join(parts[3:]).strip()
                    })
        except subprocess.SubprocessError as e:
            print("[Checkstyle Error]", e)

    return {
        "score": round(score, 2),
        "bug_count": len(issues),
        "issues": sorted(issues, key=lambda x: x["line"])
    }
