# Repository to LLM Text Converter

## Overview

This tool extracts content from a repository and generates two output files for LLM analysis and reference:
1. A raw text file (`llm.txt`) containing the concatenated content of all target files
2. A formatted markdown file (`repo_structure.md`) with syntax highlighting and directory structure

While the tool now supports multiple project types through auto-detection, only the Monad Mini-App Template extraction has been thoroughly tested. Support for other project types (Next.js, React, Python, etc.) is still in development.

## Features

- Extracts content from predefined key files in the repository
- Generates both raw text and nicely formatted markdown output
- Automatically applies appropriate syntax highlighting based on file extensions
- Includes a visual representation of the repository's directory structure
- Handles missing files gracefully with appropriate notifications
- Skips irrelevant directories (node_modules, .git, .next)

## Usage

### Running the Script

```bash
python repo_llm.py
```

When prompted, enter the path to the Monad Mini-App Template repository:

```
Enter the path to the Monad Mini-App Template repository: /path/to/repo
```

### Output Files

The script generates two files:
- `llm.txt`: Raw text file with concatenated content from all target files
- `repo_structure.md`: Formatted markdown file with syntax highlighting and directory structure

## Target Files

The script extracts the following key files from the repository:

```python
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
```

## Customization

To modify the target files, edit the `target_files` list in the script. You can add or remove file paths as needed.

## Requirements

- Python 3.6+
- markdown package (`pip install markdown`)

## Considerations for Developers

While the template extraction provides a comprehensive foundation for building Monad mini-apps, developers should be aware of the following areas that may need enhancement for production applications:

### 1. API Integration and Blockchain Interaction

The template includes basic wallet connectivity and transaction examples, but developers will need to implement:

- More sophisticated blockchain interactions specific to their use case
- Integration with Monad-specific APIs and services
- Custom API endpoints for backend services

### 2. State Management Patterns

The template uses React Context via `use-miniapp-context.ts` for basic state management. For more complex applications, consider:

- Implementing a more robust state management solution (Redux, Zustand, Jotai)
- Adding client-side caching strategies for blockchain data
- Creating more granular context providers for specific feature domains

### 3. Error Handling and Resilience

The template includes basic error states but lacks comprehensive error handling:

- Add global error boundaries to prevent app crashes
- Implement detailed error logging and reporting
- Create graceful fallback UIs for different error scenarios
- Add retry mechanisms for blockchain transactions

### 4. Performance Optimization

For production applications, consider implementing:

- Memoization of expensive computations
- Lazy loading of components and routes
- Optimized rendering for lists and frequently updated components

These enhancements can be added incrementally as your application grows in complexity.

## License

[Specify the license here]

## Contributing

[Add contribution guidelines here]
