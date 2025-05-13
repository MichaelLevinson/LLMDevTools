import os
import markdown
from pathlib import Path

# List of files we're interested in
target_files = [
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
        
        # Add target_files list to both files
        txt_file.write("### KEY FILES IN TEMPLATE STRUCTURE ###\n\n")
        target_files_str = "\n".join([f"- {file}" for file in target_files])
        txt_file.write(f"{target_files_str}\n\n")
        
        md_file.write("## Key Files in Template Structure\n\n")
        md_file.write("```\n")
        md_file.write(target_files_str)
        md_file.write("\n```\n\n")
        
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
        
        # Add application architecture explanation
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
