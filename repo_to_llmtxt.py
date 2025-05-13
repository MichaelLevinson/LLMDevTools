import os
import markdown
from pathlib import Path

# List of files we're interested in
target_files = [
    # Core app structure
    "app/page.tsx",
    "components/pages/app.tsx",
    ".env.example",
    
    # Context/SDK integration
    "components/context/MiniAppContext.tsx",
    "components/Home/FarcasterActions.tsx",
    "components/Home/WalletActions.tsx",
    
    # Configuration
    "app/.well-known/farcaster.json/route.ts",
    "package.json",
    
    # Example components
    "components/Home/User.tsx"
]

def extract_files(repo_path, output_file="llm.txt", markdown_file="repo_structure.md"):
    """
    Extract content from specified files in the repository
    and create both a raw text file and a nicely formatted markdown file.
    """
    # Ensure the repo path exists
    repo_path = Path(repo_path)
    if not repo_path.exists():
        print(f"Repository path {repo_path} does not exist!")
        return
    
    # Open the output files
    with open(output_file, "w", encoding="utf-8") as txt_file, \
         open(markdown_file, "w", encoding="utf-8") as md_file:
        
        # Write header to markdown file
        md_file.write("# Monad Mini-App Template Structure\n\n")
        md_file.write("This document contains key files from the Monad Mini-App Template to help understand its structure.\n\n")
        
        # Look for each target file
        for file_path in target_files:
            full_path = repo_path / file_path
            
            if full_path.exists():
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
                    if extension == "tsx" or extension == "ts":
                        language = "typescript"
                    elif extension == "json":
                        language = "json"
                    elif extension == "md":
                        language = "markdown"
                    else:
                        language = extension
                    
                    md_file.write(f"```{language}\n{content}\n```\n\n")
                    
                    print(f"✅ Extracted: {file_path}")
                    
                except Exception as e:
                    print(f"❌ Error reading {file_path}: {e}")
            else:
                # File not found, note this in both outputs
                txt_file.write(f"### FILE: {file_path} - NOT FOUND ###\n\n")
                md_file.write(f"## {file_path}\n\n")
                md_file.write("*File not found in repository*\n\n")
                print(f"⚠️ Not found: {file_path}")
        
        # Additionally, add directory structure to markdown file
        md_file.write("## Directory Structure\n\n")
        md_file.write("```\n")
        
        # Use os.walk to get a simplified directory structure
        for root, dirs, files in os.walk(repo_path, topdown=True):
            # Skip node_modules and .git directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '.next']]
            
            level = root.replace(str(repo_path), '').count(os.sep)
            indent = ' ' * 4 * level
            relative_path = os.path.basename(root)
            md_file.write(f"{indent}{relative_path}/\n")
        
        md_file.write("```\n")
    
    print(f"\nDone! Created {output_file} and {markdown_file}")

if __name__ == "__main__":
    # Get the repository path from user input
    repo_path = input("Enter the path to the Monad Mini-App Template repository: ")
    extract_files(repo_path)
