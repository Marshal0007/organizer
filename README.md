# Organizer

A command-line tool to organize and manage project resources.

## Description

`Organizer` is a Python-based tool that helps you manage and quickly access your project resources, such as URLs, documentation links, and notes. It provides a persistent shell environment with a user-friendly interface, inspired by tools like `wifite`.

## Features

*   **Organized Resources:** Store and categorize your resources with names, URLs, descriptions, and categories.
*   **Fast Access:** Quickly open resources in your web browser using the `open` command.
*   **Keyword Search:** Search for resources by keywords in their descriptions.
*   **Persistent Shell:** Enter commands in a dedicated `organizer>` prompt.
*   **Easy Installation:** Install the tool using `pip`.
*   **Colored Output:** Enjoy a visually appealing interface with colored text.

## Installation

1.  **Clone the repository:**

    ```
    git clone https://github.com/your_username/organizer.git  # Replace with your repository URL
    cd organizer
    ```

2.  **(Highly Recommended) Create a virtual environment:**

    ```
    python3 -m venv .venv         # Create a virtual environment
    source .venv/bin/activate    # Activate on Linux/macOS
    .venv\Scripts\activate     # Activate on Windows
    ```

    *Using a virtual environment is highly recommended to avoid conflicts with other Python packages on your system.*

3.  **Install the tool:**

    ```
    pip install .
    ```

    This command will install `organizer` and all its dependencies.

## Usage

1.  **Run the tool:**

    ```
    organizer
    ```

    This will display the `ORGANIZER` banner and the `organizer>` prompt.

2.  **Enter commands at the prompt:**

    Here's a list of available commands:

    *   `add <name> <url> <description> <category>`: Add a new resource.  The URL is optional.

        *   Example: `add "Python Docs" "https://docs.python.org" "Official Python documentation" "Python"`
        *   Example: `add "My Note" "This is a note about the project" "Notes"`

    *   `list [--category <category>]`: List resources, optionally filtered by category.

        *   Example: `list` (lists all resources)
        *   Example: `list --category "Python"` (lists resources in the "Python" category)

    *   `open <name>`: Open a resource in your web browser.

        *   Example: `open "Python Docs"`

    *   `search <keyword>`: Search for resources by keyword in their descriptions.

        *   Example: `search "API"`

    *   `update <name> [--url <new_url>] [--description <new_description>] [--category <new_category>]`: Update an existing resource

        *   Example: `update "Python Docs" --url "https://new.url"`
        *   Example: `update "Python Docs" --description "New Description"`

    *   `delete <name>`: Delete an existing resource.

        *   Example: `delete "My Note"`

    *   `help`: Display the usage instructions again.

    *   `exit`: Exit the `organizer>` prompt.

3.  **Example Session:**

    ```
    organizer
    ```

    ```
    (Displays the ORGANIZER banner and usage instructions)

    organizer> add "My Blog" "https://example.com/blog" "My personal blog" "Personal"
    Resource 'My Blog' added successfully.

    organizer> list --category "Personal"

    Resources:
      - My Blog (Personal)
        URL: https://example.com/blog
        Description: My personal blog

    organizer> open "My Blog"
    Opening 'My Blog' in your browser.

    organizer> exit
    ```

## Configuration

The `organizer` tool stores its data in a JSON file located at `~/.resource_db.json` by default. You can change this location using the `--dbpath` option when running the tool or in the persistent shell:

