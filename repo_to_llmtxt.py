import os
import json
import sys
import argparse
import markdown
from pathlib import Path
from typing import List, Dict, Optional, Any

def detect_project_type(repo_path: Path) -> Dict[str, Any]:
    """
    Analyze repository and detect project type based on key files.
    Returns project type and suggested files to extract.
    """
    project_types = {
        "nextjs": {
            "indicators": ["next.config.js", "next.config.mjs", "pages/_app.tsx", "app/layout.tsx"],
            "title": "Next.js Project",
            "files": [
                # Core structure
                "package.json",
                ".env.example",
                "next.config.js",
                "next.config.mjs",
                "app/layout.tsx",
                "app/page.tsx",
                "pages/_app.tsx",
                "pages/index.tsx",
                # Config files
                "tsconfig.json",
                "tailwind.config.js",
                "tailwind.config.ts",
                # Common component directories
                "components/layout", 
                "components/ui",
                "lib/utils.ts"
            ],
            "file_groups": ["Configuration", "Core Structure", "Components", "API Routes", "Utilities"]
        },
        "react": {
            "indicators": ["src/App.js", "src/App.tsx", "public/index.html"],
            "title": "React Project",
            "files": [
                "package.json",
                ".env",
                ".env.example",
                "public/index.html",
                "src/index.js",
                "src/index.tsx",
                "src/App.js",
                "src/App.tsx",
                "src/components"
            ],
            "file_groups": ["Configuration", "Core Structure", "Components", "Hooks", "Utilities"]
        },
        "python": {
            "indicators": ["setup.py", "requirements.txt", "pyproject.toml"],
            "title": "Python Project",
            "files": [
                "setup.py",
                "pyproject.toml",
                "requirements.txt",
                "README.md",
                "main.py",
                "app.py"
            ],
            "file_groups": ["Configuration", "Core Modules", "Utilities", "Tests"]
        },
        "monad-miniapp": {
            "indicators": ["components/farcaster-provider.tsx", "components/frame-wallet-provider.tsx"],
            "title": "Monad Mini-App Template",
            "files": [
                # Core app structure
                "app/page.tsx",
                "app/layout.tsx",
                "components/pages/app.tsx",
                ".env.example",
                # Providers and Context
                "components/farcaster-provider.tsx",
                "components/frame-wallet-provider.tsx",
                "hooks/use-miniapp-context.ts",
                # UI Components
                "components/Home/FarcasterActions.tsx",
                "components/Home/WalletActions.tsx",
                "components/Home/User.tsx",
                "components/Home/index.tsx",
                "components/safe-area-container.tsx",
                # Configuration and Utilities
                "app/.well-known/farcaster.json/route.ts",
                "lib/constants.ts",
                "lib/notifs.ts",
                "package.json",
                "next.config.mjs",
                "tailwind.config.ts",
                # Types
                "types/index.ts"
            ],
            "file_groups": ["Core Structure", "Providers and Context", "UI Components", "Configuration", "Utilities"]
        }
    }
    
    # Detect project type based on indicators
    for project_type, config in project_types.items():
        for indicator in config["indicators"]:
            if (repo_path / indicator).exists():
                return {
                    "type": project_type,
                    "title": config["title"],
                    "files": config["files"],
                    "file_groups": config["file_groups"]
                }
    
    # If no specific type is detected, return a generic configuration
    return {
        "type": "generic",
        "title": "Project Structure",
        "files": [
            "README.md",
            "package.json",
            "requirements.txt",
            ".env.example",
            "src",
            "lib"
        ],
        "file_groups": ["Documentation", "Configuration", "Source Code"]
    }


def find_files_by_pattern(repo_path: Path, patterns: List[str]) -> List[str]:
    """
    Find files in the repository matching the given patterns.
    Supports directory patterns which will include all files in that directory.
    """
    found_files = []
    for pattern in patterns:
        pattern_path = repo_path / pattern
        
        # If it's a directory, add all files recursively
        if pattern_path.is_dir():
            for root, _, files in os.walk(pattern_path):
                for file in files:
                    # Skip hidden files and common non-code files
                    if not file.startswith('.') and not file.endswith(('.pyc', '.map', '.DS_Store')):
                        file_path = Path(root) / file
                        rel_path = file_path.relative_to(repo_path)
                        found_files.append(str(rel_path))
        # If it's a direct file match
        elif pattern_path.exists():
            found_files.append(pattern)
        # Handle wildcard patterns (basic implementation)
        elif '*' in pattern:
            base_dir = Path(pattern).parent
            if base_dir == Path('.'):
                base_dir = repo_path
            else:
                base_dir = repo_path / base_dir
                
            if base_dir.exists():
                file_pattern = Path(pattern).name
                for file in base_dir.glob(file_pattern):
                    if file.is_file():
                        rel_path = file.relative_to(repo_path)
                        found_files.append(str(rel_path))
    
    return found_files


def extract_files(repo_path, target_files=None, output_file="llm.txt", markdown_file="repo_structure.md", project_title=None):
    """
    Extract content from specified files in the repository
    and create both a raw text file and a nicely formatted markdown file.
    
    Args:
        repo_path: Path to the repository
        target_files: List of files to extract. If None, will auto-detect.
        output_file: Output file for raw text
        markdown_file: Output file for markdown
        project_title: Title of the project. If None, will auto-detect.
    """
    # Ensure the repo path exists
    repo_path = Path(repo_path)
    if not repo_path.exists():
        print(f"Repository path {repo_path} does not exist!")
        return
    
    # Auto-detect project type if not specified
    if target_files is None:
        project_config = detect_project_type(repo_path)
        target_files = project_config["files"]
        if project_title is None:
            project_title = project_config["title"]
        file_groups = project_config["file_groups"]
    else:
        file_groups = ["Files"]
    
    # Set default title if not provided
    if project_title is None:
        project_title = "Project Structure"
    
    # Expand directory patterns in target_files
    expanded_files = find_files_by_pattern(repo_path, target_files)
    expanded_files = sorted(list(set(expanded_files)))  # Remove duplicates
    
    # Open the output files
    with open(output_file, "w", encoding="utf-8") as txt_file, \
         open(markdown_file, "w", encoding="utf-8") as md_file:
        
        # Write header to markdown file
        md_file.write(f"# {project_title}\n\n")
        md_file.write(f"This document contains key files from the project to help understand its structure.\n\n")
        
        # Add target_files list to both files
        txt_file.write("### KEY FILES IN PROJECT STRUCTURE ###\n\n")
        target_files_str = "\n".join([f"- {file}" for file in expanded_files])
        txt_file.write(f"{target_files_str}\n\n")
        
        md_file.write("## Key Files in Project Structure\n\n")
        md_file.write("```\n")
        md_file.write(target_files_str)
        md_file.write("\n```\n\n")
        
        # Look for each target file
        for file_path in expanded_files:
            full_path = repo_path / file_path
            
            if full_path.exists() and full_path.is_file():
                # Read the file content
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Write to raw txt file
                    txt_file.write(f"### FILE: {file_path} ###\n\n")
                    txt_file.write(content)
                    txt_file.write("\n\n")
                    
                    # Write to markdown file with syntax highlighting
                    md_file.write(f"## {file_path}\n\n")
                    
                    # Determine the language for syntax highlighting
                    extension = full_path.suffix.lstrip('.')
                    language_map = {
                        "js": "javascript",
                        "jsx": "jsx",
                        "ts": "typescript",
                        "tsx": "typescript",
                        "py": "python",
                        "rb": "ruby",
                        "java": "java",
                        "kt": "kotlin",
                        "go": "go",
                        "rs": "rust",
                        "c": "c",
                        "cpp": "cpp",
                        "cs": "csharp",
                        "php": "php",
                        "json": "json",
                        "yml": "yaml",
                        "yaml": "yaml",
                        "md": "markdown",
                        "html": "html",
                        "css": "css",
                        "scss": "scss",
                        "sql": "sql",
                        "sh": "bash",
                        "bash": "bash",
                        "zsh": "bash",
                        "toml": "toml",
                        "xml": "xml"
                    }
                    
                    language = language_map.get(extension, extension)
                    
                    md_file.write(f"```{language}\n{content}\n```\n\n")
                    
                    print(f"✅ Extracted: {file_path}")
                    
                except Exception as e:
                    print(f"❌ Error reading {file_path}: {e}")
            elif not full_path.exists():
                # File not found, note this in both outputs
                txt_file.write(f"### FILE: {file_path} - NOT FOUND ###\n\n")
                md_file.write(f"## {file_path}\n\n")
                md_file.write("*File not found in repository*\n\n")
                print(f"⚠️ Not found: {file_path}")
        
        # Generate project-specific architecture documentation if detected
        project_type = detect_project_type(repo_path)["type"]
        
        if project_type == "monad-miniapp":
            generate_monad_architecture_docs(md_file)
        elif project_type == "nextjs":
            generate_nextjs_architecture_docs(md_file)
        elif project_type == "react":
            generate_react_architecture_docs(md_file)
        else:
            generate_generic_architecture_docs(md_file, project_type)
        
        # Additionally, add directory structure to markdown file
        md_file.write("## Directory Structure\n\n")
        md_file.write("```\n")
        
        # Use os.walk to get a simplified directory structure
        for root, dirs, files in os.walk(repo_path, topdown=True):
            # Skip common directories to exclude
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '.next', '__pycache__', 'dist', 'build', 'target', 'venv', 'env']]
            
            level = root.replace(str(repo_path), '').count(os.sep)
            indent = ' ' * 4 * level
            relative_path = os.path.basename(root)
            if level > 0:  # Skip the root directory itself
                md_file.write(f"{indent}{relative_path}/\n")
        
        md_file.write("```\n")
        
    print(f"\nDone! Created {output_file} and {markdown_file}")


def generate_monad_architecture_docs(md_file):
    """Generate architecture documentation specific to Monad Mini-Apps."""
    md_file.write("## Application Architecture\n\n")
    md_file.write("### Overview\n\n")
    md_file.write("The Monad Mini-App Template is built with Next.js and integrates with Farcaster and wallet functionality. " +
                 "Here's a breakdown of how the components work together:\n\n")
    
    # Component relationships
    md_file.write("### Component Relationships\n\n")
    md_file.write("```\n")
    md_file.write("app/layout.tsx                 # Root layout with providers\n")
    md_file.write("  ├─ farcaster-provider.tsx   # Farcaster authentication context\n")
    md_file.write("  ├─ frame-wallet-provider.tsx # Wallet connection for Frames\n")
    md_file.write("  └─ app/page.tsx            # Entry point with Frame metadata\n")
    md_file.write("       └─ components/pages/app.tsx # Main application component\n")
    md_file.write("           └─ components/Home/* # UI components for user interaction\n")
    md_file.write("               ├─ FarcasterActions.tsx # Farcaster-specific actions\n")
    md_file.write("               ├─ WalletActions.tsx # Wallet connection and transactions\n")
    md_file.write("               └─ User.tsx    # User profile display\n")
    md_file.write("```\n\n")
    
    # Data flow explanation
    md_file.write("### Data Flow\n\n")
    md_file.write("1. **Authentication**: Handled by `farcaster-provider.tsx` using Farcaster authentication protocol\n")
    md_file.write("2. **Context Management**: `use-miniapp-context.ts` hook provides access to authenticated user and wallet\n")
    md_file.write("3. **Wallet Integration**: `frame-wallet-provider.tsx` enables connection to the user's wallet through Farcaster Frames\n")
    md_file.write("4. **UI Components**: Components in the Home directory leverage the context to display user info and enable interactions\n\n")
    
    # Getting Started guide
    md_file.write("## Getting Started\n\n")
    md_file.write("To set up this mini-app template:\n\n")
    md_file.write("1. Clone the repository\n")
    md_file.write("2. Install dependencies with `yarn install`\n")
    md_file.write("3. Copy `.env.example` to `.env.local` and update variables\n")
    md_file.write("4. Run the development server with `yarn dev`\n")
    md_file.write("5. Navigate to `http://localhost:3000` to view the app\n\n")
    md_file.write("For deployment, you'll need to set up the same environment variables in your hosting provider.\n\n")


def generate_nextjs_architecture_docs(md_file):
    """Generate architecture documentation specific to Next.js projects."""
    md_file.write("## Application Architecture\n\n")
    md_file.write("### Overview\n\n")
    md_file.write("This is a Next.js project that follows the App Router pattern. " +
                 "Here's a breakdown of the key architectural components:\n\n")
    
    # Component relationships
    md_file.write("### Directory Structure Explained\n\n")
    md_file.write("- **app/**: Contains the application routes and layouts using Next.js App Router\n")
    md_file.write("- **components/**: Reusable UI components organized by feature or page\n")
    md_file.write("- **lib/**: Utility functions, hooks, and configuration\n")
    md_file.write("- **public/**: Static assets like images, fonts, etc.\n\n")
    
    # Getting Started guide
    md_file.write("## Getting Started\n\n")
    md_file.write("To run this Next.js project:\n\n")
    md_file.write("1. Clone the repository\n")
    md_file.write("2. Install dependencies with `npm install` or `yarn install`\n")
    md_file.write("3. Run the development server with `npm run dev` or `yarn dev`\n")
    md_file.write("4. Open http://localhost:3000 in your browser\n\n")


def generate_react_architecture_docs(md_file):
    """Generate architecture documentation specific to React projects."""
    md_file.write("## Application Architecture\n\n")
    md_file.write("### Overview\n\n")
    md_file.write("This is a React application with a standard Create React App structure. " +
                 "The application is organized by features with a component-based architecture.\n\n")
    
    # Directory structure explanation
    md_file.write("### Directory Structure Explained\n\n")
    md_file.write("- **src/components/**: Reusable UI components\n")
    md_file.write("- **src/hooks/**: Custom React hooks\n")
    md_file.write("- **src/pages/**: Page components that represent routes\n")
    md_file.write("- **src/utils/**: Utility functions and helpers\n")
    md_file.write("- **public/**: Static assets and index.html\n\n")
    
    # Getting Started guide
    md_file.write("## Getting Started\n\n")
    md_file.write("To run this React project:\n\n")
    md_file.write("1. Clone the repository\n")
    md_file.write("2. Install dependencies with `npm install` or `yarn install`\n")
    md_file.write("3. Start the development server with `npm start` or `yarn start`\n")
    md_file.write("4. Open http://localhost:3000 in your browser\n\n")


def generate_generic_architecture_docs(md_file, project_type):
    """Generate generic architecture documentation for other project types."""
    md_file.write("## Project Overview\n\n")
    
    if project_type == "python":
        md_file.write("This is a Python project with the following structure:\n\n")
        md_file.write("- **Requirements**: See requirements.txt or pyproject.toml for dependencies\n")
        md_file.write("- **Project Organization**: The project follows standard Python module organization\n")
    else:
        md_file.write("This project contains the following key files and directories:\n\n")
        md_file.write("- **Configuration Files**: Setup and environment configuration\n")
        md_file.write("- **Source Code**: Core implementation files\n")
        md_file.write("- **Documentation**: Usage guides and API documentation\n")
    
    md_file.write("\nRefer to the directory structure and file contents for more details on the project organization.\n\n")


def main():
    """Main function to handle argument parsing and script execution."""
    parser = argparse.ArgumentParser(
        description="Extract key files from a repository into LLM-friendly formats."
    )
    parser.add_argument("repo_path", nargs="?", help="Path to the repository")
    parser.add_argument(
        "-o", "--output", default="llm.txt", help="Output text file (default: llm.txt)"
    )
    parser.add_argument(
        "-m", "--markdown", default="repo_structure.md", 
        help="Output markdown file (default: repo_structure.md)"
    )
    parser.add_argument(
        "-c", "--config", help="JSON configuration file with target files list"
    )
    parser.add_argument(
        "-t", "--title", help="Project title to use in documentation"
    )
    
    args = parser.parse_args()
    
    # If repo_path is not provided, prompt the user
    repo_path = args.repo_path
    if not repo_path:
        repo_path = input("Enter the path to the repository: ")
    
    # Load configuration if provided
    target_files = None
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
                target_files = config.get("files")
        except Exception as e:
            print(f"Error loading configuration file: {e}")
            sys.exit(1)
    
    # Extract files
    extract_files(
        repo_path=repo_path,
        target_files=target_files,
        output_file=args.output,
        markdown_file=args.markdown,
        project_title=args.title
    )


if __name__ == "__main__":
    main()
